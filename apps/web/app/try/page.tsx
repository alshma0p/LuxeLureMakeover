'use client'

import { useMemo, useState } from 'react'
import { Shell, globalDisclaimer } from '../../components/Shell'

type PreviewResponse = {
  scan_id: string
  skin_type_ar: string
  confidence: number
  confidence_pct: number
  attributes_ar: string[]
  preview_ar: {
    summary: string[]
    top_tips: string[]
  }
  locked: boolean
  unlock_options: {
    invite_required: number
    invite_completed: number
    pay_amount_sar: number
  }
  disclaimer_ar: string
  latency_ms: number
}

type FullResponse = {
  scan_id: string
  skin_type_ar: string
  confidence: number
  confidence_pct: number
  attributes_ar: string[]
  full_report_ar: {
    what_it_means: string[]
    fits_you: string[]
    avoid: string[]
    simple_routine_am: string[]
    simple_routine_pm: string[]
    see_specialist_if: string[]
  }
  unlocked_via: 'paid' | 'referral' | 'none'
  disclaimer_ar: string
  latency_ms: number
}

type HistoryItem = {
  scanId: string
  skinType: string
  confidencePct: number
  unlocked: boolean
}

const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

const getCsrfToken = () => {
  if (typeof document === 'undefined') return ''
  const match = document.cookie.match(/telederma_csrf=([^;]+)/)
  return match ? decodeURIComponent(match[1]) : ''
}

