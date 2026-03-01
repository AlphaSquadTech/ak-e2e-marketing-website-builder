# Workflow Phases — Detailed Instructions

**Important**: Before starting any phase, the preflight script must have been run.
The SKILL.md instructs Claude to run `bash <skill-path>/scripts/preflight.sh` before
doing any work. If preflight hasn't run yet in this session, run it now.

## Phase 0: Document Analysis & Plan Generation

### Parse the Source Document(s)

Based on the file type, extract content appropriately:

**Markdown (.md):** Read directly. H1 = site/page title. H2s = major sections. H3s = subsections.

**Word (.docx):** Use python-docx or the docx skill to extract text with heading hierarchy.
```bash
pip install python-docx --break-system-packages 2>/dev/null
python3 -c "
import docx
doc = docx.Document('input.docx')
for para in doc.paragraphs:
    prefix = '#' * int(para.style.name[-1]) if para.style.name.startswith('Heading') else ''
    if prefix or para.text.strip():
        print(f'{prefix} {para.text}' if prefix else para.text)
" > extracted-content.md
```

**PDF (.pdf):** Use pdfplumber for text extraction. If text is sparse or garbled, take a
screenshot of each page and use vision to extract content.
```bash
pip install pdfplumber --break-system-packages 2>/dev/null
python3 -c "
import pdfplumber
with pdfplumber.open('input.pdf') as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text:
            print(f'--- Page {i+1} ---')
            print(text)
" > extracted-content.md
```

**OpenAPI (.yaml/.json):** Parse the spec to extract:
- API title, description, version → hero section content
- Endpoints grouped by tag → documentation pages
- Request/response schemas → interactive examples
- Authentication details → getting started section

**Multiple files:** Read each, then organize into a unified content map.

### Content Mapping

After extraction, map content to a website structure:

1. **Identify the primary message** — What is this document selling/explaining/promoting?
2. **Extract key sections** — Group content into logical page-sized chunks
3. **Identify CTAs** — What actions should visitors take? (sign up, contact, download, buy)
4. **Find social proof** — Testimonials, stats, logos, case studies mentioned
5. **Note technical details** — Features, specifications, pricing tiers, API details

### Generate the Site Plan

Create a plan following `templates/project-plan.json`. For a marketing site, the typical structure:

- **Homepage** (`/`): Hero with primary value prop, key features, social proof, CTA
- **Features/Product** (`/features`): Detailed feature breakdown with visuals
- **Pricing** (`/pricing`): Pricing tiers if applicable
- **About** (`/about`): Company/team/mission story
- **Contact** (`/contact`): Contact form, location, support info
- **Docs/API** (`/docs`): If source is OpenAPI spec, generated API documentation
- **Blog** (`/blog`): If blog content is in the source documents

Adjust based on what the document actually contains. Don't create pages for content
that doesn't exist in the source.

### SEO Strategy (Built Into Plan)

For each page in the plan, define:
- **Target keywords**: Based on the document's subject matter
- **Meta title**: 50-60 chars, includes primary keyword
- **Meta description**: 150-160 chars, compelling + includes keyword
- **URL slug**: Short, keyword-rich, lowercase, hyphens
- **H1**: One per page, contains primary keyword
- **Structured data type**: Article, Product, FAQPage, Organization, etc.

### Save Plan and Initialize State

```bash
python <skill-path>/scripts/state_manager.py --action init \
  --plan project-plan.json \
  --output .nextjs-builder-state.json
```

Proceed immediately to Phase 1 — the skill operates autonomously. Only pause for user
input if the document is too ambiguous to generate a reasonable plan.

---

## Phase 1: Project Scaffolding

### Collect Design Inputs (MANDATORY — Do Not Skip)

**You MUST ask the user for their design preferences before scaffolding.** Do not
proceed to scaffolding without these values. Do not silently pick defaults. Always
ask, wait for a response, and then proceed.

If the user already provided these values in their initial message, use them directly
without re-asking. Only pick defaults if the user explicitly says "pick for me" or
"I don't care."

Ask for exactly three inputs:

1. **Accent color** — A hex code (e.g., `#2563eb`), color name (e.g., "blue"), or "pick for me"
2. **Font preference** — One of these presets, or a specific Google Font name:
   - `modern` → Inter or DM Sans (clean, versatile)
   - `elegant` → Playfair Display headings + Inter body (sophisticated)
   - `bold` → Plus Jakarta Sans (confident, startup-y)
   - `minimal` → Geist (understated, technical)
