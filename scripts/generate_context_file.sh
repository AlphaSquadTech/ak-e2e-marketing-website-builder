#!/usr/bin/env bash
# Generate a CLAUDE.md and/or GEMINI.md context file in the project root.
# This file is read by the AI on every turn, preventing verification amnesia.
#
# Usage: bash generate_context_file.sh [--project-dir .] [--skill-path .] [--format both]

set -euo pipefail

PROJECT_DIR="."
SKILL_PATH="$(dirname "$(realpath "$0")")/.."
FORMAT="both"

while [[ $# -gt 0 ]]; do
  case $1 in
    --project-dir) PROJECT_DIR="$2"; shift 2 ;;
    --skill-path) SKILL_PATH="$2"; shift 2 ;;
    --format) FORMAT="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# Resolve paths for the context file content
SKILL_ABS="$(realpath "$SKILL_PATH")"
STATE_FILE="${PROJECT_DIR}/.nextjs-builder-state.json"

# Detect project name
PROJECT_NAME="this project"
if [ -f "${PROJECT_DIR}/package.json" ]; then
  PROJECT_NAME=$(python3 -c "import json; print(json.load(open('${PROJECT_DIR}/package.json')).get('name', 'this project'))" 2>/dev/null || echo "this project")
fi

generate_content() {
  cat << CONTEXT_EOF
# Project: ${PROJECT_NAME}

This is a NextJS marketing website managed by the ak-e2e-marketing-website-builder skill.

## ⚠ MANDATORY: Visual Verification After Every Change

**YOU MUST visually verify every page after implementing or modifying it.**
This is not optional. Do not skip this step. Do not mark pages as complete without verification.

After writing or editing any page/component code:

\`\`\`bash
bash ${SKILL_ABS}/scripts/verify_page.sh <route> <page-id>
\`\`\`

Then READ every chunk image the script outputs and analyze:
- Layout correct? Elements aligned and spaced properly?
- Content visible? Text readable, not clipped or overflowing?
- Colors correct? Accent color and design system applied?
- CTAs prominent? Buttons visible and styled?
- No blank areas, broken images, or overlapping elements?

After analysis, record the result:
\`\`\`bash
python3 ${SKILL_ABS}/scripts/state_manager.py --action add-verification \\
  --page-id <page-id> --result pass|fail \\
  --screenshot screenshots/<page-id>-v<N>-full.png \\
  --notes "Your analysis summary"
\`\`\`

**The state manager will reject any attempt to mark a page as "verified" without
a verification log entry that includes a screenshot.** Do not try to bypass this.

## Workflow Quick Reference

**Check project status:**
\`\`\`bash
python3 ${SKILL_ABS}/scripts/state_manager.py --action summary
\`\`\`

**Get next page to work on:**
\`\`\`bash
python3 ${SKILL_ABS}/scripts/state_manager.py --action next-page
\`\`\`

**Verify a page (one command):**
\`\`\`bash
bash ${SKILL_ABS}/scripts/verify_page.sh / home
bash ${SKILL_ABS}/scripts/verify_page.sh /features features
bash ${SKILL_ABS}/scripts/verify_page.sh /features features --viewport mobile
\`\`\`

**Generate placeholder images:**
\`\`\`bash
python3 ${SKILL_ABS}/scripts/generate_placeholders.py
\`\`\`

**Generate real images (API key is saved in state file under design_inputs.gemini_api_key):**
\`\`\`bash
export GEMINI_API_KEY="\$(python3 -c "import json; print(json.load(open('.nextjs-builder-state.json'))['design_inputs'].get('gemini_api_key',''))")"
python3 ${SKILL_ABS}/scripts/generate_images.py --dry-run
python3 ${SKILL_ABS}/scripts/generate_images.py
\`\`\`

**Scan existing project (brownfield):**
\`\`\`bash
python3 ${SKILL_ABS}/scripts/scan_project.py --project-dir .
\`\`\`

## Build Cycle (for every page)

1. Implement the page code
2. Generate placeholders if new images were added
3. **Run verify_page.sh** ← DO NOT SKIP
4. **Read and analyze every chunk** ← DO NOT SKIP
5. Fix issues found → re-run verify_page.sh (up to 3 iterations)
6. Record verification result in state manager
7. Move to next page

## Key Files

- \`.nextjs-builder-state.json\` — Build progress (source of truth)
- \`image-manifest.json\` — Image generation manifest
- \`screenshots/\` — Verification screenshots
CONTEXT_EOF
}

if [ "$FORMAT" = "claude" ] || [ "$FORMAT" = "both" ]; then
  generate_content > "${PROJECT_DIR}/CLAUDE.md"
  echo "Generated: ${PROJECT_DIR}/CLAUDE.md"
fi

if [ "$FORMAT" = "gemini" ] || [ "$FORMAT" = "both" ]; then
  generate_content > "${PROJECT_DIR}/GEMINI.md"
  echo "Generated: ${PROJECT_DIR}/GEMINI.md"
fi
