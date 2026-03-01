#!/usr/bin/env python3
"""Scan an existing NextJS App Router project and generate state + image manifest.

Discovers pages/routes, detects images (real vs placeholder), checks for missing
metadata, and generates or updates both the state file and image manifest.

Usage:
    python scan_project.py [--project-dir .] [--output .nextjs-builder-state.json]
                           [--manifest image-manifest.json] [--accent-color "#2563eb"]
                           [--font modern]

Options:
    --project-dir   Path to the NextJS project root (default: .)
    --output        State file output path (default: .nextjs-builder-state.json)
    --manifest      Image manifest output path (default: image-manifest.json)
    --accent-color  Brand accent color for placeholders (default: #2563eb)
    --font          Font preference for manifest entries (default: modern)
    --json          Output report as JSON instead of human-readable
"""

import argparse
import glob
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def scan_pages(project_dir: str) -> list:
    """Find all page.tsx/page.jsx files in the App Router."""
    pages = []
    app_dir = None

    # Find the app directory (could be src/app or app)
    for candidate in ["src/app", "app"]:
        full = os.path.join(project_dir, candidate)
        if os.path.isdir(full):
            app_dir = full
            break

    if not app_dir:
        print(
            "WARNING: No app/ or src/app/ directory found. Is this a NextJS App Router project?"
        )
        return pages

    # Walk the app directory for page files
    for root, dirs, files in os.walk(app_dir):
        # Skip special directories
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith("_") and not d.startswith(".") and d != "api"
        ]

        for f in files:
            if f in ("page.tsx", "page.jsx", "page.js", "page.ts"):
                file_path = os.path.join(root, f)
                # Derive route from directory path relative to app_dir
                rel_dir = os.path.relpath(root, app_dir)
                if rel_dir == ".":
                    route = "/"
                else:
                    # Handle dynamic routes: [slug] stays as-is
                    route = "/" + rel_dir.replace(os.sep, "/")

                page_id = route.strip("/").replace("/", "-") or "home"

                # Extract metadata from the file
                metadata = extract_metadata(file_path)

                pages.append(
                    {
                        "id": page_id,
                        "route": route,
                        "file_path": file_path,
                        "title": metadata.get("title", ""),
                        "meta_description": metadata.get("description", ""),
                        "h1": metadata.get("h1", ""),
                        "has_metadata_export": metadata.get("has_metadata", False),
                        "has_structured_data": metadata.get("has_json_ld", False),
                        "image_refs": metadata.get("image_refs", []),
                        "status": "pending",  # Will be updated below
                    }
                )

    return pages


def extract_metadata(file_path: str) -> dict:
    """Parse a page file to extract SEO metadata and image references."""
    result = {
        "has_metadata": False,
        "has_json_ld": False,
        "title": "",
        "description": "",
        "h1": "",
        "image_refs": [],
    }

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return result

    # Check for metadata export
    if (
        "export const metadata" in content
        or "export async function generateMetadata" in content
    ):
        result["has_metadata"] = True

    # Try to extract title from metadata
    title_match = re.search(r"title:\s*['\"]([^'\"]+)['\"]", content)
    if title_match:
        result["title"] = title_match.group(1)

    # Try to extract description
    desc_match = re.search(r"description:\s*['\"]([^'\"]+)['\"]", content)
    if desc_match:
        result["description"] = desc_match.group(1)

    # Check for JSON-LD
    if "application/ld+json" in content:
        result["has_json_ld"] = True

    # Find h1 elements
    h1_match = re.search(r"<h1[^>]*>([^<]+)</h1>", content)
    if h1_match:
        result["h1"] = h1_match.group(1).strip()

    # Find image references (next/image, img tags, background images)
    img_refs = re.findall(r'src=["\']([^"\']+)["\']', content)
    for ref in img_refs:
        if any(
            ref.endswith(ext)
            for ext in (".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".avif")
        ):
            result["image_refs"].append(ref)
        elif "/images/" in ref or "/og/" in ref or "/placeholder" in ref:
            result["image_refs"].append(ref)

    return result


def scan_images(project_dir: str, pages: list) -> list:
    """Scan the public directory for images and detect placeholders."""
    images = []
    public_dir = os.path.join(project_dir, "public")

    if not os.path.isdir(public_dir):
        return images

    image_extensions = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".avif"}

    for root, dirs, files in os.walk(public_dir):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in image_extensions:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, public_dir)
                web_path = "/" + rel_path.replace(os.sep, "/")

                is_placeholder = (
                    "placeholder" in rel_path.lower()
                    or is_placeholder_svg(full_path)
                )

                images.append(
                    {
                        "path": full_path,
                        "web_path": web_path,
                        "is_placeholder": is_placeholder,
                        "size_bytes": os.path.getsize(full_path),
                        "extension": ext,
                    }
                )

    return images


