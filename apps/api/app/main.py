import uuid
import time
from datetime import datetime, timedelta
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Request, Response, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from app.core.config import settings
from app.db.session import SessionLocal, engine
from app.db.models import Base, User, Scan, WalletLedger, MinimalLog
from app.schemas.common import HealthResponse, disclaimer_ar
from app.schemas.scan import PreviewResponse, FullRequest, FullResponse
from app.schemas.wallet import WalletBalanceResponse, WalletTopupRequest, WalletTopupResponse, WalletChargeRequest, WalletChargeResponse
from app.schemas.referral import ReferralCreateResponse, ReferralCompleteResponse
from app.schemas.account import AccountDeleteResponse
from app.services.inference import get_inference_service, warmup
from app.services.reports import map_label, derive_attributes, preview_template, full_report_template
from app.services.payments import get_payment_adapter
from app.utils.images import validate_image
from app.utils.rate_limit import rate_limiter

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TeleDerma API", version=settings.version)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else exc.detail
    return JSONResponse(status_code=exc.status_code, content={"detail": detail, "disclaimer_ar": disclaimer_ar})

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = int((time.time() - start) * 1000)
        user_id = request.state.user_id if hasattr(request.state, "user_id") else None
        log = MinimalLog(
            id=str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
            route=request.url.path,
            method=request.method,
            status_code=response.status_code,
            latency_ms=duration,
            user_id=user_id,
            error_code=None
        )
        db = SessionLocal()
        db.add(log)
        db.commit()
        db.close()
        return response


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session_id = request.cookies.get(settings.session_cookie_name)
        csrf_token = request.cookies.get("telederma_csrf")
        new_session = None
        new_csrf = None
        if session_id and request.method in {"POST", "PUT", "DELETE"}:
            header_token = request.headers.get("X-CSRF-Token")
            if not header_token or header_token != csrf_token:
                return JSONResponse(status_code=403, content={"detail": "csrf_invalid", "disclaimer_ar": disclaimer_ar})
        if not session_id:
            new_session = str(uuid.uuid4())
            new_csrf = str(uuid.uuid4())
            request.state.user_id = new_session
        else:
            request.state.user_id = session_id
        response = await call_next(request)
        is_secure = settings.environment == "production"
        if new_session:
            response.set_cookie(
                settings.session_cookie_name,
                new_session,
                httponly=True,
                samesite="lax",
                secure=is_secure,
                max_age=settings.session_expiry_days * 24 * 3600
            )
            response.set_cookie(
                "telederma_csrf",
                new_csrf,
                httponly=False,
                samesite="lax",
                secure=is_secure,
                max_age=settings.session_expiry_days * 24 * 3600
            )
        return response


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(SessionMiddleware)
app.add_middleware(LoggingMiddleware)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_create_user(db: Session, user_id: str | None) -> User:
    if not user_id:
        user_id = str(uuid.uuid4())
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return user
    referral_code = user_id.split("-")[0]
    new_user = User(id=user_id, referral_code=referral_code)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.on_event("startup")
async def startup_event() -> None:
    warmup()


