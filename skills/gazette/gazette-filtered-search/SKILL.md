---
name: gazette-filtered-search
description: "Use when searching the Gazette with its live category, office, date, job, and open-status filters."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [maldives, gazette, iulaan, filters, search]
    related_skills: [gazette-dhivehi-query-builder, gazette-government-job-finding, gazette-business-project-finding]
---

# Gazette Filtered Search

Use the website's real filters before relying on broad keyword matching.

## Workflow

1. Call `iulaan_filter_schema` or `gazette_filter_schema` when a filter value is unknown. Preserve the live value and decoded label.
2. For jobs, prefer `announcement_type=vazeefaa`; use `job_category=human-resource`, `construction`, or another live category when applicable. For projects, use `announcement_type=masakkaiy` and the relevant category.
3. Add `office`, `start_date`, `end_date`, `open_only`, and `page` only when they match the user's request. Keep the exact filters in the result.
4. Use `search_iulaan_advanced` or `search_gazette_advanced`, then inspect promising detail pages and attachments.
5. If the category-filtered search is empty, run a controlled keyword/Thaana fallback and explain the relaxation.

## Output

Return query, decoded filters, result count, matched query variant, deadline/publication date, source URL, and freshness. Distinguish no matches from an unreachable source.

## Pitfalls

- Do not confuse `masakkaiy` (work/projects) with `beelan` (tender/bid).
- Do not use `type=construction`; construction is an Iulaan `job-category`.
- Do not call all officer results HR results when the human-resource filter returned none.
- Do not assume `open_only` is available for Gazette records; it is an Iulaan filter.