def is_placeholder_svg(file_path: str) -> bool:
    """Check if an SVG file looks like a placeholder."""
    if not file_path.lower().endswith(".svg"):
        return False
    try:
        with open(file_path, "r") as f:
            content = f.read(2000)
        placeholder_signals = ["placeholder", "lorem", "\u00d7", "TODO", "Replace"]
        return any(signal.lower() in content.lower() for signal in placeholder_signals)
    except Exception:
        return False


def detect_existing_state(project_dir: str, pages: list) -> list:
    """Assign statuses to pages based on what exists."""
    screenshots_dir = os.path.join(project_dir, "screenshots")

    for page in pages:
        # If there's a screenshot, mark as implemented
        if os.path.isdir(screenshots_dir):
            pattern = os.path.join(screenshots_dir, f"{page['id']}-*-full.png")
            if glob.glob(pattern):
                page["status"] = "implemented"

        # If the file has substantial content, mark as implemented
        try:
            with open(page["file_path"], "r") as f:
                content = f.read()
            if len(content) > 500:
                page["status"] = max_status(page["status"], "implemented")
        except Exception:
            pass

    return pages


def max_status(current: str, new: str) -> str:
    """Return the more advanced status."""
    order = ["pending", "in-progress", "implemented", "verified", "needs-review"]
    curr_idx = order.index(current) if current in order else 0
    new_idx = order.index(new) if new in order else 0
    return order[max(curr_idx, new_idx)]


def generate_state(
    project_dir: str, pages: list, accent_color: str, font: str
) -> dict:
    """Generate a state file from scanned pages."""
    project_name = "unknown"
    pkg_path = os.path.join(project_dir, "package.json")
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path) as f:
                pkg = json.load(f)
                project_name = pkg.get("name", "unknown")
        except Exception:
            pass

    state = {
        "version": "1.0.0",
        "project_name": project_name,
        "source_documents": [
            {"path": "scanned-from-existing-project", "type": "scan"}
        ],
        "created_at": now_iso(),
        "last_updated": now_iso(),
        "current_phase": "build",
        "scan_source": "brownfield",
        "design_inputs": {
            "accent_color": accent_color,
            "accent_color_source": "user" if accent_color != "#2563eb" else "default",
            "font_preference": font,
            "font_preference_source": "user" if font != "modern" else "default",
        },
        "plan": {
            "site_name": project_name,
            "build_order": [p["id"] for p in pages],
        },
        "pages": [
            {
                "id": p["id"],
                "route": p["route"],
                "title": p["title"],
                "meta_description": p["meta_description"],
                "h1": p["h1"],
                "target_keyword": "",
                "structured_data_type": "WebPage",
                "components": [],
                "content_source": p["file_path"],
                "status": p["status"],
                "priority": "high" if p["route"] == "/" else "medium",
                "iteration": 0,
                "screenshots": [],
                "verification_log": [],
                "seo_issues": [],
            }
            for p in pages
        ],
        "shared_components": [],
        "session_log": [
            {
                "session_id": "scan",
                "started_at": now_iso(),
                "ended_at": None,
                "actions": [f"Scanned existing project: found {len(pages)} pages"],
            }
        ],
        "issues": [],
        "image_manifest": {
            "path": "image-manifest.json",
            "total_images": 0,
            "generated": 0,
            "placeholders": 0,
            "failed": 0,
            "last_generated_at": None,
        },
        "audit": {
            "seo_passed": False,
            "accessibility_passed": False,
            "responsive_passed": False,
            "performance_passed": False,
            "completed_at": None,
        },
    }

    # Flag SEO issues found during scan
    for page_state, page_scan in zip(state["pages"], pages):
        issues = []
        if not page_scan.get("has_metadata_export"):
            issues.append("Missing metadata export")
        if not page_scan.get("h1"):
            issues.append("No <h1> found")
        if not page_scan.get("has_structured_data"):
            issues.append("No JSON-LD structured data")
        if not page_scan.get("meta_description"):
            issues.append("No meta description")
        page_state["seo_issues"] = issues
        if issues:
            state["issues"].append(
                {
                    "page_id": page_state["id"],
                    "severity": "minor",
                    "description": f"SEO: {'; '.join(issues)}",
                    "resolved": False,
                }
            )

    return state


