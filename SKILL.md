---
name: ak-e2e-marketing-website-builder
description: >-
  Build end-to-end marketing websites with best SEO practices from documents (MD, DOCX, PDF,
  OpenAPI specs, etc.) using NextJS. Use when the user wants to create a marketing site,
  landing page, product page, documentation site, or any public-facing website from a
  document or spec. Also trigger when the user mentions "build a website from this doc",
  "create a marketing site", "turn this into a landing page", "make a site from this spec",
  "SEO-optimized website", or wants to convert any document into a working, deployed website.
  The skill works autonomously — it reads the document, plans the site, builds it, and
  visually verifies every page via browser screenshots analyzed by Claude's vision.
  All progress is tracked in a session-agnostic state file so work survives session interruptions.
---

# E2E Marketing Website Builder

Autonomously build production-quality, SEO-optimized marketing websites from documents.
Feed it a Markdown file, Word doc, PDF, OpenAPI spec, or any text document, and it will
plan, scaffold, implement, and visually verify a complete NextJS marketing site.

The skill operates with minimal human intervention — it reads the source document,
generates a site plan, builds every page, takes screenshots to verify its work, and
fixes issues it finds. Progress is persisted so the build can resume across sessions.

## Preflight (Run First — Every Time)

Before doing ANY work, run the preflight script. It installs companion skills,
checks system dependencies (Node, Python, Pillow, agent-browser), and detects
whether this is a fresh start or a resume:

```bash
bash <skill-path>/scripts/preflight.sh
```

This is idempotent — safe to re-run. It will:
1. Install `vercel-react-best-practices`, `web-design-guidelines`, and `agent-browser` skills
2. Install Pillow for screenshot resizing
3. Verify Node.js 18+, npm, Python 3 are available
4. Check for an existing `.nextjs-builder-state.json` (resume detection)

If any companion skill fails to install (e.g., no internet), the skill falls back to
bundled patterns in [references/react-patterns.md](references/react-patterns.md) and
[references/design-guidelines.md](references/design-guidelines.md).

## Quick Start

### Resuming a Previous Session

After preflight, check its output. If it reports an existing state file, read it
to understand current progress and resume from the first incomplete item.
See [references/state-schema.md](references/state-schema.md).

### Starting Fresh

**STOP — Before doing anything else, you MUST ask the user for their design preferences.**
Do not skip this step. Do not pick defaults silently. Always ask, even if the user's
initial prompt doesn't mention design. If they say "pick for me" or don't care, THEN
you may choose defaults based on the document's subject matter.

Ask for exactly these three inputs (nothing more — everything else is derived automatically):

1. **Accent color** — A single brand/accent color (hex code, color name, or "pick for me").
   This drives the entire palette: primary buttons, links, highlights. The rest of the
   color system (background, text, muted, secondary) is generated automatically to
   complement this choice.

2. **Font preference** — One of: "modern" (Inter/DM Sans), "elegant" (Playfair Display + Inter),
   "bold" (Plus Jakarta Sans), "minimal" (Geist), or a specific Google Font name.
   A single font or pair is selected; all sizing/weights are handled automatically.

3. **Gemini API key** — Required for AI image generation in Phase 2.5. Ask the user for their
   `GEMINI_API_KEY` (or `GOOGLE_API_KEY`). If they don't have one, point them to
   https://aistudio.google.com/apikey to get a free key. If they want to skip image
   generation, that's fine — the site will use branded SVG placeholders and still look good.

If the user already provided these in their initial message, skip asking and use the
provided values directly. If they say "pick for me" or express no preference for colors/fonts,
choose sensible defaults based on the document's subject matter:
- SaaS/tech → `#2563eb` (blue) + modern
- Finance → `#0f172a` (dark navy) + modern
- Creative/agency → `#7c3aed` (purple) + bold
- Luxury/premium → `#18181b` (near-black) + elegant
- Health/wellness → `#059669` (green) + minimal
- Education → `#2563eb` (blue) + minimal

