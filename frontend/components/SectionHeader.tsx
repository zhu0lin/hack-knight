import { soft } from '@/lib/theme'

export default function SectionHeader({ title }: { title: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
      <span
        style={{
          width: 8,
          height: 28,
          borderRadius: 4,
          background: soft.green,
          display: 'inline-block',
        }}
      />
      <h2 style={{ margin: 0, color: soft.text }}>{title}</h2>
    </div>
  )
}
