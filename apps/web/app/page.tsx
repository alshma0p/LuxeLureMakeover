import Link from 'next/link'
import { Shell, globalDisclaimer } from '../components/Shell'

export default function HomePage() {
  return (
    <Shell>
      <section className="grid gap-8 lg:grid-cols-2">
        <div className="space-y-6">
          <div className="inline-flex items-center rounded-full bg-brand-50 px-4 py-2 text-sm text-brand-700">
            عناية ذكية بالبشرة والجمال
          </div>
          <h1 className="text-4xl font-bold leading-tight text-slate-900">
            تقرير فوري يوضح نمط بشرتك ويقترح روتينا بسيطا للعناية اليومية
          </h1>
          <p className="text-lg text-slate-700">
            TeleDerma يقدم تقديرا أوليا لنمط البشرة مع نصائح عامة فقط. الخدمة غير طبية وموجهة
            للعناية والجمال.
          </p>
          <div className="flex flex-wrap gap-4">
            <Link
              href="/try"
              className="rounded-lg bg-brand-700 px-6 py-3 text-white transition hover:bg-brand-500"
            >
              ابدأ التجربة المجانية
            </Link>
            <Link
              href="/privacy"
              className="rounded-lg border border-slate-300 px-6 py-3 text-slate-700"
            >
              سياسة الخصوصية
            </Link>
          </div>
        </div>
        <div className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-900">ما الذي ستحصل عليه</h2>
          <ul className="space-y-3 text-slate-700">
            <li>تقدير أولي لنوع البشرة مع نسبة ثقة واضحة.</li>
            <li>نصائح عامة للعناية اليومية دون أي تشخيص طبي.</li>
            <li>إمكانية فتح التقرير الكامل عبر الدعوات أو المحفظة.</li>
          </ul>
          <p className="text-xs text-slate-500">{globalDisclaimer}</p>
        </div>
      </section>
    </Shell>
  )
}
