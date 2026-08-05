---
name: gazette-compensation-calculator
description: "Use when comparing Maldives Gazette job salaries and monthly take-home estimates."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [maldives, gazette, iulaan, salaries, compensation]
    related_skills: [gazette-government-job-finding, gazette-job-shortlist-ranking]
---

# Gazette Compensation Calculator

Turn salary and allowance wording from an official Iulaan posting or TOR into a transparent monthly estimate. This is an estimate, not a promised salary.

## Workflow

1. Use the official posting and attachment/TOR as the only salary sources. Preserve the original amount and currency.
2. Separate basic salary, fixed monthly allowances, percentage allowances, daily attendance/duty allowances, overtime, and unknown components.
3. Use the requested comparison month. Count Sunday–Thursday as working days; Friday–Saturday are weekends. Remove verified public holidays that fall on working days, without double-counting weekends.
4. Calculate `fixed monthly pay + (eligible working days × per-day allowance)`. Calculate percentage allowances from their stated base only.
5. Return fixed pay, variable pay, estimated total, working-day count, holiday dates used, assumptions, and confidence. Never treat an unstated allowance as zero.

## Output

Use a table with `fixed monthly`, `variable components`, `eligible days`, `estimated monthly total`, and `source`. Mark daily pay as conditional on attendance and label any unknown amount.

## Pitfalls

- Do not call a daily allowance guaranteed monthly salary.
- Do not calculate take-home pay unless tax/deductions are explicitly available.
- Do not silently convert currencies or infer public holidays.
- If the month is unspecified, state the assumed month before calculating.

## Verification checklist

- [ ] Every amount has an official source.
- [ ] Fixed and variable pay are separate.
- [ ] Friday/Saturday and verified holidays were handled correctly.
- [ ] Formula, assumptions, and confidence are visible.
