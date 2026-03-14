# CLAUDE.md — Agent Skills Repository Guide

This file provides guidance for AI assistants working in this codebase.

## Repository Overview

This is **Anthropic's official Agent Skills repository** — a collection of reusable instruction sets that teach Claude how to complete specialized tasks. Skills are installed as Claude Code plugins and used across Claude.ai, Claude Code, and the Claude API.

- **Specification**: https://agentskills.io/specification
- **Plugin marketplace**: Defined in `.claude-plugin/marketplace.json`
- **License**: Mix of Apache 2.0 (example skills) and proprietary (document processing skills)

## Repository Structure

```
/
├── .claude-plugin/
│   └── marketplace.json        # Defines 3 plugin bundles: document-skills, example-skills, claude-api
├── spec/
│   └── agent-skills-spec.md    # Links to external specification
├── template/
│   └── SKILL.md                # Minimal starter template for new skills
├── skills/                     # 18 individual skill folders (see below)
├── README.md
└── THIRD_PARTY_NOTICES.md
```

## Skills Inventory

### Document Processing (Source-Available)
| Skill | Purpose |
|-------|---------|
| `docx` | Word document creation, editing, XML manipulation via pandoc/LibreOffice |
| `pdf` | PDF extraction, form handling, text/image processing |
| `pptx` | PowerPoint creation via python-pptx and PptxGenJS |
| `xlsx` | Excel spreadsheet creation and manipulation |

