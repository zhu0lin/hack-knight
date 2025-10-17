'use client'

import { soft } from '@/lib/theme'

interface Props {
  checked: boolean
  label: string
  onChange: () => void
}

export default function RadioRow({ checked, label, onChange }: Props) {
  return (
    <label
      className={`flex items-center gap-3 cursor-pointer rounded-xl border px-4 py-3 transition-all ${
        checked ? 'border-green-400 bg-[#F4FBF7]' : 'border-[#D9F1E3]'
      }`}
    >
      <input
        type="radio"
        checked={checked}
        onChange={onChange}
        className="w-4 h-4 accent-green-600 cursor-pointer"
      />
      <span className="text-[#0B3B29] text-sm sm:text-base">{label}</span>
    </label>
  )
}
