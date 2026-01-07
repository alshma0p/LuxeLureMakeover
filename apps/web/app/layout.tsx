import type { Metadata } from 'next'
import { Tajawal } from 'next/font/google'
import './globals.css'

const tajawal = Tajawal({
  subsets: ['arabic'],
  weight: ['400', '500', '700']
})

export const metadata: Metadata = {
  title: 'TeleDerma',
  description: 'منصة إرشادية للعناية بالبشرة والجمال'
}

export default function RootLayout({
  children
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ar" dir="rtl">
      <body className={tajawal.className}>{children}</body>
    </html>
  )
}
