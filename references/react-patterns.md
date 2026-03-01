# Essential React & Next.js Patterns

Bundled subset of critical patterns from Vercel's react-best-practices.
If the full `vercel-react-best-practices` skill is installed, prefer that for comprehensive coverage.

## Server Components by Default

Next.js App Router uses Server Components by default. This means zero JavaScript shipped
to the client unless you explicitly opt in with `'use client'`.

**Rule**: Only add `'use client'` when the component needs:
- Event handlers (onClick, onChange, onSubmit)
- useState, useEffect, useRef, or other hooks
- Browser APIs (window, document, localStorage)

```typescript
// GOOD: Server Component (default) — no JS sent to client
export default function HeroSection() {
  return (
    <section className="py-20">
      <h1>Build Better Products</h1>
      <p>Ship faster with our platform.</p>
    </section>
  )
}

// Client component only when interactivity is needed
'use client'
import { useState } from 'react'

export function MobileMenu() {
  const [open, setOpen] = useState(false)
  return (
    <button onClick={() => setOpen(!open)}>Menu</button>
    // ...
  )
}
```

## Eliminate Async Waterfalls (CRITICAL)

Never await sequentially when requests are independent:

```typescript
// BAD: Sequential — each request waits for the previous
const features = await getFeatures()
const testimonials = await getTestimonials()
const pricing = await getPricing()

// GOOD: Parallel — all requests fire simultaneously
const [features, testimonials, pricing] = await Promise.all([
  getFeatures(),
  getTestimonials(),
  getPricing(),
])
```

## Bundle Size (CRITICAL)

### Avoid Barrel Imports
```typescript
// BAD: Imports entire library
import { Button } from '@/components/ui'

// GOOD: Direct import
import { Button } from '@/components/ui/button'
```

### Dynamic Imports for Heavy Components
```typescript
import dynamic from 'next/dynamic'

// Load chart component only when needed
const Chart = dynamic(() => import('@/components/chart'), {
  loading: () => <div className="h-64 animate-pulse bg-muted rounded" />,
})
```

### Don't Import What You Don't Need
```typescript
// BAD: Import entire icon library
import * as Icons from 'lucide-react'

// GOOD: Import specific icons
import { ArrowRight, Check, Star } from 'lucide-react'
```

## Image Optimization

Always use `next/image`:

```typescript
import Image from 'next/image'

// With known dimensions (preferred)
<Image src="/hero.webp" alt="Product dashboard" width={1200} height={630} priority />

// Fill mode for responsive containers
<div className="relative aspect-video">
  <Image src="/hero.webp" alt="Product dashboard" fill className="object-cover" />
</div>
```

## Font Optimization

Use `next/font` to prevent layout shift:

```typescript
import { Inter, Poppins } from 'next/font/google'

const inter = Inter({ subsets: ['latin'], display: 'swap', variable: '--font-inter' })
const poppins = Poppins({
  subsets: ['latin'],
  weight: ['400', '600', '700'],
  display: 'swap',
  variable: '--font-poppins',
})
```

## Data Fetching Patterns

### Fetch in Server Components
```typescript
// Server Component — data fetched at build or request time, zero client JS
export default async function PricingPage() {
  const plans = await getPlans()  // Runs on the server only
  return <PricingTable plans={plans} />
}
```

### Use Suspense for Loading States
```typescript
import { Suspense } from 'react'

export default function Page() {
  return (
    <main>
      <HeroSection />  {/* Renders immediately */}
      <Suspense fallback={<TestimonialsSkeleton />}>
        <Testimonials />  {/* Streams in when ready */}
      </Suspense>
    </main>
  )
}
```

## Component Patterns for Marketing Sites

### Section Wrapper
```typescript
interface SectionProps {
  children: React.ReactNode
  className?: string
  id?: string
}

export function Section({ children, className = '', id }: SectionProps) {
  return (
    <section id={id} className={`py-16 md:py-24 ${className}`}>
      <div className="container mx-auto px-4 md:px-6">{children}</div>
    </section>
  )
}
```

### CTA Button
```typescript
import Link from 'next/link'

interface CTAProps {
  href: string
  children: React.ReactNode
  variant?: 'primary' | 'secondary'
}

export function CTA({ href, children, variant = 'primary' }: CTAProps) {
  const styles = variant === 'primary'
    ? 'bg-primary text-primary-foreground hover:bg-primary/90'
    : 'border border-input bg-background hover:bg-accent'
  return (
    <Link href={href} className={`inline-flex items-center justify-center rounded-md px-6 py-3 text-sm font-medium transition-colors ${styles}`}>
      {children}
    </Link>
  )
}
```

### Feature Card
```typescript
import { LucideIcon } from 'lucide-react'

interface FeatureCardProps {
  icon: LucideIcon
  title: string
  description: string
}

export function FeatureCard({ icon: Icon, title, description }: FeatureCardProps) {
  return (
    <div className="flex flex-col items-start gap-3 rounded-lg border p-6">
      <div className="rounded-md bg-primary/10 p-2">
        <Icon className="h-6 w-6 text-primary" />
      </div>
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
    </div>
  )
}
```

## Error Handling

### error.tsx (per route)
```typescript
'use client'

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4">
      <h2 className="text-2xl font-bold">Something went wrong</h2>
      <button onClick={reset} className="rounded bg-primary px-4 py-2 text-white">
        Try again
      </button>
    </div>
  )
}
```

### not-found.tsx
```typescript
import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4">
      <h1 className="text-4xl font-bold">404</h1>
      <p className="text-muted-foreground">Page not found</p>
      <Link href="/" className="text-primary underline">Go home</Link>
    </div>
  )
}
```

## Performance Checklist

- [ ] Server Components used by default (no unnecessary 'use client')
- [ ] `next/image` for all images
- [ ] `next/font` for all fonts
- [ ] `next/link` for all internal links
- [ ] No barrel imports
- [ ] Dynamic imports for heavy/below-fold components
- [ ] Parallel data fetching (Promise.all)
- [ ] Suspense boundaries for async content
- [ ] No unnecessary re-renders (stable references for callbacks)
