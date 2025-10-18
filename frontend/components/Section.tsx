import SectionHeader from './SectionHeader'
import { soft, layout } from '@/lib/theme'

export default function Section({
  title,
  subtitle,
  children,
}: {
  title: string
  subtitle?: string
  children: React.ReactNode
}) {
  return (
    <section
      style={{
        background: soft.card,
        border: `1px solid ${soft.border}`,
        borderRadius: layout.radius,
        padding: layout.cardPadding,
        boxShadow: soft.shadow,
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
      }}
    >
      <SectionHeader title={title} />
      {subtitle && <p style={{ color: soft.sub, marginTop: -4 }}>{subtitle}</p>}
      {children}
    </section>
  )
}
