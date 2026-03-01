# State Tracking Schema

The state file (`.nextjs-builder-state.json`) lives in the project root and tracks all progress.
It is the single source of truth for what has been done and what remains. Always read it at the
start of a session and update it after every meaningful action.

## Complete Schema

```json
{
  "version": "1.0.0",
  "project_name": "my-marketing-site",
  "source_documents": [
    {
      "path": "requirements.md",
      "type": "markdown",
      "extracted_at": "2026-02-28T10:00:00Z"
    }
  ],
  "created_at": "2026-02-28T10:00:00Z",
  "last_updated": "2026-02-28T14:30:00Z",
  "current_phase": "build",
  "design_inputs": {
    "accent_color": "#2563eb",
    "accent_color_source": "user",
    "font_preference": "modern",
    "font_preference_source": "user",
    "gemini_api_key": "AIza...",
    "gemini_api_key_source": "user"
  },
  "plan": {
    "site_name": "Acme Corp",
    "site_description": "Next-generation widget platform",
    "target_audience": "SaaS founders and product teams",
    "design_system": {
      "primary": "#2563eb",
      "primary_foreground": "#ffffff",
      "secondary": "#93a3d1",
      "background": "#ffffff",
      "foreground": "#0a0a0a",
      "muted": "#6b7280",
      "muted_background": "#f3f4f6",
      "border": "#e5e7eb",
      "destructive": "#ef4444",
      "font_heading": "Inter",
      "font_body": "Inter",
      "border_radius": "0.5rem",
      "derived_from": "accent_color=#2563eb, font_preference=modern"
    },
    "seo_strategy": {
      "primary_keyword": "widget platform",
      "secondary_keywords": ["SaaS tools", "product analytics", "dashboard builder"],
      "target_locale": "en_US"
    },
    "build_order": ["layout", "home", "features", "pricing", "about", "contact"]
  },
  "pages": [
    {
      "id": "home",
      "route": "/",
      "title": "Acme — The Fastest Widget Platform",
      "meta_description": "Build and deploy widgets 10x faster with Acme's no-code platform.",
      "h1": "Build Widgets 10x Faster",
      "target_keyword": "widget platform",
      "structured_data_type": "WebSite",
      "components": ["Hero", "FeatureGrid", "Testimonials", "CTABanner"],
      "content_source": "requirements.md#introduction",
      "status": "verified",
      "priority": "high",
      "iteration": 2,
      "screenshots": [
        "screenshots/home-v1.png",
        "screenshots/home-v2.png"
      ],
      "verification_log": [
        {
          "timestamp": "2026-02-28T11:30:00Z",
          "iteration": 1,
          "result": "fail",
          "screenshot": "screenshots/home-v1.png",
          "notes": "Hero section CTA button not visible. Footer overlapping content."
        },
        {
          "timestamp": "2026-02-28T12:00:00Z",
          "iteration": 2,
          "result": "pass",
          "screenshot": "screenshots/home-v2.png",
          "notes": "Layout correct. CTA prominent. Footer fixed."
        }
      ]
    },
    {
      "id": "features",
      "route": "/features",
      "title": "Features — Acme",
      "meta_description": "Explore Acme's powerful widget building features.",
      "h1": "Powerful Features for Every Team",
      "target_keyword": "widget builder features",
      "structured_data_type": "WebPage",
      "components": ["FeatureHero", "FeatureDetail", "ComparisonTable"],
      "content_source": "requirements.md#features",
      "status": "in-progress",
      "priority": "high",
      "iteration": 0,
      "screenshots": [],
      "verification_log": []
    }
  ],
  "shared_components": [
    {
      "name": "Header",
      "status": "verified",
      "file": "components/header.tsx"
    },
    {
      "name": "Footer",
      "status": "verified",
      "file": "components/footer.tsx"
    }
  ],
  "session_log": [
    {
      "session_id": "abc123",
      "started_at": "2026-02-28T10:00:00Z",
      "ended_at": "2026-02-28T12:30:00Z",
      "actions": [
        "Parsed requirements.md",
        "Generated plan",
        "Scaffolded project",
        "Implemented and verified home page"
      ]
    },
    {
      "session_id": "def456",
      "started_at": "2026-02-28T14:00:00Z",
      "ended_at": null,
      "actions": [
        "Resumed from state file",
        "Started implementing features page"
      ]
    }
  ],
  "issues": [
    {
      "page_id": "home",
      "severity": "minor",
      "description": "Slight spacing inconsistency in testimonials on mobile",
      "resolved": false
    }
  ],
  "image_manifest": {
    "path": "image-manifest.json",
    "total_images": 12,
    "generated": 8,
    "placeholders": 3,
    "failed": 1,
    "last_generated_at": "2026-02-28T15:30:00Z"
  },
  "audit": {
    "seo_passed": false,
    "accessibility_passed": false,
    "responsive_passed": false,
    "performance_passed": false,
    "completed_at": null
  }
}
```

## Status Values

### Page Status
| Status | Meaning |
|--------|---------|
| `pending` | Not yet started |
| `in-progress` | Currently being implemented |
| `implemented` | Code written but not yet visually verified |
| `verified` | Visually verified and passes all checks |
| `needs-review` | Failed verification after 3 attempts — needs human input |
| `failed` | Build error or critical issue preventing implementation |

### Phase Values
| Phase | Meaning |
|-------|---------|
| `plan` | Analyzing documents and generating plan |
| `scaffold` | Setting up the NextJS project |
| `build` | Implementing pages iteratively |
| `images` | Generating real images from manifest via Gemini API |
| `audit` | Final site-wide checks |
| `complete` | All pages verified, audit passed |

## State Manager Commands

The `scripts/state_manager.py` script provides these operations:

```bash
# Initialize state from plan
python state_manager.py --action init --plan project-plan.json --output .nextjs-builder-state.json

# Set current phase
python state_manager.py --action set-phase --phase build

# Update page status
python state_manager.py --action update-page --page-id home --status verified

# Add verification entry
python state_manager.py --action add-verification \
  --page-id home \
  --result pass \
  --screenshot screenshots/home-v2.png \
  --notes "Layout correct. CTA visible."

# Log a session action
python state_manager.py --action log --message "Implemented features page"

# Add an issue
python state_manager.py --action add-issue \
  --page-id home \
  --severity minor \
  --description "Spacing issue on mobile"

# Get next pending page
python state_manager.py --action next-page

# Print status summary
python state_manager.py --action summary
```

## Reading State at Session Start

When resuming, follow this procedure:

1. Read `.nextjs-builder-state.json`
2. Check `current_phase` to understand where things are
3. If phase is `build`, find the first page with status `pending` or `in-progress`
4. If phase is `audit`, run the remaining audit checks
5. Check `issues` array for unresolved problems
6. Log the new session in `session_log`

```bash
python <skill-path>/scripts/state_manager.py --action summary
```

This prints a concise status overview so you can immediately understand the project state.