Save these preferences in the state file under `design_inputs` and use them to generate
the full design system in Phase 1. The accent color and font flow into image manifest entries
(`brand.accent_color`, `brand.font`) so AI-generated images match the site's identity.
The API key is saved so it can be exported automatically before running `generate_images.py`
in Phase 2.5 — no need to ask the user again in later sessions.

### Existing Project (Brownfield)

To use this skill on an existing NextJS project:

1. **STOP — Ask for design inputs first** (same rule as fresh projects):
   - **Accent color**: Ask the user. If they already provided one, use it. If they say
     "pick for me", try to detect from the project's Tailwind/CSS config, or fall back
     to subject-matter defaults.
   - **Font preference**: Ask the user. Same logic — use provided, detect, or default.
   - **Gemini API key**: Ask the user for their `GEMINI_API_KEY`. If they don't have one,
     point them to https://aistudio.google.com/apikey. If they want to skip, that's fine.

2. **Scan the project** (pass the design inputs as flags):
   ```bash
   python <skill-path>/scripts/scan_project.py --project-dir . \
     --accent-color "<user's color>" --font "<user's font>"
   ```
   This discovers all pages, detects placeholder images, flags SEO issues, and generates
   both a state file and an image manifest with the correct brand context.

3. **Review the scan output.** Check `.nextjs-builder-state.json` for the list of pages
   and issues found. Check `image-manifest.json` for placeholder images that need prompts.

4. **Generate context files** (critical for verification enforcement):
   ```bash
   bash <skill-path>/scripts/generate_context_file.sh --project-dir .
   ```
   This creates `CLAUDE.md` and `GEMINI.md` in the project root.

5. **Work on specific pages.** Use the state manager to find what needs work:
   ```bash
   python <skill-path>/scripts/state_manager.py --action summary
   python <skill-path>/scripts/state_manager.py --action next-page
   ```

5. **Verify after every change:**
   ```bash
   bash <skill-path>/scripts/verify_page.sh <route> <page-id>
   ```

The skill's phases (Plan, Scaffold, Build, Images, Audit) can each be invoked
independently on a brownfield project — you don't have to run the full pipeline.

### Build Phases

| Phase | Name | Description |
|-------|------|-------------|
| 0 | **Plan** | Parse source document(s), extract content, generate site plan with SEO strategy |
| 1 | **Scaffold** | Initialize NextJS project, generate full design system from user's accent color + font |
| 2 | **Build** | Implement pages autonomously with visual verification after each page |
| 2.5 | **Images** | Generate real images via Gemini API from the image manifest |
| 3 | **Audit** | Full-site visual pass, SEO audit, accessibility check, responsive verification |

For detailed instructions: [references/workflow-phases.md](references/workflow-phases.md)

## Core Principles

1. **Document-first.** The source document is the content authority. Extract all copy,
   structure, and messaging from it. Don't invent content — reorganize and present it
   effectively for the web.

2. **SEO from the start.** Every decision — URL structure, heading hierarchy, metadata,
   image alt text, semantic HTML, structured data — is made with search engines in mind.
   See [references/seo-patterns.md](references/seo-patterns.md).

3. **Verify visually, autonomously.** After implementing each page, take a screenshot and
   analyze it. Fix issues without asking the user. Only escalate if stuck after 3 attempts.
   See [references/visual-verification.md](references/visual-verification.md).

4. **Track everything.** Update `.nextjs-builder-state.json` after every meaningful action.
   This is the source of truth. Use:
   ```bash
   python <skill-path>/scripts/state_manager.py --action update-page --page-id home --status verified
   ```

5. **Ship quality.** Follow React/Next.js best practices, use semantic HTML, ensure
   accessibility, optimize for Core Web Vitals. The output should be deploy-ready.

6. **Verify or it didn't happen.** The state manager enforces that pages cannot be
   marked `verified` without a passing verification entry that includes a screenshot.
   Use `verify_page.sh` to run the full verification pipeline in one command. The
   generated `CLAUDE.md`/`GEMINI.md` file repeats this rule on every turn.

## Document Processing

The skill handles multiple input formats:

