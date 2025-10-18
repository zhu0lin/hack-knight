'use client'

export default function CardSub({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-[#D9F1E3] bg-[#EEF9F3] p-4">
      {children}
    </div>
  )
}
