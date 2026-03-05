# E2E Marketing Website Builder

A Claude Code skill that autonomously builds production-quality, SEO-optimized marketing websites from documents. Feed it a Markdown file, Word doc, PDF, or OpenAPI spec, and it will plan, scaffold, implement, and visually verify a complete NextJS site — with minimal human intervention.

## What It Does

This skill turns documents into deploy-ready marketing websites. It reads your source material, generates a site plan, builds every page using NextJS (App Router), takes screenshots to verify its work, and fixes issues it finds. Progress is tracked in a session-agnostic state file so builds survive session interruptions.

The full pipeline:

1. **Document Analysis** — Parses MD, DOCX, PDF, or OpenAPI specs to extract content, structure, and messaging
2. **Site Planning** — Maps content to a website structure with SEO strategy (keywords, meta tags, structured data)
3. **Scaffolding** — Initializes a NextJS project with a design system derived from user's accent color and font choice
4. **Autonomous Build** — Implements each page with semantic HTML, metadata, structured data, and image placeholders
5. **Visual Verification** — Screenshots every page and analyzes them via vision to catch layout/content issues
6. **Image Generation** — Replaces SVG placeholders with AI-generated images via Google's Gemini API
7. **Final Audit** — Full-site pass covering SEO, accessibility, responsive design, and performance

## Key Features

- **Document-first**: All content comes from source documents — nothing is fabricated
- **SEO built-in**: Every page gets optimized metadata, structured data (JSON-LD), semantic HTML, sitemap, and robots.txt
- **Visual verification**: Screenshots + vision analysis after every page, enforced by the state manager
- **Session-resilient**: A JSON state file tracks all progress so work resumes cleanly across sessions
- **Two-stage image pipeline**: Branded SVG placeholders during build, real AI images via Gemini API after
- **Brownfield support**: Can scan and enhance existing NextJS projects, not just greenfield builds
- **Design system from two inputs**: A single accent color and font choice generate the entire palette, typography, and component styling

## Requirements

- **Claude Code** or **Cowork** (the skill runs inside either environment)
- **Node.js 18+** and npm
- **Python 3** with pip
- **agent-browser** skill (installed automatically by preflight)
- **Gemini API key** (optional — for AI image generation; free at [aistudio.google.com/apikey](https://aistudio.google.com/apikey))

## Installation

Install the skill in Claude Code:

```bash
claude install-skill /path/to/ak-e2e-marketing-website-builder
```

Or clone and reference directly:

```bash
git clone https://github.com/alphasquadtech/ak-e2e-marketing-website-builder.git
```

## Usage

### Greenfield: Build a Site From a Document

Prompt Claude with something like:

```
Build a marketing website from this document: requirements.md
```

The skill will:

1. Run preflight checks (installs dependencies, companion skills)
2. Ask for your **accent color**, **font preference**, and **Gemini API key**
3. Parse the document and generate a site plan
4. Scaffold a NextJS project with your design system
5. Build each page, verifying with screenshots after each one
6. Generate real images from the Gemini API (or keep placeholders if no key)
7. Run a final audit

You can also be specific:

```
Turn this OpenAPI spec into a developer documentation site. Use #7c3aed as the accent
color and the "bold" font preset. Here's my Gemini key: AIza...
```

### Brownfield: Enhance an Existing NextJS Project

Prompt Claude inside an existing project directory:

```
Use the e2e-marketing-website-builder skill to improve SEO and replace placeholder
images in this project.
```

The skill will:

1. Ask for your design inputs (accent color, font, API key)
2. Scan the project to discover pages, detect placeholders, and flag SEO issues
3. Generate a state file and image manifest from what it finds
4. Let you target specific improvements — add pages, fix SEO, generate images, or run a full audit

Example of targeted work:

```
Scan this NextJS project and fix all the SEO issues it finds. Then generate real images
for any placeholders. Accent color is #059669, font is minimal.
```

### Resume a Previous Build

If a build was interrupted, just invoke the skill again in the same project directory. It detects the existing `.nextjs-builder-state.json` and picks up where it left off.

```
Continue building the marketing site.
```

## How It Works

### Design System Generation

You provide two inputs — an accent color and a font preference. The skill derives everything else automatically:

| Input | Example | What it generates |
|-------|---------|-------------------|
| Accent color | `#2563eb` | Primary, secondary, muted, border, background, foreground, destructive colors |
| Font preference | `modern` | Heading + body fonts, CSS variables, Tailwind config, `next/font` imports |

### Image Pipeline

Since Claude can't generate images, the skill uses a two-stage approach:

1. **During build**: Every `<Image>` component gets a branded SVG placeholder (uses your accent color) and a manifest entry with a descriptive prompt
2. **After build**: `generate_images.py` calls the Gemini API to produce real images from those prompts, supporting 10 visual styles and 10 aspect ratios

Supported styles: photorealistic, watercolor, oil-painting, sketch, pixel-art, anime, vintage, modern, abstract, minimalist.

### State Tracking

The `.nextjs-builder-state.json` file tracks:

- Current phase (plan → scaffold → build → images → audit → complete)
- Per-page status with verification logs and screenshots
- Design inputs (accent color, font, API key) that persist across sessions
- Issues found during verification
- Session history for debugging

The state manager enforces that pages **cannot be marked as verified** without a passing verification entry that includes a screenshot path.

## Project Structure

```
ak-e2e-marketing-website-builder/
├── SKILL.md                          # Main entry point — Claude reads this first
├── references/
│   ├── workflow-phases.md            # Detailed instructions for each build phase
│   ├── visual-verification.md       # Screenshot + vision verification guide
│   ├── image-generation.md          # Image placeholder + AI generation guide
│   ├── seo-patterns.md              # SEO best practices for NextJS
│   ├── react-patterns.md            # React/Next.js component patterns
│   ├── design-guidelines.md         # Marketing design + UX rules
│   └── state-schema.md              # State file format documentation
├── scripts/
│   ├── preflight.sh                 # Dependency + companion skill installer
│   ├── init_project.sh              # NextJS project scaffolding
│   ├── state_manager.py             # Read/update the state file
│   ├── verify_page.sh               # One-command visual verification
│   ├── resize_screenshot.py         # Resize images for vision analysis
│   ├── generate_placeholders.py     # Branded SVG placeholder generator
│   ├── generate_images.py           # AI image generation via Gemini API
│   ├── generate_context_file.sh     # Generate CLAUDE.md/GEMINI.md context files
│   └── scan_project.py              # Brownfield project scanner
└── templates/
    ├── project-plan.json             # Site plan structure template
    ├── state-tracker.json            # Initial state file template
    └── image-manifest.json           # Image manifest schema + examples
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | For image generation | Gemini API key. Saved in state file after first use. Get one free at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| `GOOGLE_API_KEY` | Alternative | Works as a fallback if `GEMINI_API_KEY` isn't set |
| `IMAGE_MODEL` | No | Override the Gemini model (default: `gemini-3.1-flash-image-preview`) |

## License

MIT
