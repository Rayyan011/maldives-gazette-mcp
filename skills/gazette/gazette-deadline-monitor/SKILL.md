---
name: gazette-deadline-monitor
description: "Use when tracking open Iulaan application deadlines and deadline risk."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [maldives, gazette, iulaan, deadlines, monitoring]
    related_skills: [gazette-government-job-finding, gazette-job-shortlist-ranking]
---

# Gazette Deadline Monitor

Re-check saved official Iulaan URLs and report application deadlines in urgency order.

## Workflow

1. Start from URLs or announcement IDs supplied by the user; do not silently create a permanent watchlist.
2. Fetch each official detail page and compare its current deadline with the saved value.
3. Use the current date and Maldives time when classifying `expired`, `urgent`, `upcoming`, or `no deadline stated`.
4. Report changed, extended, withdrawn, inaccessible, and contradictory notices separately.
5. For recurring monitoring, use an explicitly approved scheduler; otherwise provide a one-time report only.

## Output

Return deadline, time remaining, employer, role, status, last checked time, source URL, and any change from the previous check.

## Pitfalls

- A searchable page is not necessarily open.
- Do not assume a deadline extension from a newer social post.
- Preserve the posted time and timezone when available.
- Never submit an application or contact an office.

## Verification checklist

- [ ] Every deadline came from the current official detail page.
- [ ] Current date/timezone is stated.
- [ ] Expired and inaccessible items are not presented as open.
- [ ] No external action was taken.
