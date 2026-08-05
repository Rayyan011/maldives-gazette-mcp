---
name: gazette-dhivehi-query-builder
description: "Use when turning an English Gazette or Iulaan request into Dhivehi Thaana searches."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [maldives, gazette, iulaan, dhivehi, search]
    related_skills: [gazette-government-job-finding, gazette-business-project-finding]
---

# Gazette Dhivehi Query Builder

Create searchable Dhivehi Thaana variants from a natural English request. The variants are search aids, not claims about official terminology.

## Workflow

1. Preserve the exact original prompt and identify role, sector, location, seniority, and action terms.
2. Load `../gazette-government-job-finding/references/dhivehi-query-mappings.md` when it applies. Use standard mappings first, then useful individual-term variants.
3. Produce a narrow phrase, one or two broader phrases, and the original English fallback. Do not replace the English query entirely.
4. Search Iulaan with `announcement_type` and `open_only` filters when relevant. Record the exact variants and which one matched each result.
5. If no results appear, relax one term at a time and explain the relaxation.

## Output

Return `original_prompt`, `search_variants`, `filters`, `matched_variant`, and the official search URL. Preserve Thaana exactly.

## Pitfalls

- Do not invent a Dhivehi translation when no mapping exists; label it as a transliteration/search variant.
- Do not broaden “government” into every private employer without saying so.
- Do not use only the broad word `އޮފިސަރ` when a narrower phrase is available.

## Verification checklist

- [ ] Original English prompt is preserved.
- [ ] Standard Thaana mappings were used where available.
- [ ] Narrow and fallback searches were attempted as needed.
- [ ] Every result records its matching variant.