3. **Gemini API key** — Their `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) for AI image generation
   in Phase 2.5. If they don't have one, direct them to https://aistudio.google.com/apikey.
   If they want to skip, the site will use branded SVG placeholders instead.

Default mapping for colors/fonts (only used when user says "pick for me"):
- SaaS/tech → `#2563eb` (blue) + modern
- Finance → `#0f172a` (dark navy) + modern
- Creative/agency → `#7c3aed` (purple) + bold
- Luxury/premium → `#18181b` (near-black) + elegant
- Health/wellness → `#059669` (green) + minimal
- Education → `#2563eb` (blue) + minimal

Save the user's choices in the state file under `design_inputs`:
- `accent_color` and `font_preference` persist across sessions and flow into image
  manifest entries (`brand.accent_color`, `brand.font`), placeholder SVGs, and the
  CLAUDE.md/GEMINI.md context files.
- `gemini_api_key` is saved so it can be auto-exported before running `generate_images.py`
  in Phase 2.5 — the user won't need to provide it again in later sessions.

### Generate Full Design System from Inputs

From the accent color and font choice, automatically derive the complete design system:

```
Given accent color (e.g., #2563eb):
  primary        = accent color                    → buttons, links, key highlights
  primary-fg     = white or dark (auto-contrast)   → text on primary buttons
  secondary      = accent desaturated 30%, +15 lightness → secondary buttons, badges
  background     = #ffffff                         → page background
  foreground     = #0a0a0a                         → primary text
  muted          = #6b7280                         → secondary text, placeholders
  muted-bg       = #f3f4f6                         → subtle backgrounds, cards
  border         = #e5e7eb                         → borders, dividers
  accent         = primary at 10% opacity          → hover states, highlights
  destructive    = #ef4444                         → errors, destructive actions

Given font preference:
  modern   → font-sans: Inter,         font-heading: Inter
  elegant  → font-sans: Inter,         font-heading: Playfair Display
  bold     → font-sans: Plus Jakarta Sans, font-heading: Plus Jakarta Sans
  minimal  → font-sans: Geist,         font-heading: Geist
```

### Initialize NextJS

```bash
bash <skill-path>/scripts/init_project.sh <project-name>
```

### Install Dependencies

```bash
cd <project-name>

# UI framework
npx shadcn@latest init -y
npx shadcn@latest add button card input label textarea separator badge

# Icons
npm install lucide-react

# SEO essentials (Next.js has built-in support, but these help)
npm install next-sitemap schema-dts

# Forms (if the plan includes contact/signup forms)
npm install react-hook-form zod @hookform/resolvers

# Content (if processing markdown content)
npm install gray-matter remark remark-html
```

### Apply Design System

Using the generated palette and font, configure:

**tailwind.config.ts** — Map the generated colors and font to Tailwind:
```typescript
// Colors derived from accent color
theme: {
  extend: {
    colors: {
      primary: { DEFAULT: '<accent>', foreground: '<auto-contrast>' },
      secondary: { DEFAULT: '<derived>', foreground: '<auto>' },
      muted: { DEFAULT: '<muted-bg>', foreground: '<muted>' },
      border: '<border>',
      destructive: { DEFAULT: '#ef4444', foreground: '#ffffff' },
    },
    fontFamily: {
      sans: ['var(--font-body)', 'system-ui', 'sans-serif'],
      heading: ['var(--font-heading)', 'system-ui', 'sans-serif'],
    },
  },
}
```

**app/globals.css** — CSS custom properties using the generated palette

**app/layout.tsx** — Import the chosen font(s) via `next/font/google`, apply as CSS variables

### Configure SEO Infrastructure

**next.config.js** — Enable all SEO-friendly features:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    formats: ['image/avif', 'image/webp'],
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-XSS-Protection', value: '1; mode=block' },
        ],
      },
    ];
  },
};
module.exports = nextConfig;
```

**app/sitemap.ts** — Dynamic sitemap generation:
```typescript
import { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://example.com'
  return [
    { url: baseUrl, lastModified: new Date(), changeFrequency: 'weekly', priority: 1 },
    // Add all pages from the plan
  ]
}
```

**app/robots.ts** — Robots.txt:
```typescript
import { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://example.com'
  return {
    rules: { userAgent: '*', allow: '/' },
    sitemap: `${baseUrl}/sitemap.xml`,
  }
}
```

**app/layout.tsx** — Root layout with SEO metadata, chosen font, analytics placeholder:
```typescript
import type { Metadata } from 'next'
import { Inter } from 'next/font/google' // Replace with user's font choice
import './globals.css'

const bodyFont = Inter({ subsets: ['latin'], display: 'swap', variable: '--font-body' })
// If elegant preset: also import Playfair Display for headings

