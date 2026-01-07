import { Shell, globalDisclaimer } from '../../components/Shell'

export default function TermsPage() {
  return (
    <Shell>
      <section className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-bold text-slate-900">الشروط والأحكام</h1>
        <p className="text-sm text-slate-700">
          TeleDerma خدمة إرشادية للعناية بالبشرة والجمال. لا تقدم تشخيصا طبيا أو علاجا أو توصيات
          دوائية. النتائج تقدير أولي وقد لا تناسب جميع الحالات.
        </p>
        <ul className="list-disc space-y-2 pr-5 text-sm text-slate-700">
          <li>يجب أن يكون عمرك 18 عاما أو أكثر لاستخدام الخدمة.</li>
          <li>تتحمل مسؤولية اختيار المنتجات المناسبة لبشرتك.</li>
          <li>في حال وجود ألم أو أعراض مقلقة، يرجى مراجعة مختص مرخص.</li>
        </ul>
        <p className="text-xs text-slate-500">{globalDisclaimer}</p>
      </section>
    </Shell>
  )
}
