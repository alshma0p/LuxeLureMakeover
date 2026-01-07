import Link from 'next/link'

const disclaimer =
  'تنبيه. TeleDerma خدمة إرشادية للعناية بالبشرة والجمال فقط. غير طبية. لا تقدم تشخيصا أو علاجا. النتائج تقدير أولي وقد تخطئ. إذا كان لديك ألم أو التهاب شديد أو أعراض مقلقة فراجع مختصا مرخصا.'

export function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/" className="text-xl font-bold text-brand-700">
            TeleDerma
          </Link>
          <nav className="flex items-center gap-4 text-sm">
            <Link href="/try">جرّب الآن</Link>
            <Link href="/privacy">الخصوصية</Link>
            <Link href="/terms">الشروط</Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-10">{children}</main>
      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-6 text-sm text-slate-600">
          <p>{disclaimer}</p>
        </div>
      </footer>
    </div>
  )
}

export const globalDisclaimer = disclaimer
