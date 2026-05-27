import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'

// [PLACEHOLDER] — update with real product and billing policies before launch
const faqs = [
  {
    q: 'What counts as a job?',
    a: 'A job is a single API call that processes a media file — trimming a video, compressing an image, transcoding audio, and so on. Each operation counts as one job regardless of file size or output format.',
  },
  {
    q: 'What happens when I reach my monthly limit?',
    a: "Processing pauses until your next billing cycle resets. You'll receive an email notification as you approach your limit. You can upgrade your plan at any time and the new limit takes effect immediately.",
  },
  {
    q: 'Can I switch plans at any time?',
    a: 'Yes. Upgrades take effect immediately and are prorated for the remainder of the billing cycle. Downgrades take effect at the start of your next billing cycle.',
  },
  {
    q: 'Is there a free trial for the Pro plan?',
    a: "The Free tier lets you explore the full API with 100 jobs per month at no cost — no credit card required. You can upgrade to Pro at any point when you're ready to scale.",
  },
  {
    q: 'How does annual billing work?',
    a: "Annual billing charges you upfront for 12 months and saves you 20% compared to the monthly rate. Pro annually is $276 / yr instead of $348 / yr — that's two months free.",
  },
  {
    q: 'Do you offer refunds?',
    a: "We offer a 14-day refund window for new Pro subscriptions. If you're not satisfied within the first 14 days of your first charge, contact support and we'll issue a full refund.",
  },
  {
    q: "What's included in an Enterprise plan?",
    a: 'Enterprise plans include custom job limits, custom storage, SLA guarantees, a dedicated support contact, and a tailored onboarding process. Contact us to discuss your specific requirements.',
  },
]

export function PricingFAQ() {
  return (
    <section className="py-20 sm:py-24">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">

        <div className="text-center mb-14">
          <p className="text-label text-brand mb-3">FAQ</p>
          <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
            Common questions
          </h2>
        </div>

        <div className="max-w-3xl mx-auto">
          <Accordion type="single" collapsible className="flex flex-col gap-2">
            {faqs.map((faq, i) => (
              <AccordionItem
                key={i}
                value={`faq-${i}`}
                className="rounded-xl border border-(--border-subtle) bg-(--bg-card) px-6 not-last:border-b data-open:border-(--border-strong) transition-colors duration-200"
              >
                <AccordionTrigger className="py-4 text-sm font-medium text-[var(--text-primary)] hover:no-underline">
                  {faq.q}
                </AccordionTrigger>
                <AccordionContent className="text-sm text-[var(--text-secondary)] leading-relaxed pb-4">
                  {faq.a}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>

      </div>
    </section>
  )
}