export const metadata: Metadata = {
  title: { default: 'Site Name', template: '%s | Site Name' },
  description: 'Site description from the plan',
  openGraph: { type: 'website', locale: 'en_US', siteName: 'Site Name' },
  twitter: { card: 'summary_large_image' },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
```

### Set Up Design System

Based on the document's tone and subject matter, configure:

1. **tailwind.config.ts** — Custom colors, fonts, spacing
2. **app/globals.css** — CSS custom properties, base styles
3. **Shared components**: Header/Nav, Footer, Section wrappers, CTA buttons

### Verify Scaffolding

```bash
npm run dev &
sleep 5
agent-browser open http://localhost:3000
agent-browser wait --load networkidle
agent-browser screenshot screenshots/scaffold.png
```

Read the screenshot. Confirm the base layout renders. Fix any issues.

### Generate Context File

Generate the AI context file that enforces verification on every turn:

```bash
bash <skill-path>/scripts/generate_context_file.sh --project-dir <project-name>
```

This creates `CLAUDE.md` and `GEMINI.md` in the project root. Claude Code reads
`CLAUDE.md` on every interaction; Gemini CLI reads `GEMINI.md`. Both contain the
verification rules and quick-reference commands.

This step is critical. Without the context file, the AI will gradually forget to
verify its work over long sessions.

```bash
python <skill-path>/scripts/state_manager.py --action set-phase --phase build
```

---

## Phase 2: Autonomous Build

For each page in the plan's build order:

### 2.1 Implement the Page

Create `app/<route>/page.tsx` with:

**SEO metadata** (every page must have this):
```typescript
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Page Title — Primary Keyword',
  description: 'Compelling 150-char description with target keyword.',
  openGraph: {
    title: 'Page Title',
    description: 'OG description',
    images: [{ url: '/og/page-name.png', width: 1200, height: 630 }],
  },
}
```

**Semantic HTML structure**:
- One `<h1>` per page with target keyword
- Logical heading hierarchy (h1 → h2 → h3)
- `<section>`, `<article>`, `<nav>`, `<main>`, `<footer>` elements
- `<a>` tags with descriptive text (not "click here")
- Images with descriptive `alt` text containing relevant keywords

**Content from the source document**:
- Copy text directly from the extracted content — don't fabricate
- Reorganize for web readability: short paragraphs, clear headings, bullet points where appropriate
- Add CTAs where the plan specifies them

**Structured data** (JSON-LD) where applicable:
```typescript
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{
    __html: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'WebPage',
      name: 'Page Title',
      description: 'Page description',
    }),
  }}
/>
```

**Image handling** (every page):

For every image the page needs (hero images, illustrations, icons, OG images, etc.):

1. Determine the image's purpose, ideal dimensions, and aspect ratio
2. Write a descriptive prompt for AI generation (see [references/image-generation.md](image-generation.md))
3. Add an entry to `image-manifest.json`. Include: id, path, placeholder path, prompt, alt text, context, dimensions, aspect ratio, style, brand object (accent_color, font, mood from design_inputs), page_id, priority, status="placeholder"
4. Generate the placeholder SVG:
   ```bash
   python <skill-path>/scripts/generate_placeholders.py
   ```
5. Reference the placeholder path in the component:
   ```tsx
   <Image
     src="/images/placeholders/hero-main.svg"
     alt="Descriptive alt text with keywords"
     width={1200}
     height={630}
     priority  // Only for above-the-fold images
   />
   ```

The visual verification step will see branded placeholders — this is expected and correct
during Phase 2. Real images are generated in Phase 2.5.

### 2.2 Visual Verification (Mandatory — One Command)

After implementing each page, verify it visually. **This is not optional.**
The state manager will reject any attempt to mark the page as `verified` without proof.

**Run the verification script:**
```bash
bash <skill-path>/scripts/verify_page.sh <route> <page-id>
# Example: bash <skill-path>/scripts/verify_page.sh / home
```

This single command handles: dev server check → navigation → wait for load →
full-page screenshot → chunking for vision analysis.

Then **analyze every chunk** the script outputs. Read each image file sequentially
(they represent the page from top to bottom). For each chunk evaluate:

- **Layout**: Properly aligned? No overlapping elements?
- **Content**: Correct text from source document? Readable? Not clipped?
- **Design**: Accent color correct? Visual hierarchy clear? Typography consistent?
- **CTAs**: Buttons visible and prominent?
- **Issues**: Blank areas? Broken images? Horizontal overflow?

See [references/visual-verification.md](visual-verification.md) for detailed
per-section criteria.

**Record the result:**
```bash
# If verification passed:
python <skill-path>/scripts/state_manager.py \
  --action add-verification --page-id <id> --result pass \
  --screenshot screenshots/<id>-v1-full.png \
  --notes "All sections verified. Layout, content, and design correct."

