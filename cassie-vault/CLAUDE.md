# Cassie Wiki — Schema & Maintenance Rules

*This file tells you (the LLM) how to maintain this Obsidian vault.*

---

## Two Modes

### MAINTAIN mode (triggered by Mark)
When Mark says things like "update the knowledge base", "add this course", "the price changed", or drops a source document:
1. Identify which wiki pages need to be created or updated
2. Create/update those pages following the conventions below
3. Add [[wikilinks]] to related pages
4. Update `index.md` if new pages were created
5. Append to `log.md`: `## [YYYY-MM-DD] ingest | {description}`

### ANSWER mode (triggered by Wee Kee Long or any student)
When someone asks a question as a student or customer, read `cassie-persona.md` first — that is Cassie's full persona, tone, tool usage guide, and booking link instructions. Then:
1. Read `index.md` to find the relevant wiki pages
2. Read those pages (follow [[wikilinks]] if you need more detail)
3. Answer following the persona defined in `cassie-persona.md`
4. Cite the page you read if useful
5. If the answer turns into a useful FAQ, offer to file it in `wiki/faq/`

---

## File Conventions

### Folder structure
```
cassie-vault/
├── CLAUDE.md           ← this file (vault maintenance rules)
├── cassie-persona.md   ← Cassie's system prompt (persona, tone, tool usage, booking links)
├── index.md            ← master page catalog (read this first on every query)
├── log.md              ← append-only change log
└── wiki/
    ├── company/        ← overview, locations, contact
    ├── courses/        ← one .md per course, organised by category subfolder
    ├── policies/       ← payment, deposit, refund, reschedule, attendance, certification
    ├── funding/        ← SSG subsidies, SFC, UTAP, corporate, pricing tiers
    ├── faq/            ← compiled Q&As
    └── concepts/       ← WSQ explained, Singpass, OLA platform
```

### Course page slugs
`wiki/courses/{category}/{slug}.md`
Category folders: `food-safety`, `maintenance`, `baking-cooking`, `ai-tech`, `cleaning`, `ms-office`, `admin-hr`, `first-aid`, `beauty`, `drone-media`, `ecommerce`, `other`

### Required frontmatter on every page
```yaml
---
tags: [list, of, tags]
last_updated: YYYY-MM-DD
---
```

Course pages also need:
```yaml
ola_module_id: NNNN
tgs_code: TGS-XXXXXXXXX   # omit if no TGS code
provider: AesthetiCar Pte Ltd | Associates Consulting Pte Ltd | Cantley LifeCare Pte Ltd
course_type: WSQ | Non WSQ | Private
funding_expiry: YYYY-MM-DD  # omit if no SSG funding
```

### Wikilinks
Use `[[folder/page-slug]]` syntax for all cross-references. Example:
- `[[funding/skillsfuture-credit]]`
- `[[policies/refund-cancellation]]`
- `[[locations]]` (for the locations page)

Every page should be self-contained — readable without requiring the reader to have read another page first. Links provide depth, not required context.

---

## Pricing Tiers (reference)

| Who | Subsidy |
|---|---|
| Foreigner / under 21 / non-eligible | Full fee (no subsidy) |
| Singapore PR aged 21+ | ~30% subsidy |
| Singapore Citizen aged 21–39 | ~45% subsidy (MCES) |
| Singapore Citizen aged 40+ or SME-sponsored | ~65% subsidy (MCES) |

All prices shown in the KB are **GST-inclusive**. GST is 9%, calculated on the pre-subsidy full fee.

---

## Lint Checks (run periodically)
Ask the LLM to health-check the wiki by looking for:
- Courses with `funding_expiry` dates in the past
- Orphan pages with no inbound links
- Missing [[wikilinks]] to related policies/funding on course pages
- Courses mentioned in index but file not found
