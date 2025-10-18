'use client'

import { soft } from '@/lib/theme'
import {
  Apple,
  LeafyGreen,
  Wheat,
  Drumstick,
  Milk,
  Droplet,
} from 'lucide-react'

const iconMap: Record<string, any> = {
  Fruits: Apple,
  Vegetables: LeafyGreen,
  Grains: Wheat,
  Protein: Drumstick,
  Dairy: Milk,
  'Healthy Fats': Droplet,
}

interface GroupPillProps {
  name: string
  done: boolean
  onToggle: () => void
}

export default function GroupPill({ name, done, onToggle }: GroupPillProps) {
  const Icon = iconMap[name] || Apple
  return (
    <button
      onClick={onToggle}
      className={`flex items-center gap-3 p-4 rounded-xl border transition-all ${
        done ? 'border-green-400 bg-[#F0FBF6]' : 'border-[#D9F1E3] bg-white'
      }`}
    >
      <Icon
        size={22}
        className={done ? 'text-green-600' : 'text-gray-400'}
        strokeWidth={2.2}
      />
      <div className="flex flex-col text-left">
        <span className="font-semibold text-[#0B3B29]">{name}</span>
        <span className="text-sm text-[#5E7F73]">
          {done ? 'Completed' : 'Missing'}
        </span>
      </div>
    </button>
  )
}
