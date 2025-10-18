import './globals.css'

export const metadata = {
  title: 'NutriBalance',
  description: 'Track your daily food groups and build a balanced diet',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-[#F1FBF6] text-[#0B3B29] font-sans min-h-screen flex justify-center px-4 py-12">
        <main className="w-full max-w-[1350px] flex flex-col gap-10">
          {children}
        </main>
      </body>
    </html>
  )
}
