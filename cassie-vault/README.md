# Cassie Vault — Knowledge Base for Cassie AI Chatbot

This repository is the structured knowledge base (KB) that powers **Cassie**, the AI assistant for [Coursemology.sg](https://coursemology.sg) — a Singapore WSQ/SkillsFuture training provider.

---

## What Is This?

Cassie is an AI chatbot built to answer questions from prospective students and existing customers about courses, pricing, SkillsFuture subsidies, policies, and registration. Instead of a traditional RAG/vector database approach, Cassie's knowledge lives in a structured Obsidian wiki — this repository — which is loaded directly into the system prompt of a Claude API call.

This approach was chosen after a previous Dify/RAG implementation failed due to poor knowledge retrieval. A structured, human-readable wiki gives the LLM precise, navigable information without hallucination risks.

---

## Repository Structure

```
cassie-vault/
├── README.md               ← this file
├── CLAUDE.md               ← LLM instructions: schema rules, Cassie's personality, maintenance conventions
├── index.md                ← master page catalog — the LLM reads this first on every query
├── log.md                  ← append-only change log
└── wiki/
    ├── company/            ← overview, locations (with accessibility notes), contact
    ├── courses/            ← one .md per course, organised by category
    │   ├── food-safety/
    │   ├── maintenance/
    │   ├── baking-cooking/
    │   ├── ai-tech/
    │   ├── cleaning/
    │   ├── ms-office/
    │   ├── admin-hr/
    │   ├── first-aid/
    │   ├── beauty/
    │   ├── drone-media/
    │   ├── ecommerce/
    │   └── other/
    ├── policies/           ← payment, deposit, refund, reschedule, attendance, certification
    ├── funding/            ← SSG subsidies, SkillsFuture Credit, UTAP, corporate, pricing tiers
    ├── faq/                ← compiled Q&As from real customer enquiries
    └── concepts/           ← WSQ explained, SingPass attendance, OLA platform
```

**Total pages:** ~54 structured wiki pages covering 65+ courses across 12 categories.

---

## How It Works

```
User message
    ↓
cassie_server.py  (Python — not in this repo)
    ↓
Reads CLAUDE.md + index.md + relevant wiki pages
    ↓
Injects as system prompt → Claude Haiku API (claude-haiku-4-5)
    ↓
Haiku responds as Cassie
    ↓
Response returned to WordPress widget (cassie_widget.js)
```

The LLM is instructed to start at `index.md`, identify the relevant page(s), read them, then answer. Wikilinks (`[[page/slug]]`) guide navigation between related pages.

---

## Three Training Providers

All courses run under the Coursemology.sg brand across three SSG-registered providers:

| Provider | Courses |
|---|---|
| AesthetiCar Pte Ltd | Food Safety, Maintenance, Baking & Cooking, AI & Tech |
| Associates Consulting Pte Ltd | Cleaning, MS Office, Admin/HR, First Aid, Beauty |
| Cantley LifeCare Pte Ltd | Drone & Digital Media, Ecommerce, Workflow AI |

---

## Cassie's Current Scope (v1)

Cassie is an **information-only** bot. She answers questions about courses, pricing, subsidies, policies, and registration logistics. She cannot:
- Check live class schedules (planned: OLA API integration)
- Book courses on behalf of users (planned: future phase)

For schedule and booking enquiries, she directs users to WhatsApp 9866 0772 or hello@coursemology.sg.

---

## Maintaining This Vault

All updates follow the conventions in `CLAUDE.md`. Key rules:
- Every change is logged in `log.md`
- New pages must be linked in `index.md`
- Wikilinks use `[[folder/slug]]` format
- All prices shown are GST-inclusive
- Frontmatter is required on every page (`tags`, `last_updated`; course pages also need `ola_module_id`, `provider`, `course_type`)

---

## Related Repositories

- **cassie_server.py** — Python API server (private, not yet built)
- **cassie_widget.js** — WordPress embed widget (private, not yet built)

---

*Last vault update: 2026-05-08*