def generate_manifest(
    project_dir: str, pages: list, images: list, accent_color: str, font: str
) -> dict:
    """Generate an image manifest from scanned images."""
    mood_map = {
        "modern": "professional, modern, trustworthy",
        "elegant": "sophisticated, elegant, refined",
        "bold": "bold, expressive, dynamic",
        "minimal": "clean, minimal, focused",
    }
    mood = mood_map.get(font, "professional, modern, trustworthy")

    font_map = {
        "modern": "Inter",
        "elegant": "Playfair Display",
        "bold": "Plus Jakarta Sans",
        "minimal": "Geist",
    }
    font_name = font_map.get(font, font)

    manifest = {
        "_schema_version": "1.0.0",
        "_description": "Image manifest generated by scan_project.py",
        "project_name": "",
        "accent_color": accent_color,
        "font_preference": font,
        "images": [],
    }

    # Find placeholder images that need generation
    for img in images:
        if img["is_placeholder"]:
            img_id = os.path.splitext(os.path.basename(img["path"]))[0]
            # Determine which page this belongs to
            page_id = "general"
            for page in pages:
                if any(
                    img["web_path"] in ref for ref in page.get("image_refs", [])
                ):
                    page_id = page["id"]
                    break

            manifest["images"].append(
                {
                    "id": img_id,
                    "path": os.path.relpath(img["path"], project_dir),
                    "placeholder": os.path.relpath(img["path"], project_dir),
                    "prompt": f"[NEEDS PROMPT] Image for {page_id} page — describe what this image should show",
                    "alt": f"[NEEDS ALT TEXT] {img_id}",
                    "context": f"Found as placeholder in {img['web_path']}",
                    "dimensions": {"width": 1200, "height": 630},
                    "aspect_ratio": "16:9",
                    "style": "photorealistic, professional",
                    "brand": {
                        "accent_color": accent_color,
                        "font": font_name,
                        "mood": mood,
                    },
                    "page_id": page_id,
                    "priority": "medium",
                    "status": "placeholder",
                    "generated_at": None,
                    "error": None,
                }
            )

    return manifest


def main():
    parser = argparse.ArgumentParser(
        description="Scan existing NextJS project and generate state + manifest"
    )
    parser.add_argument(
        "--project-dir", default=".", help="Project root directory"
    )
    parser.add_argument(
        "--output",
        default=".nextjs-builder-state.json",
        help="State file output path",
    )
    parser.add_argument(
        "--manifest",
        default="image-manifest.json",
        help="Image manifest output path",
    )
    parser.add_argument(
        "--accent-color", default="#2563eb", help="Brand accent color"
    )
    parser.add_argument(
        "--font", default="modern", help="Font preference"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output report as JSON"
    )
    args = parser.parse_args()

    print(f"=== Scanning project: {os.path.abspath(args.project_dir)} ===\n")

    # Scan
    pages = scan_pages(args.project_dir)
    pages = detect_existing_state(args.project_dir, pages)
    images = scan_images(args.project_dir, pages)

    # Report
    placeholder_images = [i for i in images if i["is_placeholder"]]
    real_images = [i for i in images if not i["is_placeholder"]]

    print(f"Pages found: {len(pages)}")
    for p in pages:
        seo_status = (
            "\u2713" if p.get("has_metadata_export") else "\u2717 (no metadata)"
        )
        print(
            f"  [{p['status']:12s}] {p['route']:20s} {seo_status}  {p.get('title', '(no title)')[:50]}"
        )

    print(f"\nImages found: {len(images)}")
    print(f"  Real images:       {len(real_images)}")
    print(f"  Placeholders:      {len(placeholder_images)}")

    # Generate outputs
    state = generate_state(
        args.project_dir, pages, args.accent_color, args.font
    )
    manifest = generate_manifest(
        args.project_dir, pages, images, args.accent_color, args.font
    )

    # Update image manifest stats in state
    state["image_manifest"]["total_images"] = len(manifest["images"])
    state["image_manifest"]["placeholders"] = len(
        [e for e in manifest["images"] if e["status"] == "placeholder"]
    )

    # Check for existing state file
    output_path = os.path.join(args.project_dir, args.output)
    if os.path.exists(output_path):
        print(f"\n\u26a0  Existing state file found at {output_path}")
        print(
            f"   Overwriting with scan results. Previous state backed up to {output_path}.bak"
        )
        shutil.copy2(output_path, output_path + ".bak")

    # Write state
    with open(output_path, "w") as f:
        json.dump(state, f, indent=2, default=str)
    print(f"\nState file written: {output_path}")

    # Write manifest
    manifest_path = os.path.join(args.project_dir, args.manifest)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    print(f"Image manifest written: {manifest_path}")

    # Summary
    issues = state.get("issues", [])
    if issues:
        print(f"\n\u26a0  {len(issues)} issues found:")
        for issue in issues:
            print(
                f"   [{issue['severity']}] {issue['page_id']}: {issue['description']}"
            )

    if placeholder_images:
        print(f"\n\U0001f4a1 {len(placeholder_images)} placeholder images found.")
        print(f"   Edit prompts in {manifest_path}, then run generate_images.py")

    if args.json:
        report = {
            "pages": len(pages),
            "images": len(images),
            "real_images": len(real_images),
            "placeholders": len(placeholder_images),
            "issues": len(issues),
            "state_file": output_path,
            "manifest_file": manifest_path,
        }
        print(f"\n{json.dumps(report, indent=2)}")

    print(
        f"\n\u2713 Scan complete. Review the state file and manifest, then proceed with targeted work."
    )


if __name__ == "__main__":
    main()