export default function TryPage() {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<PreviewResponse | null>(null)
  const [full, setFull] = useState<FullResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [tzoneShiny, setTzoneShiny] = useState(false)
  const [irritatesEasily, setIrritatesEasily] = useState(false)
  const [walletBalance, setWalletBalance] = useState<number | null>(null)
  const [referral, setReferral] = useState<{ ref_code: string; ref_link: string; invite_required: number; invite_completed: number } | null>(null)
  const [topupStatus, setTopupStatus] = useState('')

  const canExportPdf = useMemo(() => history.filter((item) => item.unlocked).length >= 10, [history])
  const unlockedCount = useMemo(() => history.filter((item) => item.unlocked).length, [history])
  const referralCode = useMemo(() => {
    if (typeof window === 'undefined') return ''
    const params = new URLSearchParams(window.location.search)
    return params.get('ref') || ''
  }, [])

  const resetState = () => {
    setPreview(null)
    setFull(null)
    setError('')
  }

  const translateError = (message: string) => {
    if (message.includes('invalid_type')) return 'نوع الملف غير مدعوم. يرجى رفع صورة JPEG أو PNG.'
    if (message.includes('too_large')) return 'حجم الصورة كبير جدا. الحد الأقصى 5MB.'
    if (message.includes('invalid_image')) return 'تعذر قراءة الصورة. حاول رفع صورة أوضح.'
    if (message.includes('insufficient_balance')) return 'الرصيد غير كاف. يرجى شحن المحفظة.'
    if (message.includes('rate_limited')) return 'عدد الطلبات مرتفع. حاول لاحقا.'
    if (message.includes('scan_not_found')) return 'لم يتم العثور على الفحص.'
    return message
  }

  const handlePreview = async () => {
    if (!file) {
      setError('يرجى اختيار صورة أولا.')
      return
    }
    resetState()
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('image', file)
      formData.append('locale', 'ar-SA')
      if (referralCode) {
        formData.append('ref_code', referralCode)
      }
      const response = await fetch(`${apiBase}/api/v1/scan/preview`, {
        method: 'POST',
        body: formData,
        headers: { 'X-CSRF-Token': getCsrfToken() },
        credentials: 'include'
      })
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data?.detail || 'حدث خطأ أثناء المعالجة.')
      }
      const data: PreviewResponse = await response.json()
      setPreview(data)
      setHistory((prev) => [{ scanId: data.scan_id, skinType: data.skin_type_ar, confidencePct: data.confidence_pct, unlocked: false }, ...prev].slice(0, 5))
    } catch (err) {
      const message = err instanceof Error ? err.message : 'تعذر الاتصال بالخادم.'
      setError(translateError(message))
    } finally {
      setLoading(false)
    }
  }

  const handleFull = async (type: 'referral' | 'paid') => {
    if (!preview) return
    setLoading(true)
    setError('')
    try {
      const response = await fetch(`${apiBase}/api/v1/scan/full`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': getCsrfToken() },
        credentials: 'include',
        body: JSON.stringify({
          scan_id: preview.scan_id,
          answers: {
            tzone_shiny: tzoneShiny,
            irritates_easily: irritatesEasily
          },
          unlock_via: type
        })
      })
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data?.detail || 'تعذر فتح التقرير الكامل.')
      }
      const data: FullResponse = await response.json()
      setFull(data)
      setHistory((prev) => prev.map((item) => (item.scanId === data.scan_id ? { ...item, unlocked: true } : item)))
    } catch (err) {
      const message = err instanceof Error ? err.message : 'تعذر الاتصال بالخادم.'
      setError(translateError(message))
    } finally {
      setLoading(false)
    }
  }

  const fetchWallet = async () => {
    try {
      const response = await fetch(`${apiBase}/api/v1/wallet/balance`, {
        method: 'POST',
        headers: { 'X-CSRF-Token': getCsrfToken() },
        credentials: 'include'
      })
      const data = await response.json()
      setWalletBalance(data.balance_sar)
    } catch {
      setWalletBalance(null)
    }
  }

  const createReferral = async () => {
    try {
      const response = await fetch(`${apiBase}/api/v1/referral/create`, {
        method: 'POST',
        headers: { 'X-CSRF-Token': getCsrfToken() },
        credentials: 'include'
      })
      const data = await response.json()
      setReferral(data)
    } catch {
      setReferral(null)
    }
  }

  const topup = async (amount: 10 | 20 | 50) => {
    setTopupStatus('')
    try {
      const response = await fetch(`${apiBase}/api/v1/wallet/topup/create`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': getCsrfToken() },
        body: JSON.stringify({ amount_sar: amount })
      })
      const data = await response.json()
      if (data.status === 'not_configured') {
        setTopupStatus('غير متاح حاليا')
      } else {
        setTopupStatus(data.next_step || 'تم إنشاء عملية الشحن')
      }
    } catch {
      setTopupStatus('تعذر إنشاء عملية الشحن')
    }
  }

  const clearHistory = () => setHistory([])

  return (
    <Shell>
      <div className="space-y-8">
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h1 className="text-2xl font-bold text-slate-900">تجربة التحليل</h1>
          <p className="mt-2 text-sm text-slate-600">{globalDisclaimer}</p>
          <div className="mt-6 grid gap-4 lg:grid-cols-[2fr,1fr]">
            <div className="space-y-4">
              <label className="block text-sm font-medium text-slate-700" htmlFor="image">
                صورة السيلفي
              </label>
              <input
                id="image"
                type="file"
                accept="image/jpeg,image/png"
                className="w-full rounded-lg border border-slate-300 p-2"
                onChange={(event) => setFile(event.target.files?.[0] || null)}
              />
              <div className="flex flex-wrap items-center gap-3">
                <button
                  className="rounded-lg bg-brand-700 px-5 py-2 text-white transition hover:bg-brand-500"
                  onClick={handlePreview}
                  disabled={loading}
                >
                  {loading ? 'جار التحليل' : 'احصل على المعاينة'}
                </button>
                <button
                  className="rounded-lg border border-slate-300 px-5 py-2 text-slate-700"
                  onClick={fetchWallet}
                >
                  تحديث رصيد المحفظة
                </button>
                <button
                  className="rounded-lg border border-slate-300 px-5 py-2 text-slate-700"
                  onClick={createReferral}
                >
                  إنشاء رابط دعوة
                </button>
              </div>
              {error && <p className="rounded-lg bg-red-50 p-3 text-sm text-red-600">{error}</p>}
            </div>
            <div className="rounded-xl bg-slate-50 p-4 text-sm text-slate-700">
              <h3 className="font-semibold text-slate-900">الأسئلة السريعة</h3>
              <div className="mt-3 space-y-2">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={tzoneShiny}
                    onChange={(event) => setTzoneShiny(event.target.checked)}
                  />
                  هل منطقة الـ T تصبح لامعة أكثر من الخدين خلال اليوم؟
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={irritatesEasily}
                    onChange={(event) => setIrritatesEasily(event.target.checked)}
                  />
                  هل تتعرض للتهيّج بسهولة من العطور أو المقشرات؟
                </label>
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-3">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm lg:col-span-2">
            <h2 className="text-lg font-semibold text-slate-900">نتيجة المعاينة</h2>
            {loading && (
              <div className="mt-4 space-y-3 animate-pulse">
                <div className="h-4 w-32 rounded bg-slate-200" />
                <div className="h-3 w-full rounded bg-slate-200" />
                <div className="h-3 w-5/6 rounded bg-slate-200" />
              </div>
            )}
            {!preview && !loading && <p className="mt-4 text-sm text-slate-500">ارفع صورة للحصول على تقرير المعاينة.</p>}
            {preview && (
              <div className="mt-4 space-y-4 text-sm text-slate-700">
                <div className="flex flex-wrap items-center gap-3">
                  <span className="rounded-full bg-brand-50 px-3 py-1 text-xs text-brand-700">تقدير أولي</span>
                  <span>نوع البشرة المتوقع: {preview.skin_type_ar}</span>
                  <span>الثقة: {preview.confidence_pct}%</span>
                </div>
                {preview.confidence < 0.5 && (
                  <p className="rounded-lg bg-amber-50 p-3 text-xs text-amber-700">
                    الثقة منخفضة. تأكدي من وضوح الصورة وإضاءة مناسبة.
                  </p>
                )}
                <div>
                  <p className="font-semibold">ملخص سريع</p>
                  <ul className="mt-2 list-disc space-y-1 pr-5">
                    {preview.preview_ar.summary.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="font-semibold">أهم النصائح</p>
                  <ul className="mt-2 list-disc space-y-1 pr-5">
                    {preview.preview_ar.top_tips.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
          <div className="space-y-4">
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <h3 className="font-semibold text-slate-900">فتح التقرير الكامل</h3>
              {preview ? (
                <div className="mt-3 space-y-3 text-sm text-slate-700">
                  <p>
                    المعاينة مجانية. التقرير الكامل لأول فحص يتطلب دعوة صديقين أو الدفع من المحفظة.
                    بعد ذلك يصبح كل تقرير كامل جديد مقابل 2 ر.س من المحفظة.
                  </p>
                  <button
                    className="w-full rounded-lg border border-slate-300 px-4 py-2"
                    onClick={() => handleFull('referral')}
                    disabled={loading}
                  >
                    فتح عبر الدعوات
                  </button>
                  <button
                    className="w-full rounded-lg bg-brand-700 px-4 py-2 text-white"
                    onClick={() => handleFull('paid')}
                    disabled={loading}
                  >
                    فتح مقابل {unlockedCount === 0 ? 1 : 2} ريال من المحفظة
                  </button>
                </div>
              ) : (
                <p className="mt-3 text-sm text-slate-500">يتطلب تقرير المعاينة أولا.</p>
              )}
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <h3 className="font-semibold text-slate-900">المحفظة</h3>
              <p className="mt-2 text-sm text-slate-700">الرصيد الحالي: {walletBalance ?? '--'} ر.س</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {[10, 20, 50].map((amount) => (
                  <button
                    key={amount}
                    className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
                    onClick={() => topup(amount as 10 | 20 | 50)}
                    disabled={topupStatus === 'غير متاح حاليا'}
                  >
                    شحن {amount} ر.س
                  </button>
                ))}
              </div>
              {topupStatus && <p className="mt-2 text-xs text-slate-500">{topupStatus}</p>}
              {topupStatus === 'غير متاح حاليا' && (
                <p className="mt-2 text-xs text-slate-500">الدفع غير متاح حاليا عبر المزود.</p>
              )}
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <h3 className="font-semibold text-slate-900">الدعوات</h3>
              {referral ? (
                <div className="mt-2 space-y-2 text-sm">
                  <p>تم إنشاء كود الدعوة: {referral.ref_code}</p>
                  <p className="break-all text-xs text-slate-500">{referral.ref_link}</p>
                </div>
              ) : (
                <p className="mt-2 text-sm text-slate-500">أنشئ رابط الدعوة وشاركه مع أصدقائك.</p>
              )}
            </div>
          </div>
        </section>

        {full && (
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">التقرير الكامل</h2>
            <p className="mt-2 text-xs text-slate-500">{full.disclaimer_ar}</p>
            <div className="mt-4 grid gap-4 lg:grid-cols-2">
              <div>
                <p className="font-semibold">ماذا يعني ذلك</p>
                <ul className="mt-2 list-disc space-y-1 pr-5 text-sm text-slate-700">
                  {full.full_report_ar.what_it_means.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="font-semibold">يناسبك</p>
                <ul className="mt-2 list-disc space-y-1 pr-5 text-sm text-slate-700">
                  {full.full_report_ar.fits_you.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="font-semibold">تجنبي</p>
                <ul className="mt-2 list-disc space-y-1 pr-5 text-sm text-slate-700">
                  {full.full_report_ar.avoid.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="font-semibold">روتين صباحي بسيط</p>
                <ul className="mt-2 list-disc space-y-1 pr-5 text-sm text-slate-700">
                  {full.full_report_ar.simple_routine_am.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="font-semibold">روتين مسائي بسيط</p>
                <ul className="mt-2 list-disc space-y-1 pr-5 text-sm text-slate-700">
                  {full.full_report_ar.simple_routine_pm.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="font-semibold">راجعي مختصا مرخصا إذا</p>
                <ul className="mt-2 list-disc space-y-1 pr-5 text-sm text-slate-700">
                  {full.full_report_ar.see_specialist_if.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </section>
        )}

        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">السجل</h2>
            <button className="text-sm text-brand-700" onClick={clearHistory}>
              مسح السجل
            </button>
          </div>
          {history.length === 0 ? (
            <p className="mt-3 text-sm text-slate-500">لا يوجد سجلات بعد.</p>
          ) : (
            <ul className="mt-3 space-y-2 text-sm text-slate-700">
              {history.map((item) => (
                <li key={item.scanId} className="flex items-center justify-between rounded-lg bg-slate-50 p-3">
                  <span>{item.skinType}</span>
                  <span>{item.confidencePct}%</span>
                  <span className="text-xs text-slate-500">{item.unlocked ? 'مفتوح' : 'مغلق'}</span>
                </li>
              ))}
            </ul>
          )}
          {canExportPdf && (
            <button
              className="mt-4 rounded-lg border border-slate-300 px-4 py-2 text-sm"
              onClick={() => window.open(`${apiBase}/api/v1/report/pdf`, '_blank')}
            >
              تنزيل تقرير زمني PDF
            </button>
          )}
        </section>
      </div>
    </Shell>
  )
}
