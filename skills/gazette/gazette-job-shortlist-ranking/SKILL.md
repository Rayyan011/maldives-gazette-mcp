---
name: gazette-job-shortlist-ranking
description: "Use when ranking Maldives Gazette jobs against a candidate's qualifications and preferences."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [maldives, gazette, iulaan, jobs, ranking]
    related_skills: [gazette-government-job-finding, gazette-compensation-calculator]
---

# Gazette Job Shortlist and Ranking

Compare official Iulaan jobs against a candidate profile without overstating eligibility.

## Workflow

1. Capture must-have qualifications, years of experience, seniority, location, salary needs, deadline constraints, and work authorization.
2. Search with the Dhivehi query skill and fetch each promising detail page and official TOR/application attachment.
3. Extract employer, role, education, experience, responsibilities, salary, location, deadline, and application method. Keep `unknown` when absent.
4. Classify each role as `strong match`, `possible match`, or `insufficient information`. A missing requirement is not proof of eligibility.
5. Rank by must-have fit first, then seniority, location, compensation estimate, deadline feasibility, and source completeness.

## Output

Return a concise ranked table, followed by evidence-backed fit notes, disqualifiers, unknowns, and the safest next action. Link every role to the official Iulaan page and attachment/TOR.

## Pitfalls

- Never turn a three-year candidate into a four-year match.
- Do not rank salary above a failed mandatory qualification.
- Do not infer nationality, age, visa, degree equivalence, or selection outcome.

## Verification checklist

- [ ] Candidate requirements were separated into must-have and preference.
- [ ] Detail pages and available TORs were checked.
- [ ] Fit labels are evidence-backed.
- [ ] Expired and incomplete jobs are clearly labeled.
