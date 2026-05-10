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

### 3. Cassie's current scope (v1 — live)

Cassie can:
- Answer questions about courses, pricing, funding, policies, and registration (from the vault KB)
- Check **live class schedules** via the `get_course_schedule` MCP tool (CATS API)
- Generate **booking links** pre-filled with class details (production server only)

Cassie cannot yet:
- Process bookings or payments — direct users to WhatsApp 9866 0772 or hello@coursemology.sg
- Book courses on behalf of users (future)

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

**Stack:** Claude API (Haiku) → `cassie_server.py` (Flask API) → `cassie_widget.js` (WordPress embed)

**Knowledge base:** `cassie-vault/` — Obsidian wiki (~57 files), hosted at github.com/architechsg/Cassie-Vault

**Key files:**
- `cassie-vault/cassie-persona.md` — Cassie's system prompt (single source of truth for persona + behaviour)
- `cassie-vault/wiki/` — structured KB loaded by `cassie_server.py` at startup
- `C:\Users\Mark Wee\Cassie\Cassie MCP server\cassie_mcp.py` — MCP server exposing `get_course_schedule` tool (dev/Cowork use)
- `C:\Users\Mark Wee\Cassie\Cassie API Server\cassie_server.py` — production Flask backend (tool-use loop, booking links, /chat + /webhook/zobot endpoints)

**Next steps:**
1. Build `cassie_widget.js` — WordPress chat widget embed
2. Future: full booking capability (not just link generation)
3. Future: ask friend to add `start_date_after` filter to CATS API