# If issues found:
python <skill-path>/scripts/state_manager.py \
  --action add-verification --page-id <id> --result fail \
  --screenshot screenshots/<id>-v1-full.png \
  --notes "Hero CTA not visible. Footer links misaligned."
```

If issues were found: fix them → re-run `verify_page.sh` (it auto-increments the
iteration number) → re-analyze → re-record. Maximum 3 iterations.

### 2.3 Regression Check

After each page, spot-check one previously verified page to catch regressions
(especially if shared components were modified).

### 2.4 Continue to Next Page

Move to the next page in the build order. Repeat until all pages are done.

---

## Phase 2.5: Image Generation

After all pages are built and verified with placeholders, generate real images.

### Prerequisites

1. **google-genai SDK**: `pip install google-genai --break-system-packages`
2. **Pillow** for image resizing: `pip install Pillow --break-system-packages`
3. **Gemini API key**: Should already be saved in the state file from Phase 1 design inputs.

Export the saved API key before running the generation script:

```bash
# Load the API key from the state file (saved during Phase 1 design inputs)
export GEMINI_API_KEY="$(python3 -c "import json; print(json.load(open('.nextjs-builder-state.json'))['design_inputs'].get('gemini_api_key',''))")"

# If empty, the user didn't provide one — ask them now
if [ -z "$GEMINI_API_KEY" ]; then
  echo "⚠ No Gemini API key saved in state file."
  echo "  Get a key from https://aistudio.google.com/apikey"
  echo "  Then provide it so it can be saved for this project."
fi
```

If the API key is missing at this point (user skipped it in Phase 1), ask the user for it
now. If they provide it, save it to the state file under `design_inputs.gemini_api_key`
so it persists for future sessions. If they decline, skip this phase and proceed to
Phase 3 with placeholders — the site is fully functional without real images.

### Dry Run (Review Prompts)

```bash
python <skill-path>/scripts/generate_images.py --manifest image-manifest.json --dry-run
```

Review the output. Each constructed prompt should be specific, descriptive, and include
aspect ratio + style context. Edit any prompts in `image-manifest.json` that need
improvement before spending API credits.

### Generate All Images

```bash
python <skill-path>/scripts/generate_images.py --manifest image-manifest.json
```

This takes ~4-6 seconds per image. A typical site with 8-15 images completes in 1-2 minutes.

### Apply a Visual Style

```bash
python <skill-path>/scripts/generate_images.py --style photorealistic
```

Available styles: photorealistic, watercolor, oil-painting, sketch, pixel-art, anime,
vintage, modern, abstract, minimalist. This overrides per-entry styles for consistency.

### Swap Placeholder References

After generation, replace placeholder paths with real image paths in all page components:

For each entry in the manifest where `status` is now `generated`:
- Find: `src="/images/placeholders/{id}.svg"`
- Replace with: `src="/images/{id}.webp"` (or whatever the entry's `path` resolves to under `public/`)

### Visual Re-verification

After swapping images, take a new full-page screenshot of each page and verify that:
- Images render correctly (no broken images, no distortion)
- Images match the page context (hero image looks like a hero, icons look like icons)
- Colors harmonize with the site's design system
- Layout is not disrupted by different image dimensions

This is a quick pass — the layout was already verified in Phase 2. Focus on image quality and fit.

### Update State

```bash
python <skill-path>/scripts/state_manager.py --action log \
  --message "Phase 2.5: Generated N images via Gemini API. Swapped placeholders."
