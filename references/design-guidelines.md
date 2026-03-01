# Marketing Website Design Guidelines

Essential design rules for building professional marketing websites.
If the full `web-design-guidelines` skill is installed, also run it for comprehensive coverage.

## Layout Fundamentals

### Responsive Grid
- Use a consistent container width: `max-w-7xl mx-auto px-4 md:px-6`
- Design mobile-first, then layer on tablet and desktop styles
- Use CSS Grid or Flexbox — never absolute positioning for layout
- Content should be readable at every breakpoint from 320px to 2560px

### Spacing System
Use a consistent spacing scale. Tailwind's default scale works well:
- Between sections: `py-16 md:py-24` (generous breathing room)
- Between elements within a section: `gap-8` or `gap-12`
- Between text elements: `space-y-4` or `space-y-6`
- Never mix arbitrary spacing values — stick to the scale

### Visual Hierarchy
Content importance should be immediately clear through:
- **Size**: Larger = more important (h1 > h2 > h3 > body)
- **Weight**: Bolder = more important for headings
- **Color**: Primary/accent for emphasis, muted for supporting text
- **Position**: Most important content above the fold
- **Whitespace**: Important elements get more surrounding space

## Typography

### Font Selection
- Use 1-2 font families max (one for headings, one for body — or the same for both)
- Sans-serif fonts are standard for marketing sites (Inter, Plus Jakarta Sans, DM Sans)
- Load via `next/font` to prevent layout shift

### Type Scale
```
h1: text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight
h2: text-3xl md:text-4xl font-bold tracking-tight
h3: text-xl md:text-2xl font-semibold
h4: text-lg font-semibold
body: text-base (16px)
small: text-sm
caption: text-xs
```

### Line Length
- Body text: 45-75 characters per line (use `max-w-prose` or `max-w-2xl`)
- Headings can be wider but shouldn't span the full page width
- Centered text should be limited to 2-3 lines max

## Color

### System Structure
Every marketing site needs:
- **Primary**: Brand color for CTAs and key interactive elements
- **Secondary**: Supporting color for variety
- **Background**: Page background (usually white or very light gray)
- **Foreground**: Primary text color (usually near-black)
- **Muted**: Secondary text, borders, subtle backgrounds
- **Accent**: Highlight color for badges, tags, small details

### Contrast Requirements (WCAG AA)
- Normal text (< 18px): 4.5:1 contrast ratio minimum
- Large text (>= 18px bold or >= 24px): 3:1 minimum
- UI components and graphical objects: 3:1 minimum
- Never place text on busy image backgrounds without an overlay

### Dark/Light Best Practices
- Primary CTA buttons should stand out in both modes
- Don't use pure black (#000) for dark mode backgrounds — use dark gray (#0a0a0a, #111)
- Don't use pure white (#fff) for light mode text backgrounds if it feels harsh — try #fafafa

## Buttons & CTAs

### Hierarchy
- **Primary CTA**: Solid fill, high contrast, used for the main action (1 per section max)
- **Secondary CTA**: Outlined or subdued, for alternative actions
- **Tertiary/Link**: Text with underline or arrow, for navigation

### Sizing
- Minimum tap target: 44x44px on mobile
- Standard button padding: `px-6 py-3` (comfortable click area)
- Full-width on mobile for primary actions: `w-full md:w-auto`

### Labels
- Use action verbs: "Get started", "Start free trial", "Book a demo"
- Be specific: "Download the guide" > "Download" > "Click here"
- Keep to 2-4 words when possible

## Images & Media

### Hero Images
- Full-width or contained, always above the fold
- Use `priority` prop in `next/image` to prevent LCP delays
- Provide a meaningful `alt` description
- Consider using illustration or product screenshots over stock photos

### Icons
- Use a consistent icon set (Lucide React recommended)
- Icons should enhance, not replace, text labels
- Minimum size: 20x20px for legibility
- Use `aria-hidden="true"` on decorative icons

### Aspect Ratios
- Hero/banner: 16:9 or 3:1
- Feature images: 4:3 or 1:1
- Thumbnails: 1:1 or 4:3
- OG images: exactly 1200x630px

## Forms

### Labels & Inputs
- Every input must have a visible label (not just placeholder)
- Use `htmlFor`/`id` to associate labels with inputs
- Group related fields with `<fieldset>` and `<legend>`
- Show validation errors inline, below the relevant field
- Use `type` attributes correctly (email, tel, url, etc.)

### UX
- Keep forms short — ask for the minimum needed
- Use a single-column layout for forms (easier to scan)
- Disable the submit button while submitting (with loading indicator)
- Show a clear success message after submission
- Don't clear the form on validation error

## Navigation

### Header
- Logo on the left, primary nav links center or right
- Primary CTA button in the top-right corner
- Hamburger menu on mobile (opens full-screen or slide-out)
- Sticky header is common for marketing sites (`sticky top-0 z-50`)

### Footer
- Organized in columns: Product, Company, Resources, Legal
- Include newsletter signup if applicable
- Social media links with icon + aria-label
- Copyright notice and year

### Internal Linking
- Every page should be reachable within 2-3 clicks from the homepage
- Use breadcrumbs on subpages for orientation
- Active nav state should be visually distinct

## Accessibility Essentials

- **Semantic HTML**: Use the right element (button for actions, a for navigation)
- **Keyboard navigation**: All interactive elements must be reachable via Tab
- **Focus indicators**: Never remove outline without replacing it (`focus-visible:ring-2`)
- **Alt text**: Descriptive for informational images, empty (`alt=""`) for decorative
- **Color alone**: Don't convey meaning through color only (add icons or text)
- **Motion**: Respect `prefers-reduced-motion` for animations
- **Skip link**: Add a "Skip to content" link as the first focusable element

```typescript
// Skip to content link
<a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:rounded focus:bg-primary focus:px-4 focus:py-2 focus:text-white">
  Skip to content
</a>
<main id="main">...</main>
```

## Animation & Motion

- Use subtle animations for polish — don't overdo it
- Fade-in on scroll for sections: `opacity-0 → opacity-100` with small `translateY`
- Hover effects on cards and buttons: scale or shadow change
- Keep transitions under 300ms for responsiveness
- Use `framer-motion` for complex animations, CSS transitions for simple ones
- Always respect `prefers-reduced-motion`

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```
