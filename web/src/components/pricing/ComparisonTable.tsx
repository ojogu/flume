import { Fragment } from 'react'
import { Check, Minus } from 'lucide-react'

// [PLACEHOLDER] — update feature list and tier limits before launch
type CellValue = boolean | string

interface FeatureRow {
  label: string
  free: CellValue
  pro: CellValue
  enterprise: CellValue
}

interface FeatureGroup {
  category: string
  rows: FeatureRow[]
}

const featureGroups: FeatureGroup[] = [
  {
    category: 'Usage',
    rows: [
      { label: 'Jobs / month', free: '100', pro: '5,000', enterprise: 'Unlimited' },
      { label: 'Storage', free: '500 MB', pro: '50 GB', enterprise: 'Custom' },
    ],
  },
  {
    category: 'Features',
    rows: [
      { label: 'API access', free: true, pro: true, enterprise: true },
      { label: 'Webhook callbacks', free: false, pro: true, enterprise: true },
      { label: 'Dashboard access', free: true, pro: true, enterprise: true },
    ],
  },
  {
    category: 'Support',
    rows: [
      { label: 'Community support', free: true, pro: false, enterprise: false },
      { label: 'Email support', free: false, pro: true, enterprise: true },
      { label: 'Dedicated support', free: false, pro: false, enterprise: true },
      { label: 'SLA guarantee', free: false, pro: false, enterprise: true },
    ],
  },
  {
    category: 'Billing',
    rows: [
      { label: 'Annual billing discount', free: false, pro: true, enterprise: true },
      { label: 'Custom quotas', free: false, pro: false, enterprise: true },
    ],
  },
]

const tierPrices = {
  monthly: { free: '$0', pro: '$29 / mo', enterprise: 'Custom' },
  annual: { free: '$0', pro: '$23 / mo', enterprise: 'Custom' },
}

const tierLabels = ['Free', 'Pro', 'Enterprise'] as const
const tierKeys = ['free', 'pro', 'enterprise'] as const

function Cell({ value }: { value: CellValue }) {
  if (value === true) {
    return <Check className="h-4 w-4 text-brand mx-auto" aria-label="Included" />
  }
  if (value === false) {
    return <Minus className="h-4 w-4 text-[var(--text-muted)] mx-auto" aria-label="Not included" />
  }
  return <span className="text-sm font-medium text-[var(--text-primary)]">{value}</span>
}

interface ComparisonTableProps {
  billingPeriod: 'monthly' | 'annual'
}

export function ComparisonTable({ billingPeriod }: ComparisonTableProps) {
  const prices = tierPrices[billingPeriod]

  return (
    <section className="py-20 sm:py-24 bg-[var(--bg-subtle)]">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">

        <div className="text-center mb-14">
          <p className="text-label text-brand mb-3">Compare</p>
          <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
            Everything, side by side
          </h2>
        </div>

        <div className="overflow-x-auto rounded-xl border border-[var(--border-subtle)]">
          <table className="w-full min-w-[560px]" style={{ borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th
                  scope="col"
                  className="py-4 px-6 text-left text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider bg-[var(--bg-card)] border-b border-[var(--border-subtle)] w-[40%]"
                >
                  Feature
                </th>
                {tierKeys.map((key) => (
                  <th
                    key={key}
                    scope="col"
                    className={`py-4 px-4 text-center border-b border-[var(--border-subtle)] ${
                      key === 'pro' ? 'bg-brand-light' : 'bg-[var(--bg-card)]'
                    }`}
                  >
                    <p
                      className={`text-sm font-semibold ${
                        key === 'pro' ? 'text-brand' : 'text-[var(--text-primary)]'
                      }`}
                    >
                      {tierLabels[tierKeys.indexOf(key)]}
                    </p>
                    <p className="text-xs text-[var(--text-muted)] mt-0.5">{prices[key]}</p>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {featureGroups.map((group) => (
                <Fragment key={group.category}>
                  {/* Category header row */}
                  <tr>
                    <td
                      colSpan={4}
                      className="py-2.5 px-6 bg-[var(--bg-subtle)] text-label text-[var(--text-muted)]"
                    >
                      {group.category}
                    </td>
                  </tr>
                  {/* Feature rows */}
                  {group.rows.map((row) => (
                    <tr
                      key={row.label}
                      className="border-t border-[var(--border-subtle)] bg-[var(--bg-card)] hover:bg-[var(--bg-subtle)] transition-colors duration-150"
                    >
                      <td className="py-3.5 px-6 text-sm text-[var(--text-secondary)]">
                        {row.label}
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <Cell value={row.free} />
                      </td>
                      <td className="py-3.5 px-4 text-center bg-brand-light">
                        <Cell value={row.pro} />
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <Cell value={row.enterprise} />
                      </td>
                    </tr>
                  ))}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  )
}
