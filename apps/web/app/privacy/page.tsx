import { Shell, globalDisclaimer } from '../../components/Shell'

export default function PrivacyPage() {
  return (
    <Shell>
      <section className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-bold text-slate-900">سياسة الخصوصية</h1>
        <p className="text-sm text-slate-700">
          نحترم خصوصيتك. TeleDerma لا يخزن صورك أو مدخلاتك النصية بشكل افتراضي. تتم معالجة الصور
          في الذاكرة فقط ثم يتم حذفها. نسجل بيانات تقنية محدودة فقط مثل رقم الطلب والزمن ونوع
          الخطأ لأغراض التشغيل.
        </p>
        <ul className="list-disc space-y-2 pr-5 text-sm text-slate-700">
          <li>تقليل البيانات والاحتفاظ الأدنى بشكل افتراضي.</li>
          <li>لا نستخدم أي أدوات تتبع أو تحليلات تسويقية.</li>
          <li>يمكنك طلب حذف بيانات الحساب الوصفية في أي وقت.</li>
        </ul>
        <p className="text-xs text-slate-500">{globalDisclaimer}</p>
      </section>
    </Shell>
  )
}