| Format | How it's processed |
|--------|--------------------|
| **Markdown (.md)** | Read directly. Headings become page/section structure. |
| **Word (.docx)** | Extract text and structure. Preserve heading hierarchy. |
| **PDF (.pdf)** | Extract text. Use vision to understand layout if text extraction is poor. |
| **OpenAPI (.yaml/.json)** | Generate API documentation pages with endpoint details, request/response examples. |
| **Multiple files** | Combine into a unified site plan. Each major document may become a page or section. |

## Environment Support

**Claude Code**: Full support. Use bash, agent-browser for screenshots, Read tool for vision.

**Cowork**: Full support. Same workflow. Save screenshots to project directory for persistence.

## Image Generation

Claude cannot generate images. The skill uses a two-stage image pipeline:

1. **During Build (Phase 2)**: Every `<Image>` component gets a branded SVG placeholder
   and a corresponding entry in `image-manifest.json` with a descriptive prompt.
   Placeholders use the accent color so the site looks intentional, not broken.

2. **After Build (Phase 2.5)**: A Python script calls the Gemini API via the `google-genai`
   SDK to generate real images from the manifest prompts using the
   `gemini-3.1-flash-image-preview` model. Requires a `GEMINI_API_KEY`.
   Cost: ~$0.50–$1.50 for a typical site.

```bash
# Generate branded placeholders (run during Phase 2, after adding manifest entries)
python <skill-path>/scripts/generate_placeholders.py

# Preview what will be generated (dry run)
python <skill-path>/scripts/generate_images.py --dry-run

# Generate real images via Gemini API (key is saved in state file's design_inputs)
export GEMINI_API_KEY="$(python3 -c "import json; print(json.load(open('.nextjs-builder-state.json'))['design_inputs'].get('gemini_api_key',''))")"
python <skill-path>/scripts/generate_images.py

# Apply a specific visual style to all images
python <skill-path>/scripts/generate_images.py --style photorealistic
```

See [references/image-generation.md](references/image-generation.md) for the full guide.

## File Reference

| Path | Purpose | When to read |
|------|---------|--------------|
| [references/workflow-phases.md](references/workflow-phases.md) | Detailed phase instructions | Starting each phase |
| [references/visual-verification.md](references/visual-verification.md) | Screenshot + vision verification | Before verifying any page |
| [references/seo-patterns.md](references/seo-patterns.md) | SEO best practices for NextJS | During implementation |
| [references/react-patterns.md](references/react-patterns.md) | Essential React/Next.js patterns | When implementing components |
| [references/design-guidelines.md](references/design-guidelines.md) | Marketing design + UX rules | When implementing UI |
| [references/state-schema.md](references/state-schema.md) | State file format | When reading/updating state |
| [scripts/preflight.sh](scripts/preflight.sh) | Install skills + check dependencies | **Always run first** |
| [scripts/resize_screenshot.py](scripts/resize_screenshot.py) | Resize images for vision | During visual verification |
| [scripts/init_project.sh](scripts/init_project.sh) | NextJS project scaffolding | Phase 1 only |
| [scripts/state_manager.py](scripts/state_manager.py) | Read/update state file | Throughout all phases |
| [scripts/verify_page.sh](scripts/verify_page.sh) | One-command visual verification | After every page change |
| [scripts/scan_project.py](scripts/scan_project.py) | Scan existing project for brownfield entry | Brownfield projects |
| [scripts/generate_context_file.sh](scripts/generate_context_file.sh) | Generate CLAUDE.md/GEMINI.md | Phase 1 or brownfield scan |
| [references/image-generation.md](references/image-generation.md) | Image placeholder + AI generation guide | During Phase 2 and 2.5 |
| [scripts/generate_placeholders.py](scripts/generate_placeholders.py) | Generate branded SVG placeholders | Phase 2 (after adding manifest entries) |
| [scripts/generate_images.py](scripts/generate_images.py) | Generate real images via Gemini API | Phase 2.5 |
| [templates/image-manifest.json](templates/image-manifest.json) | Image manifest schema + examples | Phase 2 (first image reference) |
| [templates/project-plan.json](templates/project-plan.json) | Plan structure template | Phase 0 only |
| [templates/state-tracker.json](templates/state-tracker.json) | Initial state file template | Phase 1 only |
