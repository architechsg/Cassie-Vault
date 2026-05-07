# Cassie Wiki — Change Log

Append-only. Format: `## [YYYY-MM-DD] {type} | {description}`
Types: `ingest`, `query`, `lint`, `update`

---

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