```

Proceed to Phase 3 (Audit).

---

## Phase 3: Final Audit

### Full-Site Visual Pass

Take full-page screenshots (`--full`) of every page at desktop, tablet (768px), and
mobile (375px) viewports. Chunk and analyze each to check for consistency across the site.

### SEO Audit Checklist

Run through every page and verify:

- [ ] Every page has unique `<title>` and `<meta description>`
- [ ] Every page has exactly one `<h1>`
- [ ] Heading hierarchy is correct (no skipped levels)
- [ ] All images have descriptive `alt` text
- [ ] All internal links use `<Link>` from next/link (not `<a>`)
- [ ] `sitemap.xml` includes all pages
- [ ] `robots.txt` is configured correctly
- [ ] Open Graph tags are set on all pages
- [ ] Structured data (JSON-LD) is present on key pages
- [ ] URLs are clean, lowercase, hyphenated
- [ ] No duplicate content across pages
- [ ] `next/image` used for all images (optimized formats + lazy loading)
- [ ] `next/font` used for fonts (no layout shift)
- [ ] Canonical URLs are set if needed

### Performance Check

```bash
npm run build
```

Check for build warnings. Ensure:
- No pages are unnecessarily client-side rendered
- Bundle size is reasonable
- No unused dependencies
- Images are optimized

### Accessibility Check

For each page verify:
- All form inputs have associated labels
- Interactive elements are keyboard-focusable
- Color contrast meets WCAG AA (4.5:1 for normal text, 3:1 for large)
- Skip-to-content link exists
- ARIA labels on icon-only buttons

### Deliver

Update state to complete:
```bash
python <skill-path>/scripts/state_manager.py --action set-phase --phase complete
```

Present the user with:
- Summary of all pages built (routes, titles, key content)
- Screenshot gallery (link to screenshots/ directory)
- Any unresolved issues logged in the state file
- Deployment instructions: `npx vercel deploy` or `npm run build && npm start`

---

## Brownfield Entry (Existing Projects)

When using this skill on an existing NextJS project instead of building from scratch,
the phases become modular operations rather than a linear pipeline.

### Collect Design Inputs (MANDATORY — Do Not Skip)

**You MUST ask the user for their design preferences before scanning.** Same rule as
fresh projects — do not silently pick defaults. If the user already provided values in
their initial message, use them directly. Only pick defaults if they say "pick for me."

1. **Accent color** — A hex color (e.g. `#2563eb`). If the user doesn't have one, try
   to detect it from the project's existing `tailwind.config.*` or global CSS. As a last
   resort, pick a sensible default based on the project's domain.

2. **Font preference** — One of `modern`, `elegant`, `bold`, `minimal`, or a specific
   Google Font name. If the user doesn't have one, check the project's existing
   `next/font` imports or font configuration.

3. **Gemini API key** — Their `GEMINI_API_KEY` for AI image generation. If they don't have
   one, point them to https://aistudio.google.com/apikey. If they want to skip, that's fine.

These values flow into the state file (`design_inputs`), the image manifest (`brand`
objects on every entry), and placeholder SVGs. The API key is saved so it auto-exports
before image generation. Skipping this step produces generic defaults that won't match
the existing project's visual identity.

### Scan the Project

```bash
python <skill-path>/scripts/scan_project.py --project-dir . \
  --accent-color "<user's color>" --font "<user's font>"
```

This produces:
- `.nextjs-builder-state.json` — Pages discovered, statuses inferred, SEO issues flagged
- `image-manifest.json` — Placeholder images found, needing prompts

Review both files. The scan uses heuristics — you may need to adjust page statuses,
add missing pages, or refine image manifest prompts.

### Generate Context File

```bash
bash <skill-path>/scripts/generate_context_file.sh --project-dir .
```

Always do this. The context file prevents verification amnesia.

### Targeted Work

Instead of running all phases sequentially, pick what the project needs:

**Add a new page:**
1. Create `app/<route>/page.tsx` with metadata, semantic HTML, content
2. Add image manifest entries if the page needs images
3. Run `generate_placeholders.py`
4. Run `verify_page.sh <route> <page-id>`
5. Analyze chunks → fix → re-verify
6. Record verification in state manager

**Fix SEO issues flagged by scan:**
1. Read `state_manager.py --action summary` to see issues
2. Add missing metadata exports, h1 tags, structured data, alt text
3. Verify each fixed page

**Generate images for existing placeholders:**
1. Edit `image-manifest.json` — write real prompts for each placeholder entry
   (the scanner fills in `[NEEDS PROMPT]` placeholders)
2. Run `generate_images.py --dry-run` to review prompts
3. Run `generate_images.py` to generate
4. Swap placeholder references in code
5. Re-verify affected pages

**Run a full audit on existing pages:**
1. Set phase: `state_manager.py --action set-phase --phase audit`
2. Follow Phase 3 (Audit) instructions
3. Verify at all viewports: desktop, tablet, mobile

### Verification for Brownfield Changes

The same rule applies: verify after every change. The `verify_page.sh` script works
on any page, whether it was built by this skill or already existed.

```bash
# Verify specific pages you changed
bash <skill-path>/scripts/verify_page.sh /about about
bash <skill-path>/scripts/verify_page.sh /about about --viewport mobile

# List all pages needing verification
python <skill-path>/scripts/state_manager.py --action verify-all
```
