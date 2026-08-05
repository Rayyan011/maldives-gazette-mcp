---
name: job-finding
description: "Use when finding, comparing, or tracking job opportunities."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [jobs, careers, search, applications, research]
    related_skills: []
---

# Job Finding

A source-agnostic workflow for finding real job opportunities, comparing them against a candidate's constraints, and producing an actionable shortlist. It works with ordinary web search, public job boards, employer career pages, public APIs, and user-provided job links.

## When to use

Use when the user asks to find jobs, remote work, internships, contracts, roles in a location, visa-friendly positions, jobs above a salary threshold, or help tracking applications.

Do not automatically apply, message recruiters, upload documents, accept terms, or disclose personal information. Those are separate actions requiring an explicit request and confirmation at the point of submission.

## 1. Define the search brief

Capture the highest-impact constraints before searching:

- Target role and adjacent titles
- Seniority and years of experience
- Location, remote/hybrid/onsite preference, and time zone
- Employment type: full-time, part-time, contract, freelance, internship
- Minimum salary and currency; state whether gross, net, hourly, or annual
- Visa/work authorization and relocation constraints
- Must-have skills, nice-to-have skills, and exclusions
- Preferred industries, company size, and start date
- Whether the user wants discovery only, a ranked shortlist, or an application tracker

If details are missing, search with a reasonable broad default and clearly label the assumptions rather than blocking unnecessarily.

## 2. Search in layers

Search broad-to-narrow and keep the query/source visible:

1. Employer career pages for target companies.
2. Public job boards and professional networks accessible without login.
3. Specialist boards for the role, country, industry, or disability/visa/remote niche.
4. Search engines using exact role titles, skills, location, and date terms.
5. User-provided referrals or company links.

Prefer an employer's own posting when it conflicts with an aggregator. Do not bypass authentication, paywalls, CAPTCHAs, robots restrictions, or rate limits. If a source is blocked, record it as a limitation and use a lawful alternative.

## 3. Extract evidence, not guesses

For every candidate role, preserve:

- Job title and employer
- Direct posting URL and source URL
- Location and work mode
- Employment type and seniority
- Salary/range, currency, and pay basis exactly as posted
- Required and preferred qualifications
- Work authorization or visa language
- Posting date, closing date, or freshness signal
- Application method and whether login is required
- A short evidence excerpt for material claims

Use `null` or "not stated" for missing fields. Never infer salary, remote status, visa sponsorship, seniority, or closing date from a title or a similar posting.

## 4. Verify freshness and legitimacy

Before ranking a role:

- Open the direct employer or authoritative posting when possible.
- Check whether the page is still accepting applications.
- Watch for duplicate, expired, reposted, or contradictory listings.
- Confirm the employer domain and application destination.
- Flag requests for money, gift cards, crypto, banking credentials, passport scans before a legitimate hiring stage, or communication that moves suspiciously off-platform.
- Treat social posts and aggregators as leads, not proof.

A job is not confirmed merely because it appears in a search result. State the live-check time and any uncertainty.

## 5. Rank transparently

Use a simple weighted comparison rather than a mysterious score. Suggested dimensions:

- Role and skill fit: 0–30
- Location/work-mode fit: 0–20
- Compensation fit: 0–20
- Authorization/visa fit: 0–15
- Employer/source confidence: 0–10
- Freshness/application feasibility: 0–5

Explain the biggest positive and negative factors. Keep hard disqualifiers separate from preferences. Do not let a high salary compensate for a failed work-authorization or location requirement.

## 6. Tailor without fabricating

For shortlisted roles, provide:

- Why it matches the brief
- Gaps or risks to verify
- Which existing experience maps to the requirements
- A truthful resume or cover-letter angle
- A small set of role-specific questions

Never invent experience, degrees, certifications, employment dates, work authorization, referrals, or achievements. Ask the user before changing a factual resume claim.

## 7. Track applications

If the user wants tracking, use a table with:

`company | role | location | source_url | direct_url | salary | status | date_found | deadline | next_action | notes`

Recommended statuses: `saved`, `researching`, `ready_to_apply`, `applied`, `screening`, `interviewing`, `offer`, `rejected`, `withdrawn`, `expired`.

Keep application tracking separate from public job discovery. Do not store passwords, private recruiter messages, identity documents, or sensitive personal data unless the user explicitly provides a safe storage location and asks for it.

## Output format

For a shortlist, return:

1. Search brief and assumptions
2. Freshness timestamp and sources checked
3. Ranked table with direct links
4. Evidence-backed fit notes
5. Risks, missing information, and scam checks
6. Suggested next actions

For broad searches, report the number of sources and candidates reviewed, deduplication method, inaccessible sources, and why candidates were excluded.

## Common pitfalls

1. **Aggregator copy mistaken for an active role:** verify on the employer page.
2. **Salary normalization without a basis:** preserve the posted currency and pay period; ask before converting.
3. **Remote interpreted as worldwide:** check country, time-zone, payroll, and authorization limits.
4. **Visa sponsorship assumed:** only mark it positive when the employer explicitly states it or an authoritative source confirms it.
5. **Expired postings ranked as current:** check the direct page and timestamp every result.
6. **Keyword matching without fit review:** compare actual requirements and seniority.
7. **Automatic application creep:** prepare materials, but stop before submission or external communication.
8. **Sensitive-data oversharing:** use placeholders until the user explicitly approves a secure submission step.

## Verification checklist

- [ ] Search brief and assumptions are explicit.
- [ ] Every shortlisted role has a direct source URL.
- [ ] Salary, location, work mode, visa, and freshness are evidence-backed or marked unknown.
- [ ] Duplicate and expired postings are removed or labeled.
- [ ] Scam indicators and inaccessible sources are reported.
- [ ] No application, message, upload, or account change occurred without explicit authorization.
