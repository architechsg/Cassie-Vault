# Cassie Chatbot — Project Instructions for Claude

This is the workspace for the Cassie chatbot project (coursemology.sg).
Read this file at the start of every conversation. Follow all instructions below.

---

## Standing Rules

### 1. After every significant work session — always do both:

**A) Log to the vault:**
Append an entry to `cassie-vault/log.md`:
```
## [YYYY-MM-DD] {type} | {short description}
- Bullet list of specific changes made
```
Types: `ingest` (new content added), `update` (edits to existing pages), `query` (questions answered), `lint` (health check run)

**B) Update project memory:**
Update `memory/project_cassie_chatbot.md` (in the Cowork memory folder) to reflect:
- What was done in this session (add to status list)
- Any new key facts learned about the business or project
- Any changes to next steps

Do this without being asked. If the session was purely conversational with no file changes, a memory update is still appropriate if anything meaningful was discussed.

---

### 2. Cassie vault is the source of truth

When answering any question about Coursemology.sg, courses, pricing, policies, or funding:
- Start at `cassie-vault/index.md` to find the right page
- Read the relevant page(s) before answering
- Never make up prices, dates, policies, or course details

When working in MAINTAIN mode (updating the vault):
- Follow the conventions in `cassie-vault/CLAUDE.md`
- Always update `cassie-vault/index.md` if new pages are created
- Always log changes to `cassie-vault/log.md`

---

### 3. Cassie's current scope (info-only, v1)

Cassie is an information-only bot. She cannot:
- Check live class schedules (future: OLA API)
- Book courses for users (future: booking tool)

For schedule and availability questions, direct users to:
- WhatsApp: 9866 0772
- Email: hello@coursemology.sg
- Website: coursemology.sg

---

### 4. Files never to commit to GitHub

These folders/files contain sensitive data and must never be pushed:
- `DB data/`
- `access files/`
- `business-logic-extracted/`
- `misc/`
- Any `*.accdb` files

---

## Project Summary

Rebuilding "Cassie", an AI chatbot for coursemology.sg — a Singapore WSQ/SkillsFuture training provider.

**Stack:** Claude API (Haiku) → cassie_server.py (Python) → cassie_widget.js (WordPress embed)

**Knowledge base:** `cassie-vault/` — 54-file Obsidian wiki, hosted at github.com/architechsg/Cassie-Vault

**Next steps:**
1. Build `cassie_server.py` — Python API server wrapping Claude API (info-only for now)
2. Build `cassie_widget.js` — WordPress chat widget embed
3. Future: add OLA API tool for live schedules
4. Future: add booking capability