### Technical / Development
| Skill | Purpose |
|-------|---------|
| `claude-api` | Multi-language Claude API/SDK guide (Python, TS, Java, Go, Ruby, C#, PHP, cURL) |
| `mcp-builder` | Creating MCP servers in Python (FastMCP) and TypeScript |
| `skill-creator` | Iterative skill creation and evaluation framework |
| `webapp-testing` | Playwright-based web app testing |
| `web-artifacts-builder` | React + TypeScript + Tailwind + shadcn/ui artifact creation |

### Creative / Design
| Skill | Purpose |
|-------|---------|
| `algorithmic-art` | Generative art with JavaScript templates |
| `brand-guidelines` | Anthropic brand colors, typography, design system |
| `canvas-design` | Visual art and PDF/PNG design generation |
| `slack-gif-creator` | Animated GIF creation (PIL-based, optimized for Slack) |
| `theme-factory` | Theme creation system |

### Enterprise / Communications
| Skill | Purpose |
|-------|---------|
| `doc-coauthoring` | Document collaboration patterns |
| `frontend-design` | Frontend UI/UX design guidance |
| `internal-comms` | Internal communications templates (newsletters, FAQs) |

## Skill File Structure

Every skill follows this layout:

```
skill-name/
├── SKILL.md                    # Required: YAML frontmatter + instructions
├── LICENSE.txt                 # Apache 2.0 or Proprietary
├── scripts/                    # Optional: executable helper scripts
│   ├── *.py / *.sh
│   └── __init__.py
├── references/                 # Optional: large reference documentation
│   └── *.md
├── examples/                   # Optional: working code examples
│   └── *.py / *.js / *.html
├── assets/                     # Optional: fonts, templates, PDFs
└── core/                       # Optional: library code for complex skills
    ├── *.py
    └── __init__.py
```

### SKILL.md Frontmatter Convention

```yaml
---
name: kebab-case-identifier
description: "Clear trigger context: when to activate, what it does. Be explicit and specific."
license: Apache 2.0               # or: Proprietary / Complete terms in LICENSE.txt
compatibility: optional-tool-list # e.g. computer_use, bash
---
```

## Key Conventions

### SKILL.md Authoring
- **Keep SKILL.md under ~500 lines** — move large content to `references/` files and `@`-reference them
- **Reference files >300 lines must include a Table of Contents**
- **Description must be explicit** about when to trigger the skill — descriptions combat under-triggering
- Use `## Guidelines` sections for constraints and rules
- Use `## Examples` sections with bullet points for usage examples
- Use progressive disclosure: metadata → SKILL.md body → referenced resources

### Python Scripts
- All scripts are executable (`#!/usr/bin/env python3`)
- Scripts support `--help` flags
- Organized into `scripts/`, `core/`, and `eval-viewer/` subdirectories
- Use `__init__.py` to mark Python packages

### Web Stack (web-artifacts-builder)
- React + TypeScript + Tailwind CSS + shadcn/ui
- Bundled with Parcel via `scripts/init-artifact.sh` and `scripts/bundle-artifact.sh`
- Avoid "AI slop" design patterns: no excessive centered layouts, purple gradients, or uniform rounded corners

### Anthropic Brand (brand-guidelines skill)
- Primary colors: `#141413` (dark), `#d97757` (orange accent)
- Typography: Poppins (headings), Lora (body)

## Plugin Marketplace

The `.claude-plugin/marketplace.json` defines three installable bundles:

| Bundle | Included Skills |
|--------|----------------|
| `document-skills` | docx, pdf, pptx, xlsx |
| `example-skills` | claude-api, mcp-builder, skill-creator, webapp-testing, web-artifacts-builder, algorithmic-art, brand-guidelines, canvas-design, slack-gif-creator, theme-factory, internal-comms, frontend-design, doc-coauthoring |
| `claude-api` | claude-api only |

## Development Workflow

### Adding a New Skill
1. Copy `template/SKILL.md` into `skills/new-skill-name/SKILL.md`
2. Fill in the YAML frontmatter (`name`, `description`, optionally `license`)
3. Write clear, actionable instructions in the Markdown body
4. Add any helper scripts to `scripts/`, reference docs to `references/`
5. Register the skill in `.claude-plugin/marketplace.json` under the appropriate bundle
6. Use the `skill-creator` skill to iteratively refine and evaluate the new skill

### Evaluating a Skill (skill-creator)
The `skill-creator` skill has a full evaluation pipeline under `skills/skill-creator/scripts/`:

```bash
# Run the development loop (creates/refines a skill iteratively)
python skills/skill-creator/scripts/run_loop.py --skill <skill-name>

# Run evaluations against test cases
python skills/skill-creator/scripts/run_eval.py --skill <skill-name>

# Aggregate benchmark results
python skills/skill-creator/scripts/aggregate_benchmark.py

# Generate a human-readable report
python skills/skill-creator/scripts/generate_report.py

# Optimize the skill description for better triggering
python skills/skill-creator/scripts/improve_description.py --skill <skill-name>

# Package a skill for distribution
python skills/skill-creator/scripts/package_skill.py --skill <skill-name>

# Quick validation
python skills/skill-creator/scripts/quick_validate.py --skill <skill-name>
```

### Testing Web Apps (webapp-testing skill)
```bash
# Run tests with a managed server lifecycle
python skills/webapp-testing/scripts/with_server.py <test-script.py>
```

### Building Web Artifacts (web-artifacts-builder skill)
```bash
# Initialize a new React artifact
bash skills/web-artifacts-builder/scripts/init-artifact.sh <artifact-name>

# Bundle for distribution
bash skills/web-artifacts-builder/scripts/bundle-artifact.sh <artifact-name>
```

## No Build System / CI

This repository has **no centralized build system, test runner, or CI/CD pipeline**. It is documentation and data-driven:
- No `package.json` at root
- No `requirements.txt` at root
- No `.github/workflows/` or equivalent
- Individual skills contain their own dependencies and scripts

## Git Conventions

- Commit messages reference PR numbers: e.g., `Add claude-api skill (#515)`
- Branch naming: `claude/<description>-<id>` for Claude-authored branches
- Remote: configured per-deployment (local proxy in dev environments)

## Key File Paths

| Path | Purpose |
|------|---------|
| `skills/skill-creator/SKILL.md` | Most complex skill (33KB) — skill development framework |
| `skills/claude-api/SKILL.md` | Multi-language API guide (18KB) |
| `skills/docx/SKILL.md` | Word doc processing (20KB) |
| `skills/mcp-builder/SKILL.md` | MCP server creation guide (9KB) |
| `.claude-plugin/marketplace.json` | Plugin bundle registry |
| `template/SKILL.md` | Minimal skill template |