@app.get(f"{settings.api_v1_prefix}/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    service = get_inference_service()
    return HealthResponse(
        status="ok",
        model_loaded=True,
        model_name=service.model_name,
        model_license=settings.model_license,
        version=settings.version,
        disclaimer_ar=disclaimer_ar
    )


@app.post(f"{settings.api_v1_prefix}/scan/preview", response_model=PreviewResponse)
async def scan_preview(
    request: Request,
    response: Response,
    image: UploadFile = File(...),
    locale: str = Form("ar-SA"),
    ref_code: str | None = Form(default=None),
    db: Session = Depends(get_db)
) -> PreviewResponse:
    if not rate_limiter.allow(request.client.host):
        raise HTTPException(status_code=429, detail="rate_limited")
    content = await image.read()
    try:
        img = validate_image(image.content_type or "", content)
    except ValueError as exc:
        detail = str(exc)
        raise HTTPException(status_code=400, detail=detail)
    start = time.time()
    service = get_inference_service()
    label, confidence = service.predict(img)
    skin_type = map_label(label)
    scan_id = str(uuid.uuid4())
    user = get_or_create_user(db, request.state.user_id)
    if ref_code and ref_code != user.referral_code and user.invited_by is None:
        referrer = db.query(User).filter(User.referral_code == ref_code).first()
        if referrer:
            user.invited_by = referrer.id
            referrer.referral_completed += 1
            db.add(referrer)
            db.add(user)
            db.commit()
    scan = Scan(
        id=scan_id,
        user_id=user.id,
        predicted_label=skin_type,
        confidence=confidence,
        attributes="",
        unlocked=False,
        unlocked_via="none",
        model_name=service.model_name,
        model_version_hash=service.model_revision
    )
    db.add(scan)
    db.commit()
    latency_ms = int((time.time() - start) * 1000)
    preview = preview_template(skin_type)
    return PreviewResponse(
        scan_id=scan_id,
        skin_type_ar=skin_type,
        confidence=confidence,
        confidence_pct=int(confidence * 100),
        attributes_ar=[],
        preview_ar=preview,
        locked=True,
        unlock_options={
            "invite_required": 2,
            "invite_completed": user.referral_completed,
            "pay_amount_sar": 1
        },
        disclaimer_ar=disclaimer_ar,
        latency_ms=latency_ms
    )


@app.post(f"{settings.api_v1_prefix}/scan/full", response_model=FullResponse)
async def scan_full(
    request: Request,
    payload: FullRequest,
    db: Session = Depends(get_db)
) -> FullResponse:
    if not rate_limiter.allow(request.client.host):
        raise HTTPException(status_code=429, detail="rate_limited")
    start = time.time()
    user = get_or_create_user(db, request.state.user_id)
    scan = db.query(Scan).filter(Scan.id == payload.scan_id, Scan.user_id == user.id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="scan_not_found")
    unlocked_count = db.query(Scan).filter(Scan.user_id == user.id, Scan.unlocked.is_(True)).count()
    attributes = derive_attributes(scan.confidence, payload.answers.tzone_shiny, payload.answers.irritates_easily, scan.predicted_label)
    unlocked_via = scan.unlocked_via if scan.unlocked else "none"
    if not scan.unlocked:
        if payload.unlock_via == "referral" and user.referral_completed >= 2 and unlocked_count == 0:
            scan.unlocked = True
            scan.unlocked_via = "referral"
            unlocked_via = "referral"
        elif payload.unlock_via == "paid":
            amount = 1 if unlocked_count == 0 else 2
            if user.wallet_balance >= amount:
                user.wallet_balance -= amount
                ledger = WalletLedger(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    amount=-amount,
                    type="unlock_first_full" if unlocked_count == 0 else "scan",
                    description="Unlock full report"
                )
                db.add(ledger)
                scan.unlocked = True
                scan.unlocked_via = "paid"
                unlocked_via = "paid"
            else:
                raise HTTPException(status_code=400, detail="insufficient_balance")
    scan.attributes = ",".join(attributes)
    db.add(scan)
    db.commit()
    report = full_report_template(scan.predicted_label, attributes)
    latency_ms = int((time.time() - start) * 1000)
    return FullResponse(
        scan_id=scan.id,
        skin_type_ar=scan.predicted_label,
        confidence=scan.confidence,
        confidence_pct=int(scan.confidence * 100),
        attributes_ar=attributes,
        full_report_ar=report,
        unlocked_via=unlocked_via,
        disclaimer_ar=disclaimer_ar,
        latency_ms=latency_ms
    )


@app.post(f"{settings.api_v1_prefix}/referral/create", response_model=ReferralCreateResponse)
async def referral_create(request: Request, db: Session = Depends(get_db)) -> ReferralCreateResponse:
    user = get_or_create_user(db, request.state.user_id)
    ref_link = f"{settings.frontend_url}/try?ref={user.referral_code}"
    return ReferralCreateResponse(
        ref_code=user.referral_code,
        ref_link=ref_link,
        invite_required=2,
        invite_completed=user.referral_completed,
        disclaimer_ar=disclaimer_ar
    )


@app.post(f"{settings.api_v1_prefix}/referral/complete", response_model=ReferralCompleteResponse)
async def referral_complete(ref_code: str, db: Session = Depends(get_db)) -> ReferralCompleteResponse:
    user = db.query(User).filter(User.referral_code == ref_code).first()
    if not user:
        raise HTTPException(status_code=404, detail="referral_not_found")
    user.referral_completed += 1
    db.add(user)
    db.commit()
    return ReferralCompleteResponse(
        ref_code=user.referral_code,
        invite_required=2,
        invite_completed=user.referral_completed,
        unlocked=user.referral_completed >= 2,
        disclaimer_ar=disclaimer_ar
    )


@app.post(f"{settings.api_v1_prefix}/wallet/balance", response_model=WalletBalanceResponse)
async def wallet_balance(request: Request, db: Session = Depends(get_db)) -> WalletBalanceResponse:
    user = get_or_create_user(db, request.state.user_id)
    return WalletBalanceResponse(balance_sar=user.wallet_balance, disclaimer_ar=disclaimer_ar)


@app.post(f"{settings.api_v1_prefix}/wallet/topup/create", response_model=WalletTopupResponse)
async def wallet_topup(payload: WalletTopupRequest) -> WalletTopupResponse:
    adapter = get_payment_adapter()
    if settings.payment_provider == "none":
        return WalletTopupResponse(provider=adapter.provider, status="not_configured", next_step="غير متاح حاليا", disclaimer_ar=disclaimer_ar)
    return WalletTopupResponse(provider=adapter.provider, status="configured", next_step=adapter.create_topup(payload.amount_sar), disclaimer_ar=disclaimer_ar)


@app.post(f"{settings.api_v1_prefix}/wallet/charge", response_model=WalletChargeResponse)
async def wallet_charge(request: Request, payload: WalletChargeRequest, db: Session = Depends(get_db)) -> WalletChargeResponse:
    user = get_or_create_user(db, request.state.user_id)
    if user.wallet_balance < payload.amount_sar:
        return WalletChargeResponse(charged=False, balance_sar=user.wallet_balance, reason="insufficient_balance", disclaimer_ar=disclaimer_ar)
    user.wallet_balance -= payload.amount_sar
    ledger = WalletLedger(
        id=str(uuid.uuid4()),
        user_id=user.id,
        amount=-payload.amount_sar,
        type=payload.type,
        description="Wallet charge"
    )
    db.add(ledger)
    db.add(user)
    db.commit()
    return WalletChargeResponse(charged=True, balance_sar=user.wallet_balance, disclaimer_ar=disclaimer_ar)


@app.get(f"{settings.api_v1_prefix}/report/pdf")
async def report_pdf(request: Request, db: Session = Depends(get_db)):
    user = get_or_create_user(db, request.state.user_id)
    since = datetime.utcnow() - timedelta(days=30)
    scans = (
        db.query(Scan)
        .filter(Scan.user_id == user.id, Scan.unlocked.is_(True), Scan.created_at >= since)
        .all()
    )
    if len(scans) < 10:
        return JSONResponse(status_code=400, content={"detail": "غير مؤهل بعد للتقرير الزمني", "disclaimer_ar": disclaimer_ar})
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, "TeleDerma تقرير زمني غير طبي")
    pdf.multi_cell(0, 10, disclaimer_ar)
    for scan in scans:
        pdf.multi_cell(0, 10, f"{scan.created_at.date()} - {scan.predicted_label} - {int(scan.confidence * 100)}%")
    data = pdf.output(dest="S").encode("latin1")
    return StreamingResponse(iter([data]), media_type="application/pdf")


@app.post(f"{settings.api_v1_prefix}/account/delete", response_model=AccountDeleteResponse)
async def account_delete(request: Request, db: Session = Depends(get_db)) -> AccountDeleteResponse:
    user = get_or_create_user(db, request.state.user_id)
    db.query(Scan).filter(Scan.user_id == user.id).delete()
    db.query(WalletLedger).filter(WalletLedger.user_id == user.id).delete()
    db.query(User).filter(User.id == user.id).delete()
    db.commit()
    return AccountDeleteResponse(deleted=True, disclaimer_ar=disclaimer_ar)
