# TeleDerma MVP

منصة إرشادية للعناية بالبشرة والجمال فقط. غير طبية.

## المتطلبات الرئيسية
- عدم تخزين الصور أو مدخلات المستخدم بشكل افتراضي.
- تشغيل استدلال ذكاء اصطناعي حقيقي على الخادم.
- واجهة عربية RTL مع تحذير واضح.

## النموذج المستخدم
- Model: dima806/skin_types_image_detection
- License: Apache-2.0
- الهدف: تصنيف نوع البشرة إلى دهنية أو عادية أو جافة فقط.

## البنية المعمارية
```
[Next.js Web] -> HTTPS -> [FastAPI API] -> [Postgres]
                           |-> [HF Image Model on CPU]
```

## بيئة التشغيل
| المتغير | الوصف | مثال |
| --- | --- | --- |
| TELEDERMA_DATABASE_URL | اتصال قاعدة البيانات | postgresql+psycopg2://telederma:telederma@localhost:5432/telederma |
| TELEDERMA_FRONTEND_URL | رابط الواجهة | http://localhost:3000 |
| TELEDERMA_PAYMENT_PROVIDER | stripe أو moyasar أو hyperpay أو none | none |
| TELEDERMA_PAYMENT_KEYS | مفاتيح الدفع | <keys> |
| TELEDERMA_REDIS_URL | تمكين Redis للحد من المعدل | redis://localhost:6379/0 |
| NEXT_PUBLIC_API_BASE | رابط API للواجهة | http://localhost:8000 |

## تشغيل محلي
```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env

docker-compose up --build
```

## خطوات النشر
### Backend على Fly.io
1. ثبّت flyctl وسجّل الدخول.
2. أنشئ تطبيق جديد:
   ```bash
   flyctl apps create telederma-api
   ```
3. اضبط الأسرار:
   ```bash
   flyctl secrets set TELEDERMA_DATABASE_URL=... TELEDERMA_FRONTEND_URL=... TELEDERMA_PAYMENT_PROVIDER=none
   ```
4. انشر:
   ```bash
   flyctl deploy -c infra/fly.toml
   ```

### Frontend على Vercel
1. اربط مشروع Next.js.
2. اضبط المتغيرات البيئية:
   - NEXT_PUBLIC_API_BASE=https://<api-domain>
3. انشر.

## الخصوصية والأمان
- الصور تعالج في الذاكرة فقط ولا تحفظ.
- السجلات تقتصر على بيانات تقنية محدودة.
- الحد الأقصى للرفع 5MB مع التحقق من النوع والمحتوى.

## القيود المعروفة
- دقة النموذج تتأثر بالإضاءة وزاوية التصوير.
- التقدير أولي ولا يغني عن مختص مرخص.

## الوثائق
- Swagger: `/docs` من عنوان API.
- OpenAPI: `/openapi.json`.

## المجلدات
- `apps/web`: تطبيق Next.js
- `apps/api`: تطبيق FastAPI
- `infra`: ملفات النشر
