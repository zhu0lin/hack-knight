'use client'

export function PrimaryButton({
  children,
  onClick,
}: {
  children: React.ReactNode
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className="bg-[#2BAA66] text-white px-5 py-2.5 rounded-lg font-semibold flex items-center justify-center gap-2"
    >
      {children}
    </button>
  )
}

export function GhostButton({
  children,
  onClick,
}: {
  children: React.ReactNode
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className="border-2 border-[#2BAA66] text-[#2BAA66] px-5 py-2.5 rounded-lg font-semibold flex items-center justify-center gap-2"
    >
      {children}
    </button>
  )
}
