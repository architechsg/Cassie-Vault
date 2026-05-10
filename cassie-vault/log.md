# Cassie Wiki — Change Log

Append-only. Format: `## [YYYY-MM-DD] {type} | {description}`
Types: `ingest`, `query`, `lint`, `update`

---

## [2026-05-11] update | Dev infrastructure — API keys secured, repos prepped for GitHub, demo.html fixed
- Both `cassie_server.py` (Anthropic + CATS keys) and `cassie_mcp.py` (CATS key) moved to `.env` files via `python-dotenv`; keys no longer hardcoded
- `.gitignore` and `.env.example` added to Cassie API Server and Cassie MCP Server folders
- `demo.html` fixed: booking links now clickable — added markdown `[text](url)` → `<a>` regex in `addBotMessage()` with hyperlink CSS styling
- `test_start_date_filter.py` created and run: confirmed `start_date_after` CATS API filter NOT yet active (count 112→112, 2024 dates still returned); both files remain on client-side date filtering
- Multi-tool-call behavior verified correct — Claude reformulates failed generic course queries using specific names from KB
- Architectural decision solidified: MCP = data-only (no booking logic); `cassie_server.py` owns `LOCATION_ADDRESSES`, `build_booking_url()`, and all business logic

## [2026-05-10] update | Persona refactor — cassie-persona.md created as single source of truth
- Extracted Cassie's persona, tone, tool usage guide, and booking link instructions from `CLAUDE.md` into new `cassie-vault/cassie-persona.md`
- `cassie_server.py` now loads `cassie-persona.md` at startup instead of hardcoded system prompt string
- `CLAUDE.md` ANSWER mode section now points to `cassie-persona.md` instead of duplicating the content
- Single edit point for Cassie's behaviour in both Cowork dev mode and production

## [2026-05-10] update | Booking link generator added — Cassie now surfaces registration links after schedule queries
- Updated `CLAUDE.md` (vault): added "Booking Links" section instructing Cassie to share the `booking_url` from schedule results
- Cassie now gently nudges users toward booking after showing class dates ("Ready to book? Here's your registration link…")
- Rules added: never share booking link for a FULL class; fallback to WhatsApp if link missing
- Corresponding code changes made outside the vault: `cassie_mcp.py` and `cassie_server.py` now include `build_booking_url()` helper and populate `booking_url` in each class run result

---

## [2026-05-08] update | SSG subsidy rates corrected — YanHui confirmed exact figures
- Previous vault had approximate rates (~45%, ~65%, ~30%) — now replaced with official SSG rates
- Self-sponsored: SC/PR/LTVP+ 21–39 = 50%; SC 40+ = 70%
- Company-sponsored: SME = 70%; non-SME = 50%
- LTVP+ payment note added: full fee collected upfront, grant refunded after SSG disbursement
- Eligibility updated: PR and LTVP+ now correctly grouped with SC for subsidy tiers

## [2026-05-08] update | CLAUDE.md updated — Cassie now has live schedule tool
- Updated personality section: Cassie can now check live schedules via get_course_schedule MCP tool
- Removed redirect-to-WhatsApp as default for schedule queries
- Added "Live Schedule Tool" section with full instructions: when to call, how to construct query, how to handle results (found / not found / ambiguous / month not available)
- Booking still not active — WhatsApp redirect kept for booking only

## [2026-05-08] update | YanHui confirmed: LTVP+ eligible for SSG subsidy at 75% attendance
- UPDATED: ssg-subsidies.md — added LTVP+ row to subsidy tiers table (eligible, 75% attendance required)

## [2026-05-08] update | Dad confirmed: MacPherson closed, cash rarely used, 75% attendance correct
- **REMOVED**: MacPherson venue from locations.md — dad confirmed "MacPherson is no longer, closed liao"
- Updated locations.md intro from "six" to "five" training locations; removed MacPherson from "Which Courses Run Where"
- **UPDATED**: payment-methods.md Cash row — "rarely collected in practice, PayNow preferred" (confirmed by dad; YanHui to finalise exact policy)
- Removed "Cash only at Toa Payoh" note from Toa Payoh entry in locations.md
- **RESOLVED**: 75% attendance is correct for SSG funding eligibility (dad confirmed); CATS kform 80% figure is wrong — vault unchanged, already correct
- ⚠️ STILL OPEN: LTVP+ SSG subsidy rate — dad confirmed eligible but rate unknown; ask YanHui
- ⚠️ STILL OPEN: Exact cash payment policy — ask YanHui to confirm

