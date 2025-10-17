'use client'

export default function ProgressBar({ percent }: { percent: number }) {
  return (
    <div className="flex flex-col gap-1">
      <div className="h-3 w-full bg-[#E7F6EE] rounded-full overflow-hidden">
        <div
          className="h-full bg-[#2BAA66] transition-all duration-300"
          style={{ width: `${percent}%` }}
        />
      </div>
      <span className="text-xs text-[#5E7F73] text-right">{percent}% complete</span>
    </div>
  )
}
