# SEO Best Practices for NextJS Marketing Sites

## Metadata Strategy

### Page-Level Metadata

Every page must export a `metadata` object or `generateMetadata` function:

```typescript
// Static metadata (most pages)
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Primary Keyword — Brand Name',           // 50-60 chars
  description: 'Compelling description with keyword that drives clicks.', // 150-160 chars
  alternates: { canonical: '/page-slug' },
  openGraph: {
    title: 'Primary Keyword — Brand Name',
    description: 'OG-specific description',
    url: '/page-slug',
    images: [{ url: '/og/page-slug.png', width: 1200, height: 630, alt: 'Descriptive alt' }],
  },
  twitter: { card: 'summary_large_image' },
}
```

```typescript
// Dynamic metadata (pages with params)
import { Metadata } from 'next'

export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const content = await getContent(params.slug)
  return {
    title: `${content.title} — Brand Name`,
    description: content.excerpt,
  }
}
```

### Title Patterns

- Homepage: `Brand Name — Value Proposition` (e.g., "Acme — The Fastest Widget Builder")
- Product pages: `Feature/Product Name — Brand Name`
- Blog posts: `Post Title — Brand Name`
- Use the `title.template` in root layout: `'%s | Brand Name'`

### Meta Descriptions

- Include the target keyword naturally
- Write as a compelling pitch (like ad copy)
- Include a call to action when appropriate
- Never duplicate across pages

## URL Structure

- **Lowercase, hyphenated**: `/features/api-integration` not `/Features/API_Integration`
- **Short and descriptive**: `/pricing` not `/our-pricing-plans-and-options`
- **Keyword-rich**: `/react-dashboard-template` not `/template-1`
- **No trailing slashes** (configure in next.config.js: `trailingSlash: false`)
- **No file extensions**: URLs should not end in `.html`

## Heading Hierarchy

Every page follows this structure:

```
<h1> — One per page. Contains primary keyword. (the page title)
  <h2> — Major sections. Contains secondary keywords.
    <h3> — Subsections. Supporting details.
      <h4> — Only if deeply nested content requires it.
```

Rules:
- Never skip levels (no h1 → h3)
- Never use headings for visual styling (use CSS instead)
- The `<h1>` should be visible on the page (not just in metadata)

## Semantic HTML

Use the right elements for the right purpose:

```html
<header>     <!-- Site header with nav -->
<nav>        <!-- Primary and secondary navigation -->
<main>       <!-- Primary page content (one per page) -->
<section>    <!-- Thematic grouping of content -->
<article>    <!-- Self-contained content (blog posts, cards) -->
<aside>      <!-- Sidebar, related content -->
<footer>     <!-- Site footer -->
<figure>     <!-- Images with captions -->
<figcaption> <!-- Caption for figures -->
<time>       <!-- Dates and times (with datetime attr) -->
<address>    <!-- Contact information -->
```

## Structured Data (JSON-LD)

Add structured data to help search engines understand page content.

### Organization (root layout or homepage):
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Company Name",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "sameAs": ["https://twitter.com/company", "https://linkedin.com/company/name"]
}
```

### WebSite (homepage):
```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Site Name",
  "url": "https://example.com"
}
```

### Product (product/pricing pages):
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Product Name",
  "description": "Product description",
  "offers": {
    "@type": "Offer",
    "price": "29.99",
    "priceCurrency": "USD"
  }
}
```

### FAQPage (FAQ sections):
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Question text?",
      "acceptedAnswer": { "@type": "Answer", "text": "Answer text." }
    }
  ]
}
```

### BreadcrumbList (all pages with breadcrumbs):
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com" },
    { "@type": "ListItem", "position": 2, "name": "Features", "item": "https://example.com/features" }
  ]
}
```

## Image Optimization

- Use `next/image` for all images — it handles lazy loading, responsive sizes, and format conversion
- Always set `width`, `height`, and `alt` attributes
- Use descriptive, keyword-containing alt text: "Dashboard showing real-time analytics" not "screenshot"
- Use `priority` prop only for above-the-fold images (hero, logo)
- Prefer `.webp` or `.avif` formats (Next.js handles this automatically)
- Generate OG images for social sharing (1200x630px)

```typescript
import Image from 'next/image'

<Image
  src="/hero-dashboard.webp"
  alt="Acme dashboard showing real-time sales analytics"
  width={1200}
  height={630}
  priority  // Only for above-the-fold
/>
```

## Internal Linking

- Use `next/link` for all internal links (enables client-side navigation)
- Use descriptive anchor text: "View our pricing plans" not "Click here"
- Link related pages to each other (features → pricing, blog → features)
- Include breadcrumb navigation on subpages
- Keep navigation consistent across all pages

```typescript
import Link from 'next/link'

<Link href="/pricing">View pricing plans</Link>
```

## Sitemap and Robots

**app/sitemap.ts** — Include all public pages with priorities:
```typescript
import { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://example.com'
  return [
    { url: baseUrl, lastModified: new Date(), changeFrequency: 'weekly', priority: 1.0 },
    { url: `${baseUrl}/features`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
    { url: `${baseUrl}/pricing`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
    { url: `${baseUrl}/about`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.5 },
    { url: `${baseUrl}/contact`, lastModified: new Date(), changeFrequency: 'yearly', priority: 0.5 },
  ]
}
```

**app/robots.ts**:
```typescript
import { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      { userAgent: '*', allow: '/', disallow: ['/api/', '/_next/'] },
    ],
    sitemap: 'https://example.com/sitemap.xml',
  }
}
```

## Performance = SEO

Google's Core Web Vitals directly impact rankings:

- **LCP (Largest Contentful Paint) < 2.5s**: Use `priority` on hero images, preload fonts
- **FID (First Input Delay) < 100ms**: Minimize client-side JS, use Server Components
- **CLS (Cumulative Layout Shift) < 0.1**: Set image dimensions, use `next/font`

NextJS best practices that support this:
- Default to Server Components (zero client JS)
- Use `'use client'` only for interactive elements
- Use `next/font` with `display: 'swap'` to prevent font-related layout shift
- Use `next/image` to prevent image-related layout shift
- Lazy load below-the-fold content with `dynamic()` imports
- Keep the initial bundle small — code-split aggressively

## Common Marketing Page Patterns

### Hero Section
- Clear, concise headline (h1) with primary keyword
- Supporting subtext (1-2 sentences)
- Primary CTA button (high contrast, above the fold)
- Hero image or illustration
- Optional: social proof badges, stats, trust indicators

### Features Section
- Section heading (h2) with secondary keyword
- 3-6 feature cards with icons, titles, descriptions
- Each feature should link to more detail if available

### Social Proof
- Customer logos (use grayscale for consistency)
- Testimonial quotes with names and titles
- Statistics ("10,000+ customers", "99.9% uptime")

### Pricing Table
- Clear tier names and prices
- Feature comparison list
- Highlighted "most popular" tier
- CTA button on each tier

### CTA Sections
- Repeated throughout the page (not just once)
- Clear action verb: "Start free trial", "Get started", "Book a demo"
- Supporting text that addresses the last objection

### Footer
- Organized link columns (Product, Company, Resources, Legal)
- Newsletter signup form
- Social media links
- Copyright and legal links (Privacy, Terms)