## [2026-05-08] update | Final vault sync — remaining business-logic files + full DB data re-check
- Read remaining 11 business-logic files: agent-attribution-and-sales, ar-aging-and-soa, daily-closing, sfc-invoicing, penalty, zoho-integration, xero-invoice-gen-workflow, xero-payment-confirmed-flow-v2, class-count-and-revenue-reports, global-vba-helpers, auth-and-navigation
- Finding: all 11 are internal-ops only (sales reporting, AR aging, daily closing, Xero/Zoho integrations, VBA helpers, auth) — no new customer-facing content identified
- Re-checked DB data folder (35 files): found MacPherson and Ubi Workshop missing from locations page
- **UPDATED**: `wiki/company/locations.md` — added MacPherson (401 MacPherson Road, #01-12, MacPherson Mall, S368125) and Ubi Workshop (01-434 Ubi Road 1, S408701); updated intro from "four" to "six" training locations
- ⚠️ OPEN: LTVP+ student type appears in DB — eligibility for SSG subsidies unclear. Needs Mark's confirmation before adding to vault.

## [2026-05-08] ingest | CATS system deep-dive — new pages and policy updates from internal admin system
- Source: CATS (Coursemology Admin Terminal System) — 20+ business-logic markdown files covering enrolments, invoicing, payments, refunds, reschedules, deposits, SSG grant claims
- **NEW**: `wiki/concepts/wsq-registration-data.md` — complete list of personal data required for WSQ/SSG-funded course registration (NRIC, DOB, salary, education, etc.)
- **NEW**: `wiki/funding/corporate-invoicing.md` — invoice format (ATT/AB/CT-OLA-XXXXX), which entity issues, payment terms, GST at 9%, how to pay
- **UPDATED**: `wiki/company/overview.md` — added billing abbreviations (ATT/AB/CT) and invoice number format; link to corporate-invoicing page
- **UPDATED**: `wiki/policies/refund-cancellation.md` — added bank account requirement for Finance Bank Refund (bank transfer) type
- **UPDATED**: `wiki/faq/registration.md` — 2 new Q&As: WSQ data requirements, corporate invoice reading guide
- **UPDATED**: `index.md` — added entries for 2 new pages
- ⚠️ ATTENTION: CATS kform doc references SSG attendance requirement as **80%**, but the vault currently says **75%**. Needs verification with Mark before changing.

## [2026-05-08] update | Real-world KB gaps patched from WhatsApp conversation analysis
- Source: 3 WhatsApp conversation files (Chat AB Course Conversation, Chat CT Course Conversation, Conversation) containing ~15 real customer journeys via SalesIQ → Coursemology.sg
- faq/general.md — added 4 new Q&As: (1) all courses are face-to-face only (no online option); (2) Work Permit holders can attend and receive WSQ cert, full fee applies, Gmail for e-attendance; (3) Mid-Career Enhanced SFC has separate approved course list, not all Coursemology courses qualify; (4) food safety cert renewal — refresher (not full course) at 5-year mark, then every 10 years
- company/locations.md — Toa Payoh: added "no lift, staircase only" accessibility warning
- courses/drone-media/drone-media-courses.md — Aerial Photography (#CT11): added course structure note (Day 1 theory at Toa Payoh, Days 2–4 practical at Sin Ming Open Field, trainer WhatsApp group for coordination); Video Production (#CT61): added marketing alias "Mobile Photography & Videography for Beginners"
- funding/skillsfuture-credit.md — added Mid-Career Enhanced SFC section (two credit types, how to check balance breakdown); added one.coursemology.sg personalised SFC submission portal explanation with NRIC/DOB accuracy note
- courses/cleaning/cleaning-courses.md — added Work Permit Holders section (eligible to attend, full fee, WSQ cert valid, FIN + Gmail for e-attendance)
- policies/payment-methods.md — added PayNow UENs by provider: AesthetiCar (201400645KATT), Cantley LifeCare (201703024GCCC + UOB 360-309-963-8)

## [2026-05-08] update | Post-build fixes after DB data scan + full vault review
- Added Cheque as accepted payment method (payment-methods.md)
- Fixed 4 broken wikilinks: [[courses/ms-office/microsoft-copilot]] → [[courses/ms-office/ms-office-courses]] in 3 AI Tech files; [[courses/drone-media/video-production-social-media]] → [[courses/drone-media/drone-media-courses]] in visual-content-creation-ai.md
- Full DB data scan (34 files): no new pages required; confirmed vault content matches DB

## [2026-05-08] ingest | Initial vault build from cassie_knowledge_base.md + db2_active_modules_full.json + business-logic docs
- Created all company, course, policy, funding, FAQ, and concept pages
- 65+ course pages across 12 categories
- Sources: cassie_knowledge_base.md (May 2026), db2_active_modules_full.json, business-logic extracted docs
- Added #AB51A Copilot Training Workshop (from JSON, missing from original KB)
- Added PSEA eligibility flags to relevant courses
- Deposit policy updated to reflect actual range ($20–$100+ depending on course)
