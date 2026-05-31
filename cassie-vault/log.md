# Cassie Wiki — Change Log

Append-only. Format: `## [YYYY-MM-DD] {type} | {description}`
Types: `ingest`, `query`, `lint`, `update`

---

## [2026-05-31] update | Deep-dive meticulous V4 cleanup of all 47 enriched vault entries

- **Trigger:** Mark spotted that the previous cleanup pass still had truncation (cleaning-courses.md being "cut off"). Asked for a deep, meticulous pass.
- **Switched extraction strategy** from flat-text regex to **BS4 HTML walker**: parse the gutena-tabs `wp-block-gutena-tab` divs, walk each panel's siblings forward from each `<h2>/<h3>` heading, collect `<p>/<ul>/<ol>` content until a hard-stop heading (Mode of Assessment / Certification / Pre-requisites / Locations / Languages / Course Details / etc.). Skip-but-don't-stop on cross-promo h2 bleeds (Office Management Skills, Effectiveness Management, etc.).
- **Cross-panel fallback heading search**: some courses put Course Objectives in the Course Introduction panel rather than Course Outline (e.g. Excel Basic). V4 searches both panels for each section.
- **Sentence-boundary truncation**: cuts at `[.!?] ` boundaries (or `;` / ` ` as fallback), never mid-word. Cap raised 400–500 → 600–900 chars per field.
- **Polish pass** stripped: leading title-repeats (e.g. BCLS bullet used to start "BCLS (CPR + AED) Course This course aims..." → now "This course aims..."), trailing "Visit this page for more X courses in Singapore." UI tails, "View the X here" cross-promo, double-period before "Examples:".
- **Final audit:** 27 vault blocks now have rich website-sourced content; **18 of 27 have all 5 fields** (What you'll learn / Course modules / Who should attend / Prerequisites / Assessment & certification); 6 have 4 fields; 3 have 3 fields. **Zero remaining noise** in any bullet (no more "certified with a combined", no "Visit this page", no "Course Provider: UEN:" boilerplate, no title-repeats). 13 vault blocks have no enriched content — those are the Private courses (Cookie, Mooncake, Sake, Eyelash, Hair-cutting variants, Child First Aid, Copilot private, Drone bundle, Malay food safety) without public website detail pages.
- **Specific verifications:**
  - `food-safety-level-1-english.md` Assessment still verbatim from website: "1.5-hour assessment... Practical Performance (PP)... MCQ + SAQ" — matches Mark's BCLS-test reference.
  - `first-aid/first-aid-courses.md` BCLS Course modules is now correctly "Adult CPR; Adult Relief; Child CPR; Child Relief; Infant CPR; Infant Relief; AED" — the cross-promo "Office Management Skills" bleed is gone permanently.
  - `cleaning/cleaning-courses.md` — all 7 WSQ cleaning courses have full content with proper module breakdowns.
  - `ms-office/ms-office-courses.md` — Excel Basic (AB22) had originally been thin because the page puts Objectives in the Intro tab; V4's cross-panel search now picks it up properly.
- **Approach scripts:** `/tmp/v4_extract.py` (the BS4 walker), `/tmp/v4_apply.py` (vault writer), `/tmp/final_audit.py` (verification). Raw HTML snapshots in `/tmp/cm_data/raw/*.html` if a fresh re-extract is ever needed.

---

## [2026-05-31] update | Cleanup pass on contaminated Course Content bullets (Mark's BCLS exam test caught the issue)

- **Trigger:** Mark tested local Cassie with "Food Safety Level 1 — what's the exam?" Cassie's reply said "3 parts: MCQ, SAQ, PP — pass all three". Mark checked and pushed back. Investigated and found the vault's "Assessment / certification" bullet was contaminated: cut off mid-sentence at "1." and bled into instructor-bio text ("certified with a combined 20 years of culinary experience..."). The actual website says: **"1.5-hour assessment comprising a Practical Performance (PP) and a Written Assessment. The Written Assessment includes both MCQ and SAQ."** Two parts, not three. Cassie had reframed it incorrectly because vault content was garbage.
- **Scope of contamination:** Audited all 47 enriched entries. ~40 of them had similar bleed in the Assessment bullet — pulling in "Venue(s): Toa Payoh Central...", "Language: English", "Course Outline...", "Course Provider: ASSOCIATES CONSULTING...", "certified with a combined 20 years..." (instructor bios), TGS codes, UENs, etc. Pattern: the original regex stopped at section-paragraph boundaries that don't exist in the WordPress page DOM.
- **Cleanup pass executed:**
  - Built a much stricter section-boundary regex (`Venue(s):`, `Language:`, `Course Outline`, `Course Details`, `Minimum Entry`, `Pre-requisites`, `Admission Requirements`, `Course Provider`, `certified with a combined`, `Visit this page`, `Schedule a class`, etc.).
  - New extractor pulls Assessment content from the "Course Outline" tab's `Mode of Assessment` subsection specifically, then truncates at the first boundary hit.
  - Re-injected ONE clean block per course; removed the contaminated old bullets.
  - Bug along the way: my first dedup regex looked for colon AFTER `**` markers, but markdown has colon INSIDE (`**What you'll learn:**`). Fixed and re-ran; cleaned 5-14 contaminated bullets per entry across all 27 catch-all blocks.
  - Final pass: deleted 4 specific Course modules bullets that were obvious cross-promo bleed (BCLS had "Course modules: Office Management Skills" from the page's related-courses sidebar; similar for admin-hr, ev-car, cleaning).
- **Specific fix on the BCLS-trigger:** `food-safety-level-1-english.md` now has accurate Assessment line: "At the end of the course, participants will undergo a 1.5-hour assessment. This assessment comprises a Practical Performance (PP) and a Written Assessment. The Written Assessment includes both Multiple-Choice Questions (MCQ) and Short Answer Questions (SAQ)..." Matches the website verbatim. Cassie should no longer say "3 parts".
- **Bullet schema standardised:** Every entry now has up to 5 clean bullets: `What you'll learn` / `Course modules` / `Who should attend` / `Prerequisites` / `Assessment & certification`. (Renamed from `Assessment / certification` to `Assessment & certification` — slash was confusing in some regex matches.)
- **Remaining quality risks** (not yet cleaned, lower priority): some entries still have truncated content mid-sentence at the 400-500 char cap; some "Who should attend" sections cut off at "Examples of roles that should attend" before listing the actual roles; raw content is still website prose not rephrased to Cassie's voice. Catchable by Phase 3 classifier in production grading.

---

## [2026-05-31] verify | CATS-check of the 10 unmatched website pages — all confirmed duplicates, zero vault adds needed

- **Why:** After the bulk course-content backfill, 10 website pages had no matching vault entry. Mark's rule: website is golden source — so any website page that exists in CATS should become a vault entry.
- **Method:** For each of the 10 unmatched website slugs, called `get_course_schedule` via the CATS MCP tool. Compared returned course code to existing vault entries.
- **Result:** ZERO new vault adds needed. Every CATS-confirmed match pointed to a course vault already has.
  - `automation-management-generative-ai-chatbots2` — text identical to v1; vault has #AT52.
  - `basic-car-maintenance-course` (title "EV Maintenance") — CATS returns #AT22A "Basic Car w/ Hands-on"; vault has it.
  - `caas-uapl-drone-course-singapore` — same Course Introduction text as the drone-photography slug; vault has #CT11.
  - `employment-111-manpower` — not a course (B2B/manpower page).
  - `food-hygiene-refresher-course` — not in CATS directly (old naming); vault has #AT13 L1 Refresher.
  - `implement-work-plans-and-monitor-performance` — CATS returns #AB33 DCMP L3; vault has it.
  - `microsoft-excel-2019` — legacy/deprecated page; vault has AB22/23/24.
  - `professional-makeup-essentials-singapore` — CATS returns #AB82; vault has it.
  - `wsq-food-safety-level-1-mandarin-course` — vault has Mandarin Food Safety L1.
  - `basic-computer-course-senior-citizens` — already auto-mapped to OL68 in earlier pass.
- **Insight for Mark (not a vault issue):** the website has SEO/marketing-driven duplicate slugs for the same underlying course (common WordPress pattern). Three slugs (`employment-111-manpower`, `microsoft-excel-2019`, `food-hygiene-refresher-course`) are legacy pages with no CATS match — they should probably be cleaned up on the website side or redirected. Suggest raising with Weixing/website team.

---

## [2026-05-31] ingest | Course content backfill from coursemology.sg (47 of 62 vault entries enriched)

- **Why:** Vault course entries were skeletal (title + code + duration + funding). Cassie couldn't answer "what does this course teach?" or "is there an exam?" Weixing confirmed: content from website, prices/schedules from CATS, structural metadata from vault. This pass adds the missing course-content layer.
- **Method:** Scraped all 71 course-detail pages on coursemology.sg (gutena-tabs blocks: Course Introduction / Course Outline / Requirements / FAQs). 56 of 71 returned real content (15 are 404/duplicate/redirect slugs). Matched to vault entries by course code (catch-all blocks) or hand-curated slug map (single-course files).
- **Outcome:** 47 of 62 vault course entries enriched with 4 new bullet fields:
  - `**What you'll learn:**` — course objectives / learning outcomes
  - `**Who should attend:**` — target audience
  - `**Prerequisites:**` — entry requirements
  - `**Assessment / certification:**` — how learners are graded + what credential they receive
- **15 vault entries left unchanged** (no website detail page): Private courses without public pages — Child First Aid Blended/Refresher (Eng + Chi), Cookie Baking, Handcrafted Mooncake, Sake Appreciation, Basic Makeup Workshop, Eyelash Extension, Hair Cutting Children/Infant, Hair Cutting Men+Women, Copilot Workshop Private, Drone Bundle, Malay Food Safety variant.
- **10 website pages had no matching vault entry** — mostly duplicates (Excel 2019, Food Hygiene Refresher, multiple makeup/manpower slugs, automation-chatbots2). Tally report at outputs/COURSE_BACKFILL_REPORT.md for Mark's review — discussion needed on which (if any) deserve new vault entries.
- **Files modified (30):** All 9 catch-all course files (admin-hr, beauty, cleaning, drone-media, ecommerce, first-aid, ms-office, other, private-workshops), all 8 food-safety single-course files, all 5 maintenance single-course files, all 3 baking-cooking single-course files (dim-sum-delights, basic-peranakan-cuisines, artisan-decorative-breads), all 5 ai-tech single-course files.
- **Known noise:** Some "Assessment / certification" bullets have trailing bleed from the website's Course Details / FAQ panels (regex couldn't always find the section boundary cleanly). Content is raw website prose, not yet rephrased into Cassie's warm-but-concise voice. Truncation cap 400-500 chars per field — some content cut mid-sentence. All cleanup-able in a follow-up pass; doesn't block answering most questions correctly today.
- **Vault size impact:** System prompt was ~28K tokens before. Each enriched block adds ~1.5-2K chars. Catch-all files grew most: cleaning-courses.md 4KB → 14KB, beauty-courses.md 2KB → 5KB. Net vault growth ~50K chars (~13K tokens). System prompt now ~41K tokens; still well under context window but worth monitoring cache_read efficiency.

---

## [2026-05-31] update | Persona Rule 3 tightened + server loop-guard bumped (Excel-PSEA failure mode fix)

- **Smoke test surfaced a real failure:** `"Is the Excel basic course PSEA eligible?"` → Cassie made 3 tool calls in a row (`Excel Basic` → fail, `Workplace Productivity using Excel Basic` → fail, `Excel` → ambiguous with 3 matches), then server's loop guard fired with "I ran into a loop trying to answer that."
- **Root cause:** two layers.
  - Persona Rule 3 ambiguous-result handling was too vague ("Present the results, ask user to confirm"). No explicit "STOP retrying" instruction, so model kept blind-guessing query variations.
  - Persona had no instruction for `found: false` (course-not-found, distinct from empty `upcoming_classes`). Cassie defaulted to retry behavior on both.
  - Server `max_tool_rounds = 3` was just-too-few for any worst case (1 weak attempt + 1 better attempt + 1 final ambiguous = 3 rounds, no headroom to process the ambiguous result).
- **Fixes:**
  - **persona Rule 3 rewritten** — replaced 2 vague bullets with 3 explicit cases: `found: false`, `ambiguous: true`, `classes-empty`. Each case spells out: at most 1 retry / no retry / soft fallback. Top of the section now reads "**never blind-retry the tool with different query strings**." Old vague "Ambiguous: Present results, ask to confirm" → "**STOP calling the tool.** Do not try to narrow it down with a more specific query — the user knows what they want better than your guesses."
  - **server `max_tool_rounds` 3 → 5** in cassie-deploy/app/server.py (`get_cassie_reply`). Defence in depth in case persona drift causes a retry anyway. Comment explains the test failure that prompted it.
- **Bumped persona last_updated.**

---

## [2026-05-31] update | Strip per-course funding flags from vault + expand persona Rule 5

- **Follow-up sweep after the price strip.** Mark spotted the same hallucination class applied to UTAP / PSEA / Mid-Career SFC top-up flags: CATS is the operational system that tracks these per course, so the vault should not assert them. Persona Rule 5 already said "PSEA and UTAP eligibility live ONLY in the tool" (line 164) — the vault had been silently contradicting it.
- **Verified gating condition before stripping:** confirmed CATS tool returns `pricing.utap_eligible`, `pricing.psea_eligible`, `pricing.mces_top_up` per course (booleans). Confirmed CATS does NOT surface funding-window end dates (e.g. "Funding until: 1 Dec 2027") — so those `Funding until: X` lines and `funding_expiry:` frontmatter STAY (Mark's rule: only strip what CATS can answer).
- **Surprising finding during verification:** Hair Cutting WSQ (#AB81) vault said "No PSEA" but CATS returns `psea_eligible: true`. Vault was actively wrong, not just stale. After strip this is moot.
- **What got stripped:** every `UTAP eligible / no UTAP`, `PSEA eligible / no PSEA`, `AddSFC eligible`, `Mid-Career SFC eligible / no Mid-Career` per-course line across 7 catch-all course files:
  - `admin-hr/admin-hr-courses.md` — dropped "No UTAP, no PSEA" notes from AB71 + AB72
  - `beauty/beauty-courses.md` — AB81 "SFC eligible, UTAP eligible. No PSEA" → "SFC eligible (WSQ)"; AB82 likewise. Also reworded header.
  - `cleaning/cleaning-courses.md` — 7 entries had "SFC eligible, UTAP eligible, PSEA eligible (+ AddSFC)" → all collapsed to "SFC eligible (WSQ)"
  - `drone-media/drone-media-courses.md` — 4 entries normalised to "SFC eligible (WSQ)"
  - `ecommerce/ecommerce-courses.md` — 2 entries
  - `first-aid/first-aid-courses.md` — header + BCLS+AED dropped "no UTAP, no PSEA"
  - `ms-office/ms-office-courses.md` — 4 entries (AB22/AB23/AB24/AB51) normalised
  - `baking-cooking/private-workshops.md` — header reworded
  - `other/other-courses.md` — already clean (private courses only said "No subsidy")
- **What was KEPT:** `SFC eligible (WSQ)` lines (Mark's call — SFC eligibility is structural to WSQ status, not drift-prone, and helps Cassie answer "is this SkillsFuture eligible?" without a tool call); `Funding until: <date>` lines (CATS doesn't surface); `funding_expiry:` frontmatter on individual course files (CATS doesn't surface); `No subsidy` on Private and Non-WSQ courses (structural — private/non-WSQ courses by definition have no SSG funding).
- **Persona edit:** `cassie-persona.md` Rule 5 title + body updated to cover UTAP / PSEA / Mid-Career SFC top-up explicitly (previously only PSEA + UTAP). Dropped the "Even if a course page mentions funding options..." hedge since vault no longer carries the flags. Added explicit note that WSQ vs Private vs Non-WSQ classification IS safe to quote from vault. Bumped `last_updated`.
- **Header pattern across all catch-all course files**: every page header now ends with "Call `get_course_schedule` for live pricing and UTAP/PSEA/Mid-Career SFC top-up eligibility." — this gives the LLM an explicit pointer at the top of each page so the call habit forms even on questions that don't name pricing directly.
- **Verification:** `grep "UTAP eligible|PSEA eligible|AddSFC|Mid-Career.*eligible|No UTAP|No PSEA"` across `wiki/courses/` returns zero hits.

---

## [2026-05-31] update | Strip $ prices from course vault files (Rule 5 enforcement)

- Phase 3 classifier flagged a BCLS+AED conversation where Cassie hallucinated $163.50 from the vault after a tool failure. Vault is now the only source of truth for prices that contradicted the tool — fixed by removing all $ amounts so vault can't be the source of drift.
- Verified all 19 priced courses ARE retrievable from CATS before stripping (gate condition Mark set).
- Found 7 of 19 vault prices were STALE — Basic Makeup, Children's Hair Cutting, Eyelash, Sake, Basic Computer all drifted (pre-GST vs CATS GST-inclusive); Hair Cutting Women (#OL90) + Men (#OL91) have been merged in CATS into a single SKU #OL93. Vault was actively misleading on these.
- Files edited (5):
  - `wiki/courses/first-aid/first-aid-courses.md` — stripped $ from all 5 entries (BCLS+AED, Child First Aid Blended Eng/Chi, Child First Aid Refresher Eng/Chi). Replaced with "Funding: No subsidy." line + header note pointing to `get_course_schedule`.
  - `wiki/courses/beauty/beauty-courses.md` — stripped $ from 5 entries. Deleted obsolete OL90 + OL91 entries, added merged OL93 entry. Added CATS canonical names for OL87/OL92/OL88 (drift-aware).
  - `wiki/courses/ms-office/ms-office-courses.md` — stripped $ from Copilot Workshop (#AB51A). Renamed from "Copilot Training Workshop" to "Copilot Workshop" to match CATS.
  - `wiki/courses/other/other-courses.md` — stripped $ from Sake (#OL78) and Basic Computer (#OL68).
  - `wiki/courses/baking-cooking/private-workshops.md` — stripped $ from all 6 workshops (Cookie, Shio Pan, Dumpling, Donuts, Pasta, Mooncake).
- Bumped `last_updated: 2026-05-31` on all 5 files.
- Verification: `grep \$\d wiki/courses/` returns zero hits.
- Government scheme constants ($500 SFC baseline, $4000 mid-career top-up, $750 UTAP cap) left alone in funding/ and policies/ — those are MOE/SSG/NTUC facts, not Coursemology fees, and aren't a Rule 5 risk.

---

## [2026-05-29] update | Phase 3 deploy-day fixes — gateway overlay + rolling window + review-priority reframe

- **Deploy hit two real-world issues that ship-day audit didn't predict, plus a product reframe on Mark's intuition.** Documented here in order of when they surfaced.
- **Issue 1 — gateway DNS.** First post-deploy cron run failed with `httpcore.ConnectError: [Errno -3] Temporary failure in name resolution` on `policy-gateway`. Cause: cassie's `.env` has `ANTHROPIC_BASE_URL=http://policy-gateway:8000` (crewmesh gateway). The web container `cassie` is on the gateway network via `docker-compose.gateway.yml` overlay, but `cassie_cron` was never added to the overlay — only on the default Docker network. Fix: added `cassie_cron` block to `docker-compose.gateway.yml` so both containers join the crewmesh-gateway external network. Deploy command became `docker compose -f docker-compose.yml -f docker-compose.gateway.yml up -d --build cassie_cron` (overlay flags + service-specific build to avoid touching the working cassie web service).
- **Issue 2 — date-window misalignment with Cassie's busy hours.** The original "yesterday SGT" default meant the 09:30 SGT cron processed the previous calendar day (00:00-23:59 SGT). But Cassie's busy window is 8pm-8am SGT (after-hours, no live agents), which spans TWO calendar days. The 09:30 cron caught the 8pm-23:59 portion under "yesterday" but the 00:00-08:00 SGT chats sat in TODAY's calendar date and waited 24+ hours for tomorrow's cron. Mark spotted this immediately from his /admin/conversations view — 6 of 7 May 29 chats were unclassified. Fix: switched default to rolling 24h window from NOW(), with 15-min settle to exclude in-progress chats and `topic IS NULL` for idempotency. New flags: `--lookback-hours` (default 24) and `--settle-minutes` (default 15). Kept `--date` and `--backfill` for manual historical runs. Trade-off accepted: 24h window has a sharp left edge — chats that sat unclassified for >24h fall out and need explicit `--date` catch-up. Mark chose not to widen to 48h to keep design tight; one-time deploy-day stragglers got rescued via `--date 2026-05-29`.
- **Reframe — quality_score is review priority, not Cassie's quality grade.** Mark's product insight mid-deploy: the actual goal of grading is to triage the weekly review queue, not to grade Cassie's behaviour on a quality scale. A novel edge-case question Cassie handled fine is worth surfacing because the QUESTION is the lesson (one-handed visitor asking about medical discount was his canonical example). A routine pricing query Cassie handled perfectly is NOT worth a reviewer's time. Score = (NOVELTY of question) + (SEVERITY of any drift from persona/vault), folded into one 1-5 priority signal. Rubric rewritten in `RUBRIC_AND_OUTPUT` with explicit novelty signals (accessibility, multi-policy questions, KB-gap cases, corporate edge cases) alongside the existing drift signals. INTRO_AND_FRAMING repositioned grader as "TRIAGE REVIEWER" not "auditor". Anchors flipped: 1 = SKIP REVIEW (routine, healthy), 5 = TOP PRIORITY (novel + botched, or major drift). Column name `quality_score` kept for schema stability — semantic meaning flipped in the prompt + UI.
- **UI palette + labels flipped to match the new semantic.** Was: 1=red (bad), 5=green (good). Now: 1=grey (skip), 2=green, 3=amber, 4=orange, 5=red (urgent). Eye is drawn to high-priority rows. Same CSS class names (`.grade-N`) for backward compat with existing templates. List view column header "Auto" → "Priority". Detail view row "Auto grade" → "Review priority (higher = more worth a reviewer's time)". Detail view callout "Why this grade" → "Why this priority (auto-triage)". Dashboard topic-table column "Avg quality" → "Avg priority". Dashboard description rewritten so a topic with a high avg priority reads as "edge cases or drift in this topic" instead of "Cassie doing well on this topic".
- **Test harness updated** to three fixtures (ROUTINE / DRIFT / EDGE) matching the new scoring philosophy. ROUTINE should score 1-2 (skip), DRIFT 4-5 (urgent), EDGE 3-5 (worth a look even if Cassie didn't fail). Mark's calibration run after the reframe: ROUTINE=2, DRIFT=5, EDGE=4 — all in target.
- **Calibration discovery — the grader is implicitly auditing the vault for consistency, not just Cassie.** The grader caught Cassie's slightly ambiguous "Singaporeans 21-39 and PRs (50% subsidy)" phrasing, citing `funding/ssg-subsidies.md` line 22. But that line itself says "PRs always qualify regardless of age" — which slightly contradicts `cassie-persona.md` line 156 (`pricing.sc_pr` = "PR aged 21+") AND `funding/pricing-tiers.md` lines 16-17 (which says PR rate is ~30% subsidy, not 50%). Three vault pages disagree about PR subsidy tier and age cutoff. Not a Phase 3 issue — flagging for a later vault-consistency pass. Useful side-effect that's emerging from reference-grounded judging.
- **Verification (deploy day, on production):** `curl -X POST https://chatbot.h5.sg/chat` with ZOBOT_SECRET returned 200 with a clean Cassie reply, 5s round-trip. Confirms web service unaffected by the cron fixes. After Weixing applied gateway overlay + redeploy, expected sequence: backfill --date 2026-05-29 classifies the 7 stragglers, scheduled 09:30 SGT cron fires tomorrow with rolling window and catches everything from the last 24h.
- **Production secret leak risk acknowledged.** Mark pasted ZOBOT_SECRET into chat to let me run the curl test from my sandbox. Treat as compromised; rotate via `openssl rand -hex 32` → update .env → `docker compose restart cassie`.

---

## [2026-05-29] update | Phase 3 v2 — reasoning persistence + auto-migration + local test harness

- **Reasoning is now persisted to cassie_db, not just stdout.** Added `classifier_reasoning TEXT NULL` column to `conversations` table. The CoT audit string Haiku produces (e.g. "Rule 0 violation in turn 3 — visitor sent to coursemology.sg instead of offered a booking link") is written alongside topic + quality_score by `write_review()`. Mark can now spot-check WHY each chat got its score directly in the admin UI.
- **Idempotent auto-migration on every cron run.** `ensure_schema_migrations()` runs at the start of `main()` (skipped in `--dry-run`). It tries the ALTER TABLE; if MySQL returns errno 1060 ("Duplicate column name"), it logs and continues. Any other error propagates. This means the column is added automatically the first time the new code lands on Plesk — no separate ALTER step, no Weixing ask.
- **Detail view surfaces the reasoning** as a "Why this grade (auto-reviewer)" callout between Auto grade and Reviewer grade rows in `/admin/conversations/<chat_id>`. Green left-border + italic text matches the existing reviewer-comment styling so it reads as a similar editorial note. Hidden via `{% if conv.classifier_reasoning %}` when the field is NULL (handles both pre-v2 chats and any chats that fail to grade).
- **Local test harness shipped** at `cassie-deploy/test_grader_local.py`. Two synthetic conversations (one "good" — tool called, link surfaced, correct day-of-week / one "bad" — Rule 0 violation, scrubber fired). Uses the same `make_anthropic_client`, `render_transcript`, `review_conversation` as production. ~$0.01 per run. Lets Mark iterate on the rubric without needing a DB. Calibration heuristic: if good scores 4-5 and bad scores 1-2, rubric is right.
- **`sql/init.sql` updated** to include the new column for fresh installs. The init.sql change is belt-and-braces with the auto-migration: fresh cassie_db deployments get it via init.sql at first MySQL start; existing deployments get it via the cron job's startup migration.
- **Schema-write truncation guard**: `write_review` truncates reasoning at 2000 chars (MySQL TEXT holds 65K but defensive against runaway prompts).
- **Verified locally** (in /tmp because the bash mount keeps catching stale snapshots of cassie-deploy after each Edit cycle — known FUSE quirk, Plesk reads via Docker COPY at build so unaffected):
  - Migration logic: fresh DB → ALTER applied; column exists → errno 1060 swallowed; unrelated errors (e.g. 1146 missing table) correctly propagate.
  - Detail-view template snippet renders the "Why this grade" callout when reasoning is set, hides it when NULL (covers pre-Phase-3 rows and pre-v2 rows). Quality_score=4 example renders cleanly.
- **Action for Mark before push**: just push. No new env vars, no manual DB step. After the next 09:30 SGT cron run, the column exists, every newly-classified conversation has its reasoning visible at `https://chatbot.h5.sg/admin/conversations/<chat_id>?key=<ZOBOT_SECRET>`. The 17 already-classified conversations from before this change will still show "Auto grade: 4/5" but no "Why" callout (their reasoning was never persisted) — to backfill, run `python -m app.nightly_review --backfill --since 2026-05-22 --force` once.

---

## [2026-05-29] update | Phase 3 v2 — reference-grounded grader (vault + persona + adversarial framing + CoT)

- **v1's blind-grader weakness exposed by Mark.** v1's REVIEWER_SYSTEM contained a paraphrased version of Cassie's persona rules. That meant the grader could detect tonal drift and structural drift (clarifying-Q-before-tool, scrubber fires) but could NOT detect: factual hallucinations (wrong prices/dates/course names), canonical Rule 0 violations against the actual persona text, or general-policy errors that contradicted the vault. Treating the grader as a blind judge would have meant low quality_scores correlated mostly with "felt off" rather than "actually wrong".
- **Mark surfaced the confirmation-bias concern**: if grader and Cassie use the same source material, do they tend to agree with each other? Researched the LLM-as-judge literature (arXiv self-preference papers, Snowflake RAG-triad benchmarks, "Judging the Judges" 2025) and split the question into two:
  - **Self-preference bias** (Haiku grading Haiku) IS real but mechanism is *perplexity-based*, not source-based. Judges prefer text that reads naturally to them, regardless of whether they see the source.
  - **Confirmation bias from shared context** is a smaller risk than expected. Reference-based grounding is the STANDARD best practice for catching hallucinations — you need to show the judge the source of truth or you can't audit faithfulness at all.
  - So the two concerns are independent. Vault/persona inclusion addresses hallucinations. Adversarial framing + chain-of-thought address bias.
- **v2 implementation in `cassie-deploy/app/nightly_review.py`:**
  - `_load_vault_text()` + `_load_persona_text()` + `_resolve_path()` mirror server.py's vault loading. Both load lazily on first `review_conversation()` call (so importing the module for tests doesn't require the vault to exist).
  - System prompt restructured as a LIST of 4 cacheable content blocks (Anthropic's `cache_control={"type":"ephemeral"}` per block). Order is intro → persona → vault → rubric so the most-iterated content (rubric) is at the end of the prefix and doesn't invalidate the persona/vault cache when tweaked.
  - `INTRO_AND_FRAMING` block uses ADVERSARIAL framing: "You are an AUDITOR... your job is to FIND PROBLEMS... you are not here to confirm she did well." Includes explicit source-of-truth split: persona/policy/funding-scheme-rules/catalogue come from the VAULT; live prices, specific eligibility checks (per Mark's clarification: PSEA eligibility is per-tool-call not per-vault), specific class dates/availability come from the get_course_schedule TOOL CALLS visible in the transcript.
  - Output JSON now requires a `reasoning` field BEFORE topic + quality_score (chain-of-thought). Forces specific citation of issues. We don't persist reasoning to the DB (Phase 3 v2 scope — could go to `turns.classifier_output_json` later) but log it on every row so spot-checks can see what the grader was thinking.
  - `max_tokens` bumped 200 → 500 to accommodate the reasoning field.
  - `_validate_review()` returns a 3-tuple `(topic, quality_score, reasoning)`. Bad single conversations still log-and-skip without killing the batch.
- **Cost projection** (with prompt caching, after the first call in each batch warms the cache): vault ~18.9k cached tokens + persona ~5k cached + intro/rubric ~1k = ~25k cached tokens per call, plus 1-3k uncached transcript, plus ~500 output. At Haiku 4.5 cache-read pricing (~10% of full input) → ~$0.005/call → ~$1.50/month at current volume. Up from v1's ~$0.30-0.50/month, still well below the original Phase 3 infographic budget.
- **Mitigation choices**:
  - Stayed on Haiku (Mark's call). Sonnet would mitigate self-preference bias more strongly but at 3x cost; Haiku + adversarial framing + CoT is the cheaper compromise.
  - Did NOT add a multi-judge ensemble — overkill for the volume.
  - DID add periodic-human-calibration to the operational plan (already in the infographic): spot-check 5 quality_score=1 and 5 quality_score=5 each calibration round.
- **Verified locally** (in /tmp because the bash mount got stuck on a stale 25KB snapshot of `nightly_review.py` partway through the edits — known recurring FUSE issue, Plesk reads via Docker COPY so unaffected):
  - F-string with `{{`/`}}` literal braces + `{', '.join(TOPICS)}` substitution compiles in Python 3.10.
  - Vault loader pulls 54 wiki files (~75k chars, ~18.9k tokens).
  - Persona loader pulls ~20k chars (~5k tokens).
  - Validator accepts the new `reasoning` field, correctly rejects invented topics + out-of-range scores.
  - 4-block cacheable system prompt structures correctly; graceful degradation to 2 blocks (intro + rubric) when vault/persona files missing.
- **CLI is unchanged**: `--date / --backfill --since / --force / --dry-run / --limit` all work as before. Cron schedule unchanged (09:30 SGT). Dashboard topic panel unchanged.
- **Action for Mark before push**: same as v1 — nothing new to provision. Push cassie-deploy, ask Weixing to rebuild. After deploy, recommended smoke sequence:
  ```bash
  # First run on real chats, no DB write — reads vault+persona, calls Haiku, prints reasoning
  docker compose exec cassie_cron python -m app.nightly_review --backfill --since 2026-05-27 --dry-run --limit 3
  # Spot-check the reasoning field. If grader is being too lenient, tweak RUBRIC_AND_OUTPUT and re-run.
  # When happy, drop --dry-run.
  ```

---

## [2026-05-29] update | Phase 3 v1 feedback loop built (nightly classifier + grader + dashboard topic panel)

- **Single-call design.** One Haiku call per conversation returns BOTH `topic` and `quality_score` in one JSON response (cheaper than two calls; rubric stays coherent). New file `cassie-deploy/app/nightly_review.py` (~430 lines). Mirrors `aggregate_daily.py` patterns: `pymysql` + `dotenv`, SGT-aware date math, `--date / --backfill --since / --force / --dry-run / --limit` CLI.
- **Topic taxonomy locked to 10 categories from the Phase 3 infographic**: registration, pricing, funding, schedule, location, refund_cancel, corporate, complaint, off_topic, casual_greeting. Single source of truth in `TOPICS` constant; the reviewer prompt references it via f-string so the list never drifts.
- **Quality rubric anchors persona rules** Mark and Claude have been iterating since 5/21: Rule 0 (booking channel not brochure), Rule 1 (tool-call on specific course mention), Rule 3 (day_of_week + is_weekend from tool output, never hallucinated dates), Rule 5 (no raw URLs — scrubber_fired=true is a meaningful penalty), tone (warm first turn, brief follow-ups, no em dashes). Anchor points (1-5) make the scale stable. Short casual_greeting/off_topic chats default to 3 to keep the distribution honest.
- **Re-run policy**: only NULL `topic` rows are reviewed by default (idempotent, safe to re-run). `--force` re-grades regardless — used after rubric tweaks to apply the new rubric to history.
- **Conversation-level only** for now: `turns.classifier_output_json` deliberately NOT populated. Per-turn intent/outcome tagging deferred until a concrete consumer surfaces (probably Phase 5 pattern mining).
- **Anthropic client honours env vars** the same way `app/server.py` does — reads `ANTHROPIC_API_KEY` + optional `ANTHROPIC_BASE_URL`. If Mark ever turns the crewmesh gateway overlay back on, classifier traffic flows through it for free. Model: `claude-haiku-4-5-20251001` (same as Cassie's main loop).
- **Transcript rendering**: each turn becomes a labelled line (`[USER] ... / [CASSIE] ... / [TOOL: name] args=... result=...`). Tool result JSON is pretty-printed and truncated to 1200 chars per call so a single chatty get_course_schedule run doesn't blow up the prompt. `scrubber_fired=true` is appended to the `[CASSIE]` line so the reviewer sees that signal.
- **JSON parser is forgiving** — tries a direct `json.loads` first, falls back to first balanced `{…}` regex match for cases where Haiku wraps in code fences. `_validate_review` rejects unknown topics, non-int quality_score, and out-of-range scores; bad single conversations log + skip without killing the batch.
- **Cron entry added** to `docker/crontab`: `30 1 * * *` UTC = **09:30 SGT** (30 min after Phase 2 aggregator). Phase 2 doesn't read `topic`, so they're independent; running AFTER avoids any DB contention and ensures the day's daily_stats row exists by the time Phase 3 touches the same range. No Phase 2 file changes — the cron service rebuilds with the new module automatically because the existing Dockerfile already `COPY app/ ./app/`.
- **`/admin/dashboard` now shows a topic breakdown card** above the existing trend charts. Live GROUP BY on `conversations.topic` over the same 30-day window the rest of the dashboard uses. Two-pane layout: Chart.js doughnut on the left, table of (topic / count / avg quality with grade-N colour band) on the right. Card is hidden via `{% if topic_rows %}` when Phase 3 hasn't classified anything yet, so the page never renders a misleading "100% unclassified" doughnut. A small "X conversation(s) still unclassified" note appears when relevant. No schema change; no daily_stats column added — Phase 2 stays untouched.
- **Verified locally**: `py_compile` clean on both files. Transcript renderer unit-tested with mixed roles (user/cassie/tool/scrubber). JSON extractor handles raw JSON + code-fence wrapping. `_validate_review` correctly rejects 4 categories of bad input. Dashboard Jinja template renders cleanly in 3 scenarios (Phase 3 populated / Phase 3 empty but Phase 2 populated / total empty state). The doughnut chart only instantiates client-side when `TOPIC_COUNTS.length > 0`.
- **Bash-mount staleness recurred** during template verification — a single trailing NULL byte appeared on the bash-side view of `app/admin_routes.py` after the edits, breaking standalone `python3` imports there. The actual file on Windows side and the Read tool view are both clean (verified). Plesk reads via Docker COPY at build time so production is unaffected. Same recurring pattern as Phase 1 and Phase 2 verification days; documented in project memory.
- **Cost**: per Phase 3 infographic projection, ~$0.001/chat = ~$0.30-0.50/month at current volume (~10 chats/day). System prompt + transcript ~6-10k input tokens; `max_tokens=200` on the output keeps cost predictable.
- **Action for Mark before push**: nothing new to provision — `ANTHROPIC_API_KEY` already in `.env`, cron service already running. Just push `cassie-deploy` and ask Weixing to rebuild. First nightly run will pick up yesterday's chats at 09:30 SGT. To populate immediately: `docker compose exec cassie_cron python -m app.nightly_review --backfill --since 2026-05-22 --dry-run` first to sanity-check Haiku's grades; then drop `--dry-run`.

---

## [2026-05-28] update | Phase 2 feedback loop built (daily aggregator + Zoho client + /admin/dashboard) and cassie-deploy folder reorganized

- **Zoho probe done end-to-end.** Discovered the actual data path Cassie's attribution travels: `utm_chat=cassie` lands on Zoho's **Contacts** module (custom field `UTM_Chat`), NOT on Deals. To filter Cassie-attributed deals, COQL-JOIN through `Contact_Name.UTM_Chat = 'cassie'`. Confirmed 6 all-time Cassie deals exist (started 2026-05-22 — exact match for when utm_chat was added to the URL). Stage breakdown: 2 Enquiry, 1 Class, 3 Cold Deal, 0 Closed Won (so dashboard's revenue column will be $0 for a while — that's correct).
- **Surprising gotcha #1:** there's a Deals-module field with api_name `NRIC` and display label "UTM Chat". It is NOT the utm_chat field — it actually holds real Singapore NRICs (`S8899493J` etc.). Leftover from some never-finished integration. Ignore it.
- **Surprising gotcha #2:** money field is `Course_Fee` (double), NOT the standard `Amount`. Coursemology's Zoho never populates `Amount`. Revenue queries `SUM(Course_Fee)`.
- **Surprising gotcha #3:** Cassie deals come in two flavors — `"SalesIQ Chat"` (auto-created on widget chat, top-of-funnel noise) and `"Class Booking For ..."` (form-submitted bookings, real conversions). We filter `Lead_Sources = 'Class Booking'` to count only conversions.
- **Surprising gotcha #4:** COQL doesn't support `LIKE`. Use `=` only.
- **OAuth setup completed.** Self Client at api-console.zoho.com (US data center, .com not .com.sg). Refresh token has scopes: `ZohoCRM.modules.deals.READ,ZohoCRM.modules.contacts.READ,ZohoCRM.coql.READ,ZohoCRM.settings.fields.READ`. Two refresh token regenerations during the session — first one only had Deals + settings scopes (sufficient for probing fields metadata but not for the JOIN query), second has the full set we need.
- **Phase 2 code lands in `cassie-deploy/`:**
  - NEW `app/zoho_client.py` — OAuth + COQL helpers. `count_cassie_class_bookings_created_on(date)` + `sum_cassie_closed_won_revenue_on(date)`.
  - NEW `app/aggregate_daily.py` — cron entry. Aggregates internal metrics (convs, turns, link rate, tool rate, scrubber fire rate, avg latency) + pulls Zoho cols, UPSERTs daily_stats. SGT-aware date math (`SGT = UTC+8`, fixed). Supports `--backfill --since YYYY-MM-DD`. Zoho failures don't break the run.
  - EXTENDED `app/admin_routes.py` — new `/admin/dashboard` route with Chart.js (CDN). KPI strip + 7 trend charts (convs, link rate, tool rate, scrubber rate, latency, Zoho deals, Zoho revenue). Cross-links between `/admin/conversations` and `/admin/dashboard` added.
  - NEW `cassie_cron` service in `docker-compose.yml`. Uses same image as cassie (supercronic installed in shared Dockerfile). Schedule: `0 1 * * *` UTC = **09:00 SGT** (corrected from earlier 10am plan — Phase 2 no longer depends on Phase 3, so it can run at 9am).
  - UPDATED `docker/Dockerfile` (formerly `Dockerfile` at root) — added supercronic + tini + tzdata; switched to `COPY app/ ./app/`; CMD = `gunicorn ... app.server:application`.
- **Folder reorg done in same push** (Mark explicitly asked — flat root was getting messy):
  - `cassie_server.py` → `app/server.py` (also renamed since `cassie_` prefix is redundant inside a package)
  - `db_logger.py` → `app/db_logger.py`
  - `admin_routes.py` → `app/admin_routes.py`
  - `Dockerfile` → `docker/Dockerfile`
  - `init.sql` → `sql/init.sql`
  - Added `app/__init__.py` (package marker), `docker/crontab` (supercronic schedule)
  - `docker-compose.yml` kept at root per Mark's call (standard convention; cleanest for `docker compose up` ergonomics)
  - All imports updated to `from app.foo import ...`. Vault path resolution unchanged — existing `_resolve_path` fallback chain handles the new `Path(__file__).parent.parent` location automatically.
- **Action for Mark before push**: git index in cassie-deploy got corrupted during the file reorg (first git mv succeeded, subsequent ones left .git/index in bad state). Recovery: `rm .git/index.lock .git/index; git reset HEAD; git add -A; git commit; git push`.
- **Action for Mark on Plesk before first cron run**: add the 3 Zoho env vars to `.env` (values in project memory + the conversation). Until added, aggregator stores NULL for zoho_cassie_* cols (graceful degradation, internal metrics still work).
- **Production verification sequence** (after Weixing rebuilds): `docker compose ps` → all 3 services up; `docker compose exec cassie_cron python -m app.aggregate_daily --backfill --since 2026-05-28` → backfills today; check daily_stats has rows; visit `https://chatbot.h5.sg/admin/dashboard?key=<ZOBOT_SECRET>` → charts render.
- **Bash-mount staleness recurred** during smoke-test syntax verification. `py_compile` reported a spurious SyntaxError on admin_routes.py — actually fine per Read-tool inspection (file is 830 lines, dashboard handler ends cleanly at line 830). Same pattern as Phase 1 verification day. Confirmed harmless via structural Read at lines 410-461 and 464-830.

---

## [2026-05-26] update | Two production fixes from last night's SalesIQ review (classifier course-blindness + em dash AI-tell)

- **Problem 1: classifier blocked legitimate course noun phrases.** Two confirmed cases: "Dumpling making" (image 1 from Mark's review) and "Microsoft Word" (reported earlier). Classifier prompt had no awareness of Coursemology's actual catalogue, so course names that sound like recipes/hobbies in isolation were treated as off-topic. Worst part: persona ALREADY had a "Dumpling making" example flow (line 236-239) that gracefully says "we don't run that, but we have artisan bread, want to see that?" — but the classifier intercepts before that designed behaviour can fire. Visitor sees the cold deflection and bounces.
- **Fix**: edited `CLASSIFIER_SYSTEM` in `cassie-deploy/cassie_server.py` to:
  - Lead with an exhaustive list of Coursemology's course categories (food safety, baking, vehicle maintenance, AI/tech, MS Office, cleaning, admin/HR, first aid, beauty/hair, drone/media, ecommerce, other workshops) with example phrasings under each.
  - Add an explicit "any short noun phrase under 5 words → default ALLOW" rule.
  - Add a section "Examples of messages that MUST be ALLOWED (these have all been wrongly blocked in the past)" listing dumpling, microsoft word, drone, sake, makeup, hair cutting, AED, dim sum, aircon, EV, shopee, powerpoint.
  - Strengthen the golden rule: blocking a genuine enquiry is FAR worse than letting an off-topic message through (Cassie can deflect it gracefully herself).
- **Problem 2: Haryo flagged em dashes (—) as obvious AI tell.** Looking at second image, Cassie's reply used multiple em dashes in a single short message. Root cause: the persona file itself had ~50 em dashes, which Haiku was faithfully imitating. Telling Haiku "don't use em dashes" while showing it 50 of them in the system prompt would never stick.
- **Fix**:
  - Added new top-of-list rule in `cassie-persona.md` Response Style section: "Never use em dashes." Explains what an em dash is, why it reads as AI, and what to use instead (commas, hyphens with spaces, parentheses, new sentences).
  - Stripped em dashes throughout the entire persona file — every em dash replaced with a context-appropriate alternative (comma / period / colon / parens). Only one em dash remains in the persona, inside the rule definition itself so Haiku can identify the character. En dashes (–) for ranges like "21–39" or "19–21 June" preserved.
  - **No server-side regex scrubber.** Mark explicitly declined defence-in-depth on this one — wants Cassie to follow the persona rule directly rather than have us mangle her output post-hoc.
- **Verification**: ran `python3 -c "import ast; ast.parse(...)"` on the modified server file — syntax OK. Grep on persona confirms only the one intentional em dash remains (line 56, inside the rule definition).
- **Next**: Mark to deploy the changes to Render and watch SalesIQ closed-chats over the next day or two for both (a) zero false-blocks on course noun phrases and (b) zero em dashes in Cassie's replies.

## [2026-05-27] update | Phase 1 complete — db_logger + /admin/conversations admin pages

- **Phase 1 Python integration landed.** Three new files in `cassie-deploy/`:
  1. **`db_logger.py`** (343 lines) — background-thread queue + MySQL writer with JSONL fallback file. `DBLogger.log_turn()` is non-blocking; the daemon thread drains the queue and writes to cassie_db. On MySQL failure, events spill to `/app/db_fallback/queue.jsonl` (on the `cassie_fallback_data` Docker volume). The fallback file is auto-drained on worker startup AND on every successful write after a failure. Module-level singleton `db_logger` started once on app boot.
  2. **`admin_routes.py`** (457 lines) — Flask Blueprint with `/admin/conversations` (list view with date/topic/status/has-link/search filters + pagination) and `/admin/conversations/<chat_id>` (detail view with full transcript, tool call args/results, scrubber-fire flags, per-turn latency + token counts). Templates inline via Jinja2 `render_template_string`. Auth via `X-Chat-Key` header OR `?key=` query param using existing `ZOBOT_SECRET`.
  3. **`cassie_server.py`** modified — added `import time`, imports for `db_logger` + `admin_bp`, started logger after `app = Flask(__name__)`, registered admin blueprint, added 4 `db_logger.log_turn()` calls in `get_cassie_reply()` (one for user turn at entry, one for cassie tool-use turn, one per tool call, one for cassie final reply with `scrubber_fired` + `contained_booking_link` flags).
- **`Dockerfile` updated** to COPY the two new Python files alongside cassie_server.py.
- **Schema unchanged** — all writes target the existing `conversations` + `turns` tables created in Phase 1 scaffolding. UPSERT on `conversations.salesiq_chat_id` increments `total_turns` on every turn, ORs in `contained_booking_link`, COALESCEs in `visitor_id_hash` if not previously set.
- **Bash-mount staleness recurred** during syntax verification — bash sandbox saw a truncated 1297-line copy of cassie_server.py while Read tool saw the correct 1314+ lines. Confirmed all edits landed correctly via grep. This is harmless for Plesk deployment (Plesk reads the real file).
- **Action for Mark**: push `cassie-deploy` to GitHub. Once friend rebuilds Docker, verify the 6-step Phase 1 checklist from PHASE1_PLAN.md (MySQL healthy → schema created → cassie connects on startup → real chat writes a row → async non-blocking on DB outage → /admin/conversations renders).

## [2026-05-26] update | Phase docs collated in cassie-deploy/misc/, README updated, Lark lifecycle refined for push

- **5 phase infographics created in `cassie-deploy/misc/`**: phase-1-logging-foundation, phase-2-metrics-dashboard, phase-3-classifier-grader, phase-4-lark-review, phase-5-pattern-synthesis. Each self-contained HTML, no chat-specific context, purely factual.
- **Plus 2 reference docs in `cassie-deploy/misc/`**: feedback-loop-architecture.html (overview, schema, 8-step weekly cycle) and column-lifecycle.html (7-stage column-level data flow).
- **README rewritten** for cassie-deploy: feedback-loop section with full phase table + status, references to all misc/ files, setup steps include MYSQL_ROOT_PASSWORD + DB_PASSWORD + backup cron, endpoints table covers existing + Phase 1/2/4 admin endpoints, architecture diagram updated to show cassie_db.
- **Design refinements landed this session**:
  - Lark Base "Archived" status added (Status: Unreviewed → In Progress → Reviewed → Archived). The /admin/weekly-export endpoint flips records to Archived after sync; Lark Form view filters Archived out so reviewer queue stays clean. No table reset needed.
  - On-demand sync (was nightly cron in v2): /admin/weekly-export now does pull-from-Lark + update-cassie_db + flip-to-Archived + return-markdown in one idempotent call. Removed pull_from_lark.py nightly cron from Phase 4 scope.
  - Conversation-level granularity in Lark confirmed (not turn-level). One record = one full conversation. Reviewer Comment free text allows turn-level callouts when needed. Rejected turn-level granularity because it'd 5-10x records and lose context.
  - Three admin endpoints total: /admin/conversations (Phase 1, browse + filters), /admin/dashboard (Phase 2, Chart.js KPIs), /admin/weekly-export (Phase 4, Claude-paste digest). All auth-gated via ZOBOT_SECRET.
- **Action for Mark**: pushing `cassie-deploy` to GitHub tonight with current state. Phase 1 Python integration deferred to next session — schema is ready but no code is writing to it yet, so functional Cassie behaviour is unchanged. Friend can rebuild Docker safely at any time; cassie_db container will spin up cleanly and sit idle until db_logger.py is added next session.

## [2026-05-26] update | Lark chosen over Airtable; cron-to-Lark mechanics designed; column-lifecycle diagram drafted

- **Reviewer interface decision: Lark Base.** Mark weighed Lark vs Airtable; Lark wins because (a) Weixing AND Xingjian already use it (zero onboarding for the team), (b) free tier has generous record cap vs Airtable's 1,000-record limit which we'd hit in ~3 months, (c) Singapore data centers (PDPA-friendly). Tradeoff acknowledged: Airtable has objectively better reviewer UX, but migration is half a day if Lark turns out to be a problem. Plan: set up Lark Base "Form view" so reviewers don't see a scary spreadsheet grid.
- **Cron-to-Lark mechanics designed (Phase 4)**: nightly cron script lives in cassie-deploy. Either a `cassie_cron` Docker service or Plesk system cron. Auth pattern: `app_id + app_secret` → `tenant_access_token` (2hr lifetime, SDK auto-refreshes) → POST records to Lark Base via REST. 4 new env vars Weixing provisions in Lark Developer Console (LARK_APP_ID, LARK_APP_SECRET, LARK_BASE_TOKEN, LARK_TABLE_ID). App scope: minimum needed (read/write only the one Base). Idempotency: cron checks `review_status='unreviewed'` before pushing, sets to `'in_review'` after success. PII redaction (regex NRIC/email/phone) BEFORE sending to Lark — reviewers never see raw PII.
- **Column-lifecycle diagram drafted** at `cassie-column-lifecycle.html`. 7 stages from "all-day Cassie chats" through "weekly Mark+Claude review" showing exactly which columns get Written/Read/Updated at each stage, in cassie_db AND Lark AND Zoho. Includes a cheat sheet at the bottom grouping columns by lifecycle pattern. Mark requested this because he was getting confused about how each column flows through the weekly loop.
- **Memory updated** — project_cassie_chatbot.md now reflects Phase 1 scaffolding done (4/6) + Lark decision + cron design + column lifecycle reference.
- **Three workspace artifacts ready for Weixing review**:
  1. `cassie-feedback-loop-architecture.html` — v2 architecture (decoupled, Lark, Zoho aggregation)
  2. `cassie-phase1-implementation.html` — Phase 1 infographic with 4/6 status progress bar
  3. `cassie-column-lifecycle.html` — column-by-column lifecycle through the weekly loop
- **Action for Mark**: send all three artifacts to Weixing for his eyes-on-design pass before any code goes live. Next session: complete the remaining 2 Phase 1 tasks (db_logger.py + /admin/conversations) so Weixing can rebuild Docker with a fully-wired system.

## [2026-05-25] update | Phase 1 infrastructure scaffolding — schema, docker-compose, env (Python integration deferred)

- **Started Phase 1 of the feedback loop**. Four files added/modified in `cassie-deploy/`:
  1. **NEW `PHASE1_PLAN.md`** — shareable plan doc covering scope, file changes, deploy sequence, Weixing's ask, verification checkpoints, backup strategy, rollback plan, and open decisions. Mark can show this to Weixing alongside the v2 architecture diagram.
  2. **NEW `init.sql`** — full schema (conversations + turns + daily_stats tables). Heavily commented to teach Mark MySQL concepts (InnoDB engine, ACID, indexes, composite indexes, foreign keys with CASCADE, JSON columns, ENUM, utf8mb4 for emojis). Auto-runs on first `cassie_db` container start via `/docker-entrypoint-initdb.d/`. Seeds one empty `daily_stats` row for today.
  3. **MODIFIED `docker-compose.yml`** — added `cassie_db` service (mysql:8.0, no public port, healthcheck, init.sql mount); added `cassie_db_data` and `cassie_fallback_data` named volumes; added DB env vars to `cassie` service; added `depends_on: condition: service_healthy` so Cassie waits for MySQL ready. Loopback-only port pattern on the cassie service preserved.
  4. **MODIFIED `requirements.txt`** — added `pymysql>=1.1.0` (pure-Python driver, no compilation needed).
  5. **MODIFIED `.env.example`** — documented the two new required vars (`MYSQL_ROOT_PASSWORD`, `DB_PASSWORD`) + noted the other DB connection vars are wired via docker-compose env not .env.
- **Deferred to next session (Phase 1 part 2)**: the actual Python integration — `db_logger.py` module (background-thread queue, async writes, local fallback file drain logic) + hooks into `get_cassie_reply()` + new `/admin/conversations` endpoint. These are bigger changes that deserve a focused session.
- **Schema decisions worth flagging**:
  - `conversations.salesiq_chat_id` is UNIQUE-indexed → no duplicate conversation rows even if SalesIQ retries a webhook.
  - `turns` uses BIGINT PK because turns grow ~5× faster than conversations.
  - `visitor_id_hash` stores SHA-256 of the visitor ID — never the raw ID. Privacy default.
  - `topic`, `quality_score`, `review_status`, `reviewer_grade`, `reviewer_comment` are all nullable so Phase 1 can write rows without any nightly classifier yet running.
  - Foreign key on `turns.conversation_id` with `ON DELETE CASCADE` — deleting a conversation auto-deletes its turns.
- **Open decisions documented in PHASE1_PLAN.md** (defaults picked, can revisit): MySQL 8.0 vs MariaDB; single .env vs separate DB env file; auth scheme for `/admin/conversations` (ZOBOT_SECRET reuse for now).
- **Action for Mark**: skim the four changes, push to `architechsg/cassie-deploy` when comfortable, but DON'T have Weixing rebuild yet — the Python integration in the next session needs to land before rebuild so we don't have a half-wired system in prod. (Alternative: push to a feature branch and let Weixing eyeball it.)

## [2026-05-25] update | Feedback-loop architecture v2 after Weixing's feedback — decoupled from CATS, Zoho-aggregate attribution

- **Weixing reviewed the v1 proposal (sent 2026-05-24) and pushed back on the cross-DB JOIN** for principled security reasons. His direct quote: *"a customer-facing AI solution should never have access to operational DB in any way. We can expose it via api / dedicated tools."* Also his rule of thumb: *"avoid touching the main database unless we absolutely need to. Try to decouple the bot from main business logic."* Both correct. Mark accepted on security grounds.
- **Key context I (Claude) was missing**: visitor-level tracking is already implemented via UTM cookies in Zoho — a unique ID is generated when a visitor opens the website, follows them through page views, sign-up, and course completion. So per-conversation attribution doesn't need to be invented from scratch; it's a piping problem (Zoho → somewhere queryable). Mark noted this tracking column doesn't currently land in MySQL `class_registration` — would need OLA logic change to accept and persist. Mark agreed this is nice-to-have, not blocker.
- **Decisions agreed**:
  - **DB moves into cassie_server's docker-compose** (MySQL container alongside cassie_server.py). NOT a database on s2.architech.sg. Weixing endorsed: *"You can add a db component in docker compose to start using it right away."*
  - **No cross-DB JOIN** — the "killer feature" of the v1 plan is dropped. Cassie's DB is fully decoupled from CATS.
  - **Attribution via Zoho aggregate** for Phase 1 (daily cron pulls Cassie-attributed deal totals into `daily_stats`). Per-conversation attribution deferred to Phase 5 (would need CATS API endpoint OR Xingjian's monitoring setup to surface Zoho's UTM tracking).
  - **Review interface = Lark Base** (not Airtable). Weixing flagged Airtable's 1k record free-tier limit; Lark is what their team uses, Singapore-popular, more generous free tier. Sheets + n8n is the fallback.
  - **Xingjian mentioned setting up website tracing as part of monitoring** — if that happens, we get the per-conversation tracking for free.
- **Revised phase plan**: P1 logging foundation (Docker compose MySQL + async writes) → P2 dashboard + Zoho-aggregate stats → P3 nightly classifier + grader → P4 Lark Base review interface → P5 (deferred) per-conversation attribution if needed.
- **Diagram updated to v2** at `cassie-feedback-loop-architecture.html`:
  - Section 1: cassie_db is now inside the chatbot.h5.sg docker-compose, not on s2.architech.sg. Added a "Decoupled from CATS" callout explaining the API-only access principle.
  - Section 2: dropped the cross-DB schema panel; added a `daily_stats` table with `zoho_cassie_deals` and `zoho_cassie_revenue` columns. SQL example replaced with "how we get conversion data without touching CATS DB" + Zoho cron explanation.
  - Section 3: step 4 updated from "Push to Airtable" → "Push to Lark Base", step 5 updated from "Dad" → "Mr. Wee" (more respectful framing for sharing externally).
  - Weixing's ask box rewritten: nothing to provision on s2.architech.sg; just sanity-check the docker-compose change; Zoho API credentials are the only future ask.
  - Added a new "Key principles agreed" callout at the bottom listing the four decisions Mark and Weixing landed on.
- **Action for Mark**: send the v2 HTML to Weixing for final sign-off, then start Phase 1 (docker-compose MySQL container + async logging from cassie_server.py).

## [2026-05-24] update | Feedback-loop architecture proposal drafted for Weixing review

- **Context**: current Cassie improvement loop is fully manual — Mark scrolls SalesIQ closed-chats every few days, picks issues, brings to Claude. Inefficient and biased toward whatever Mark happens to see. Proposed automating selection + adding human-in-loop review by Mr. Wee + live agents.
- **Architecture agreed in chat**: log every Cassie turn to a new `cmlg_cassie` MySQL schema on s2.architech.sg (alongside CATS's existing `cmlg_staging`). Async writes from `cassie_server.py` with local fallback file for resilience. Nightly cron classifies + grades each chat via Haiku, picks worst-per-topic + outcome-regret + KB-gap chats, pushes top 10–15 to Airtable for Mr. Wee + live agents to grade & comment. Mark exports reviewed comments weekly, brings to Claude for persona/KB diffs.
- **Killer feature**: JOIN between `cmlg_cassie.conversations` and `cmlg_staging.class_registration` on `utm_chat` → can finally measure real paid-booking conversion, not just link clicks. `utm_chat=cassie` parameter already on booking URLs (since 2026-05-22 fix), so no booking-link changes needed.
- **Initial DB recommendation was SQLite (lazy default)**; Mark pushed back, MySQL is the right call because (a) reuses existing infra, (b) Weixing knows it, (c) enables the JOIN.
- **Phase plan**: P1 logging foundation (week 1) → P2 metrics dashboard (week 2) → P3 nightly classifier + grader (week 3) → P4 Airtable review interface (week 4) → P5 pattern synthesis (later, only if needed).
- **Deliverable**: architecture diagram saved at `cassie-feedback-loop-architecture.html` (workspace root). Three sections: runtime data flow, DB schema with JOIN example SQL, daily/weekly review cycle. Bottom callout lists what's needed from Weixing (~30 min of his time: create DB, grant user, sanity-check schema, confirm utm_chat capture into class_registration).
- **Action for Mark**: share the HTML with Weixing, get his sign-off (or pushback) on the schema + JOIN approach. Once approved, Phase 1 implementation starts.

## [2026-05-24] update | First-turn warmth — opening reply gets 2–3 sentences instead of curt one-liner

- **Trigger**: Mark felt the new canonical "How do I register?" reply ("I can help you book right here — what course are you interested in?") was too short and direct for the *first* substantive reply in a conversation. Read as customer-service-y / cold for a moment that's actually trust-building.
- **Principle added**: brevity is still the default for follow-up turns and factual answers, BUT the opening reply (especially when the visitor hasn't given Cassie a concrete course or topic yet — e.g. tapped a generic chip) deserves 2–3 sentences: warm acknowledgement → what Cassie can do → funnel question. After the first turn, snap back to brevity.
- **Edits to `cassie-persona.md`**:
  1. **Response Style** — new bullet "Exception — first-turn warmth" added directly under the "Be brief" bullet so the brevity rule still leads but the exception is unmissable.
  2. **Rule 0** — "Shape of the right answer" updated to the warmer 3-sentence version Mark picked: *"Great question! The easiest way is to just tell me which course you're interested in — I can pull up the next available class right here and send you a booking link that pre-fills the registration form for you. What are you looking to learn?"* Cross-reference to first-turn warmth added.
  3. **Example Flows — "How do I register?"** — canonical updated to match Rule 0. Annotation added noting this is opening-turn warmth and that follow-ups stay brief.
- **Action for Mark**: re-push `cassie-vault` and ask friend to rebuild Docker so the persona is reloaded. Then re-run test A1–A5 from the test set — same pass criteria (don't send to website) but the pass shape is now the longer warmer reply, not the one-liner.

## [2026-05-24] update | Cassie reframed as booking channel (not brochure) — persona + registration FAQ rewritten

- **Trigger**: two production chats where users tapped the SalesIQ chip "How do I register for a class?". Cassie answered correctly per the KB — but the KB and persona were written before the booking-link/token system existed. She told visitors to go to coursemology.sg and click "Book Class" themselves, instead of offering to generate a pre-filled booking link via `get_course_schedule`. Conversion KPI undermined.
- **Diagnosis**: `wiki/faq/registration.md` Q1 was literally telling Cassie to send users to the website. `cassie-persona.md` reinforced this with "What you CANNOT do → Make or confirm bookings" — which framed booking as off-Cassie rather than as the *purpose* of every course-interest conversation.
- **Fixes (single coherent commit)**:
  1. **`wiki/faq/registration.md` Q1 rewritten** — now leads with "I can help you book directly here — just tell me which course you're interested in" before mentioning the website as a self-serve fallback.
  2. **`cassie-persona.md` — Mission section added** (above Personality): states Cassie's primary purpose is to hand visitors a booking link, that she IS the booking channel not a brochure, and that friction reduction (not sales pressure) is the value prop.
  3. **`cassie-persona.md` — "What you CANNOT do" rewritten**: removed "Make or confirm bookings" (misleading); replaced with the actual limits — can't process payment, can't modify existing bookings, can't handle bulk corporate. Generating booking links IS booking.
  4. **`cassie-persona.md` — Rule 0 added** (above Rule 1): "You are the booking channel, not a brochure". Names the shape of the right answer for "how do I register?" + lists forbidden phrases ("go to coursemology.sg", "find your course on the website", "click Book Class on the course page") + lists when website mentions ARE acceptable (visitor explicitly wants to browse, info genuinely out-of-scope, post-booking).
  5. **`cassie-persona.md` — Rule 6 added** (after Rule 5): soft funnel after factual answers. One short follow-up offer max ("Want me to find the next available class?") — not after every answer, not chained.
  6. **`cassie-persona.md` — Example Flows section appended** (after Booking Links): canonical shapes for "how do I register?", "tell me about your courses", "Dumpling making" (no-such-course case — call tool first, then offer closest alternative; never deflect with "outside what I can help with"), "Excel" (specific course), "How do I cancel?" (correctly off-Cassie), "How much is food safety?" (pricing is in tool).
- **Both files updated `last_updated` to 2026-05-24**.
- **Action for Mark**: push `cassie-vault` AND `cassie-deploy` (persona is baked into `cassie_server.py` system prompt at startup, so the Docker container needs to restart to pick up the new persona). Monitor next 10–20 production chats for: (a) "go to website" anti-pattern disappearing, (b) booking-link rate per conversation rising, (c) no over-correction into pushy/salesy language. Later: instrument `utm_chat=cassie` click-through in Zoho to measure actual conversion lift.

## [2026-05-24] update | Booking link issue confirmed resolved in production

- Mark confirmed the production booking link bug is fixed.
- Resolution chain: token-placeholder architecture (2026-05-21) → unclosed `<a>` scrubber + day_of_week field (2026-05-21) → short venue `class_location` (2026-05-22) → untruncated logs + `utm_chat=cassie` (2026-05-22). Friend's Docker rebuild + Plesk pull picked up all changes.
- Cassie now consistently emits one clean per-class link, no malformed `<a>` shells, and Zoho accepts the form submissions. Project memory updated to mark booking link work complete.
- Next focus unblocked: `cassie_widget.js` for WordPress embed.

## [2026-05-22] update | Logs untruncated + utm_chat=cassie added to booking URLs

- **Two requests from Mark/Mr. Wee, both into `cassie-deploy/cassie_server.py`**:
  1. **Logs too short to debug the booking URL bug.** `Cassie: {reply[:80]}` cut off after the first 80 chars — a 260-char booking URL was unreadable. Same for `User: {user_message[:80]}`, `[Tool result] ... [:200]`, `[Classifier] Raw response ... [:200]`, `[Zobot] Incoming: ... [:300]`, `[Guard] Pattern-blocked: ... [:80]`. All removed — log messages now carry full content.
  2. **Need to differentiate Cassie-generated bookings from other entry points** (Mr. Wee's request via Mark). Added `&utm_chat=cassie` as a tenth query parameter in `build_booking_url`. Lets Mr. Wee filter Zoho deals / WordPress form submissions by `utm_chat` to see Cassie's contribution to bookings.
- **Buffer also bumped**: `_LOG_BUFFER` deque maxlen 1000 → 5000 lines; `/logs` endpoint `n` cap 1000 → 5000, default 200 → 500. Untruncated lines average 200–500 chars so the buffer is now ~1–2 MB — still tiny on Render's free tier and gives ~5× more debugging history.
- **Kept intentionally**: `conversation_id[:8]` and `chat_id[:8]` short prefixes in log lines (8 chars is enough to correlate a session, full UUIDs add noise without value), and `[:300]` slices on lines 836 and 873 which are classifier-context truncations, not log output.
- **Verified**: sample URL with utm_chat is `https://coursemology.sg/course-registration/?class_id=1328866&...&course_fee=741.2&utm_chat=cassie` — 278 chars total (was 262 before utm_chat, still well under the previous 280–362 range from before today's `class_location` shortening).
- **Action for Mark**: push `cassie-deploy/` so friend rebuilds Docker. Once live, the SalesIQ widget should produce booking URLs that (a) Zoho will accept (short class_location), (b) survive the SalesIQ auto-linker cleanly, and (c) tag the deal source as `utm_chat=cassie`. The `/logs` endpoint will then carry full Cassie replies for end-to-end debugging if anything else surfaces.

## [2026-05-22] update | class_location uses short venue name (fixes Zoho 120-char limit + SalesIQ multi-link mangling)

- **Two related production issues reported today by Mark (and confirmed by Haryo via WhatsApp)**:
  1. **Zoho CRM rejecting form submissions.** Haryo flagged: `&class_location` was exceeding Zoho's `maximum_length: 120`. Live check: Tampines full address URL-encoded is **121 chars** — exactly over the limit. Toa Payoh is 113 chars (under, but close). The booking form submitted from coursemology.sg/course-registration/ was failing silently on the CRM side.
  2. **One booking link contained pieces of ALL 3 venue addresses.** Production chat #19059 — visitor asked for Artisan Breads, Cassie produced one `[Book this class](...)` markdown link, but its URL contained `class_id=1328866` (Adelphi) yet the `class_location` value interleaved Adelphi + Toa Payoh + Tampines (twice) + Singapore 179803. The interleaved class IDs in the URL (`1328891`, `31863`, `1330047`, `1330055`) were the run_ids of the OTHER 4 AT43 classes Cassie had tokens for. SalesIQ's Zobot auto-linker — the same one that mangled HTML `<a>` tags pre-token migration — appears to also mangle multiple adjacent markdown booking links when the URLs are very long. The previous full-address URL was 280–362 chars per link; with 5 in a reply, the auto-linker chained them.
- **Root cause**: `build_booking_url` was expanding the CATS API's short `location_name` ("Adelphi @ City Hall", "Toa Payoh Central") to a full street address via a hardcoded `LOCATION_ADDRESSES` dict. This was the wrong shape from the start — every other Coursemology system (api.ola.sg endpoint, WordPress registration form, Haryo's reference snippet showing `location: "Ubi Workshop"`) uses the short name. The expansion only fit by luck and broke as soon as URLs got chained.
- **Fix — `cassie-deploy/cassie_server.py`**:
  - Deleted `LOCATION_ADDRESSES` dict (lines 244–252) and `resolve_location_address()` (lines 381–388) — both now unused.
  - `build_booking_url` passes the CATS `location_name` through directly: `short_location = location_name or ""`.
  - Replaced the deleted dict with a comment block explaining why we use the short name (both bugs above, plus parity with sister systems).
- **Verified** (`/tmp/verify_fix.py`, isolated against live CATS API for course_id=1789):
  - All 9 AT43 runs now produce `class_location` of 16–19 chars (was 57–113 chars, with Tampines hitting 113 and over Zoho's 120 limit under any encoding overhead).
  - Full booking URL is now 253–262 chars (was 280–362).
  - Sample for class_id=1328866 from bug report: `https://coursemology.sg/course-registration/?class_id=1328866&...&class_location=Adelphi+%40+City+Hall&deal_value=741.2&course_fee=741.2` — clean, single venue, well under all limits.
- **Bash-mount staleness note**: same recurring issue — bash sees a cached binary copy of cassie_server.py so live reimport showed `LOCATION_ADDRESSES still imports`. Read tool confirmed the actual Windows file is correct. Worked around by inlining the fixed logic in the verifier rather than importing the module. Plesk reads the real file directly so this does NOT affect deployment.
- **Next**: Mark to push `cassie-deploy/` (separate repo at github.com/architechsg/Cassie-Deploy) so friend rebuilds the Docker image and Plesk picks it up. Verify via SalesIQ widget — post-fix the bug should disappear because each markdown booking link is now ~260 chars instead of ~330, which (a) keeps each individual `class_location` value under Zoho's 120 limit and (b) is short enough that the auto-linker no longer chains adjacent links into one corrupt URL.

## [2026-05-21] update | Day-of-week field added + scrubber catches unclosed `<a>` (recurring-review batch 1)

- **Two production issues from Mark's first review batch (chats Wlshua/Food Safety, Visitor 868767/Office Mgmt)**:
  1. **Cassie miscalls day-of-week.** Visitor asked "Any available days on weekdays" for Office Management. Cassie said *"30 May, 8 June, 24 June, 10 July are all Monday–Friday"* — but 30 May 2026 is a Saturday, AND 10 July was never in the original list (hallucinated). Root cause: `format_run` returned only ISO dates; Haiku cannot reliably compute weekdays from a date string.
  2. **Malformed booking links keep showing up.** Same `<a href="[ ](URL%22)URL["](URL%22) target="_blank">Book this class</a>` pattern the 2026-05-21 01:23 token+scrub commit was meant to fix. Mark confirms the deploy is pushed. Live test of the current scrubber against the exact production string shows it WOULD strip it cleanly — so either the Plesk container hasn't picked up the new image yet, OR persona drift means Cassie is occasionally also emitting *unclosed* `<a>` shapes the old paired-anchor regex couldn't catch.
- **Fix — `cassie-deploy/cassie_server.py`**:
  - Added `_day_of_week(iso_date)` and `_is_weekend(iso_date)` helpers using `datetime.strptime(...).strftime("%A")` and `.weekday() >= 5`.
  - `format_run` now returns two new fields per run: `day_of_week` (`"Monday"` or `"Monday–Friday"` for multi-day runs) and `is_weekend` (bool). Authoritative — Haiku must read, not compute.
  - `_scrub_urls` extended with two extra regexes: orphan opener `<a\s[^>]*>` and orphan closer `</a\s*>`. Closes the case where Haiku's URL gets truncated by `max_tokens=1024` mid-output, leaving an unclosed `<a href="…" target="_blank">` that the paired-anchor regex couldn't match (bare-URL strip removed the href value but the empty `<a …>` shell still rendered as a broken click target).
  - `datetime` added to the `from datetime import …` line.
- **Persona — `cassie-vault/cassie-persona.md`**:
  - Booking Links section: added explicit "URLs are forbidden in your replies. If you find yourself about to type http, https, www., coursemology.sg/course-registration, `<a href`, or anything resembling a clickable URL or anchor tag — STOP and write a `[[BOOK_<run_id>]]` token instead. Long invented URLs get truncated mid-output and leave broken HTML in the chat."
  - Rule 3 (Handling results): two new bullets — "User asks about weekdays / weekends / a specific day of the week" (use `day_of_week` and `is_weekend` fields, never compute) and "Never mention a date that isn't in the tool result" (kills the 10 July hallucination class of bug).
- **Verified**: `/tmp/test_e2e.py` confirms (a) `_day_of_week("2026-05-30") == "Saturday"` and `_is_weekend == True`, (b) paired malformed pattern (1158-char string from the user) strips to "Adelphi — June 5–12 Book this class", (c) unclosed `<a href>…target="_blank">` strips to plain text with no shell remaining, (d) `[[BOOK_*]]` tokens preserved untouched.
- **Bash-mount staleness note**: `python3 -m py_compile` returned a phantom SyntaxError at line 1163; bash sees a stale 1171-line copy ending mid-string. Read tool confirms the actual Windows file is intact through `/logs` and the entry point. Same recurring sync issue noted in earlier 2026-05-19 and 2026-05-21 entries. Plesk reads the real file directly so this does not affect deployment.
- **Next**: Mark to push `cassie-deploy/` (separate repo at github.com/architechsg/Cassie-Deploy) and verify Plesk pulls the new image. Watch the `/logs` endpoint for `[Scrub] stripped URL` warnings — if those fire frequently post-deploy, the persona needs another tightening pass.

## [2026-05-21] update | Token substitution outputs markdown not HTML — SalesIQ Zobot was mangling `<a href>` tags

- **Bug**: Visitor chat in production STILL showed `<a href="[ ](URL)URL["](URL)" ...>Book this class</a>` malformed soup, even though server-side logs clearly showed `[Tokens] substituted 4 token(s) in outbound reply` (the tokens WERE being substituted correctly to clean HTML anchors).
- **Root cause**: SalesIQ's Zobot response pipeline runs an auto-linker over the text in the response body BEFORE the visitor sees it. When that auto-linker sees a URL inside an HTML `href="..."` attribute, it wraps it with `[ ](URL)URL["](URL)` markdown-link syntax and jams it back inside the href attribute — producing the nested malformed string. This is a SalesIQ-side behaviour, not something we control. Local `/chat` testing didn't show this because the local demo frontend just renders the HTML directly without that auto-linker.
- **Fix — `cassie-deploy/cassie_server.py`**: `_substitute_booking_tokens()` now outputs markdown `[Book this class](URL)` instead of HTML `<a href="URL" target="_blank">Book this class</a>`. SalesIQ renders markdown natively as clickable links without post-processing. The local demo's markdown→`<a>` regex also handles `[label](url)` fine. Single-line change inside the substitution function. Order of operations unchanged: scrub URLs → save to history → substitute tokens (substitution still happens AFTER scrub so the markdown booking links it produces are not stripped).
- **Why this only surfaced today**: every clean test today was via `/chat` endpoint with the local demo page. The Zobot mangling only manifests on the `/webhook/zobot` path → SalesIQ widget. Production was the first end-to-end Zobot+SalesIQ test of the new token output.
- **Pending**: push to GitHub + friend rebuilds Docker. End-to-end test via SalesIQ widget required to confirm — local /chat can't replicate the bug.

## [2026-05-21] update | Alt-venue runs get booking_tokens too — fixes empty-map issue when venue fallback fires

- **Bug**: User asked "moon cakes class in tampines" → no Tampines runs → fallback returned 3 Adelphi alt-venue runs WITHOUT booking_tokens (because format_run was called with course_fee omitted in the alt-venue path). conv_tokens map stayed empty. Cassie reasonably wanted to give booking links, invented 3 `[[BOOK_*]]` placeholders. Server stripped them silently, so user saw classes with no links at all. Follow-up turns (which referenced prior tokens) hit the same empty-map problem.
- **Root cause**: the "alt-venue runs intentionally have no booking_url" rule was a workaround for the OLD single-URL auto-append design — where one auto-grabbed link could mislead the user before they'd picked a venue. **Under the token architecture this constraint is obsolete**: Cassie chooses where each token goes, so there's no auto-grab.
- **Fix — `cassie-deploy/cassie_server.py`**: `execute_get_course_schedule` alt-venue path now passes `course_fee = pricing.get("full")` to `format_run` so alt-venue runs get full `booking_url` + `booking_token` like any other run. Comment block above updated to explain.
- **Persona — `cassie-persona.md` Booking Links**: "Alternative-venue runs intentionally have no booking_token" rule REVERSED — they DO have tokens, treat them same as `upcoming_classes`. Visitor can book any alt-venue class directly.
- **Net effect** for the three failing test cases: (1) "moon cakes at tampines" now populates conv_tokens with 3 Adelphi tokens → Cassie's tokens resolve → 3 clickable links; (2) "provide me booking link for all" can resolve from prior-turn map; (3) "i want 31 july" can resolve the specific class.

## [2026-05-21] update | Token mechanism hardened — invalid tokens stripped silently + persona token discipline

- **Bug** (during live testing of token rollout): Cassie wrote `[[BOOK_NA]]` for a mooncake class that had no `booking_token` in the tool result (likely the class had end_date null, so format_run skipped the token). The original strict regex `\[\[BOOK_\d+\]\]` didn't match `BOOK_NA`, so the literal `[[BOOK_NA]]` was left visible in the chat — looked broken to the user.
- **Fix — `cassie-deploy/cassie_server.py`**:
  - Loosened `BOOKING_TOKEN_RE` from `\[\[BOOK_\d+\]\]` to `\[\[BOOK_[^\]]+\]\]` — catches any `[[BOOK_*]]` shape Cassie might invent.
  - `_substitute_booking_tokens()` now returns a 3-tuple `(text, valid_count, invalid_stripped_count)`. Invalid tokens (not in the conv_tokens map) are stripped silently with `""` instead of being left literal. Whitespace tidy-up after stripping (trailing space before punctuation, empty parens, double spaces).
  - Call site at end of `get_cassie_reply()` logs `[Tokens] substituted N` and `[Tokens] stripped N invalid` as a WARNING — flags persona drift without exposing the artefact to visitors.
- **Persona — `cassie-persona.md` Booking Links rewritten** with new "Token discipline" section:
  - Use the token EXACTLY as it appears in the tool result. Don't retype or paraphrase.
  - NEVER invent a token. No `[[BOOK_NA]]`, `[[BOOK_TBA]]`, `[[BOOK_TBC]]`, etc.
  - If a class has no `booking_token`, omit the token entirely — the visitor WhatsApps to book that one.
- **Verified**: unit test reproducing the exact mooncake-workshop bug pattern — 1 invalid stripped, 2 valid substituted, 24 June line ends cleanly with no trailing artefacts.

## [2026-05-21] update | Booking-link architecture — token placeholders replace single-URL auto-append

- **Why**: previous architecture only attached one `<a href>` per Cassie reply (the first booking_url it saw in a tool result). When the user asked for all 3 dates they got 1 clickable + 10 dead "Book now" labels (scrubber stripped the markdown URLs Cassie wrote for the others). Follow-up turns ("Tampines please, give me the link") got nothing because no new tool call fired, so the server had no booking_url to capture.
- **New flow** — `cassie-deploy/cassie_server.py`:
  - `format_run()` now emits both `booking_url` and `booking_token` (format: `[[BOOK_<run_id>]]`) for runs that qualify for booking.
  - Module-level `booking_links: dict[str, dict[str, str]]` — per-conversation token→URL map. Persists across turns so Cassie can reference tokens from earlier tool calls in follow-up replies.
  - Tool loop populates `conv_tokens` from each tool result's `upcoming_classes` (and `upcoming_classes_other_venues`, though those don't currently carry tokens). Strips `booking_url` from `result_clean` — Cassie sees only `booking_token`.
  - `BOOKING_TOKEN_RE = re.compile(r'\[\[BOOK_\d+\]\]')` and `_substitute_booking_tokens(text, conv_tokens)` — single regex pass at end of `get_cassie_reply()` replaces each token with `<a href="{url}" target="_blank">Book this class</a>`.
  - REMOVED: the old `booking_url_for_html` capture-and-append-at-end logic. Tokens handle all link placement.
  - `_scrub_urls()` retained as defence-in-depth; logs a warning when it fires (signals persona drift).
  - History save: still `reply_raw` (the post-scrub, pre-substitution text) — preserves tokens so Cassie can reference them on follow-up turns; no URLs in history to imitate.
- **Persona — `cassie-persona.md` "Booking Links" section rewritten**: tells Cassie to use `booking_token` inline next to each class; explains follow-up turn behaviour (repeat the token from a prior reply); skips token for FULL classes; alt-venue runs have no token by design.
- **Verified**: 6 isolated unit tests of `_substitute_booking_tokens` all pass — multi-link (3 tokens in one reply), follow-up turn (token from prior turn map), invalid-token (left literal so it shows in logs), plain reply, empty map, token-with-punctuation. End-to-end testing requires Mark to restart the local server.
- **File state**: bash mount in test env stuck on stale 1044-line copy; actual Windows file is 1152 lines with all edits — Read tool confirms. Recurring sync issue; Mark's local Python will read the live file directly.
- **Net code change**: roughly the same size as the strip+capture+append block it replaced. Number of "places link logic lives" went from 3 (strip in tool loop, capture in tool loop, append at end) to 2 (strip+populate-map in tool loop, substitute at end). Smaller surface, cleaner contract.

## [2026-05-21] update | Location-fallback in `get_course_schedule` — offer other venues when the requested venue has none

- **Bug**: User picked "Jurong East" for the Drone course; Cassie said "I don't see any upcoming dates in the system right now" and offered the WhatsApp fallback. But 4 future runs at Toa Payoh existed in CATS — the user just couldn't see them. When the user narrowed to "Aerial Photography & Videography with Drones", Cassie carried the Jurong East filter forward and got the same empty result again, never trying without the filter.
- **Root cause**: `execute_get_course_schedule` had a single empty-result branch with one message ("WhatsApp us — schedules update regularly"). That message conflated *"no runs at the requested venue"* with *"no runs anywhere"*. The existing limit-15 retry kept the same location filter, so it never widened the search.
- **Fix — `cassie-deploy/cassie_server.py`**:
  - After both initial fetch and limit=15 retry come up empty, **if a `location_ids` was specified**, do a second fetch with `location_ids=None` and return a new bucket `upcoming_classes_other_venues` alongside the empty `upcoming_classes`.
  - Tool-result `message` field now explicitly tells Cassie: "no upcoming dates at \<venue\>, BUT classes are scheduled at other venues — offer them, ask if any other location works."
  - Alternative-venue runs are intentionally returned WITHOUT `booking_url` — the server's auto-append fires off the first `booking_url` it finds, and we don't want it picking one for the user before they've picked a venue. Once the user picks a venue, a follow-up tool call returns its runs with proper booking URLs.
  - Refactored: hoisted `course_name`/`course_code` into locals for readability across the three return paths.
- **Verified**: isolated reproducer at `/tmp/test_isolated.py` exercised three cases against the live CATS API — (1) Drone+Jurong East returns 4 alt-venue runs (Toa Payoh) with no `booking_url` leakage and the expected "BUT classes ARE scheduled" message; (2) Drone+Toa Payoh hits the normal path with booking URLs; (3) Drone with no location filter returns 4 runs normally. All assertions passed.
- **Note**: bash mount in the test environment was showing a stale truncated copy of `cassie_server.py`, but the Read tool confirmed the Windows file is intact at 1099 lines with the fallback branch correctly placed at lines 495–533. Patch is live in the deployed file.

## [2026-05-21] update | Defensive fix for malformed booking links — scrub URLs + save raw reply to history

- **Bug**: malformed booking link reappeared in production (drone+AI multi-topic query, 2026-05-21). Output was `<a href="[ ](URL_A)URL_B["](URL_C)" target="_blank">Book this class</a>` — Claude wrote a botched URL attempt inside her reply, server's clean append nested inside it via the href attribute.
- **Root cause** (architectural, not a regex bug): two latent issues that the May-19 fix didn't fully close.
  1. The server appended `<a href="URL">Book this class</a>` HTML and saved the full appended reply into conversation history. On the next turn Haiku saw that prior `<a>` in her own assistant turns and imitated the pattern — even though the persona told her not to.
  2. The tool result still gives Claude all the raw fields needed to reconstruct the URL (class_id, dates, course_code, course_name, venue), and the KB resolves the venue to a full address. She has both means and template.
- **Fix — `cassie-deploy/cassie_server.py`**:
  - Added `_scrub_urls(text)` helper: regex-strips markdown links `[…](url)`, HTML anchors `<a …>…</a>`, and bare `https?://…` / `www.` URLs. Emails and phone numbers (no scheme) pass through untouched.
  - In `get_cassie_reply()`: after collecting Claude's text, scrub URLs → save to `reply_raw` → only then append the server's clean `<a href>` for the outbound reply.
  - Changed `history.append({"role": "assistant", "content": reply})` → uses `reply_raw` (the pre-append, URL-free version). Kills the imitation loop.
  - `reply_raw` set in all four reply paths (normal, loop-exhausted, AuthError, generic Exception).
- **Verified**: file parses cleanly (`python -m py_compile`); unit tests against the exact 1336-char malformed string from the bug — output 399 chars, URLs gone, content intact, "Book this class" inner text preserved (server then appends one clean booking link below).
- **Side effect** during edit: Edit tool re-truncated the file tail (`/logs` route, 429 handler, entry point) — same recurring issue noted in 2026-05-19 log. Restored via `cat >> file << HEREDOC` after the truncation was detected by py_compile.
- **NOT YET APPLIED**: `Cassie API Server/cassie_server.py` and `Cassie API Server/cassie_server_dev.py` — outside the connected Cowork workspace folder. Mark to mirror the same two changes (`_scrub_urls` definition + scrub call + `reply_raw` to history) per the three-server sync rule.

## [2026-05-21] update | Fix SMS → WhatsApp confirmation wording across vault

- Changed "SMS and email confirmation" to "WhatsApp and email confirmation" in 4 files:
  - `faq/general.md` (class confirmation FAQ)
  - `faq/registration.md` (post-payment FAQ)
  - `policies/certification.md` (SOA result notification)
  - `concepts/ola-platform.md` (OLA booking confirmation)

## [2026-05-19] update | Fix booking link rendering — strip booking_url from tool result

- **Root cause**: `booking_url` was included in the tool result JSON that Cassie sees. Haiku tried to write it as a markdown link but mangled the URL (wrong encoding, wrong params). The server then also appended its own HTML anchor (because Cassie's URL ≠ correct URL), producing two broken links.
- **Fix**: `booking_url` is now extracted from `result` before Cassie sees it, then stripped from `result_clean` that goes into the tool_result message. Server always appends the clean HTML anchor from `booking_url_for_html`. Applied to `cassie-deploy/cassie_server.py` and `Cassie API Server/cassie_server.py`.
- **Persona**: `## Booking Links` section rewritten — Cassie told that links are server-managed, never to write URLs, never to ask "want a booking link?".

## [2026-05-19] update | Bug fixes: booking URL # fragment, wikilink stripping, classifier context, persona brevity

- **Fix — Booking URL `#` fragment bug**: `build_booking_url()` was encoding `#AB51` → `%23AB51`; Claude Haiku decoded `%23` back to `#` when writing the URL; browser treated `#` as fragment separator, stripping all query params after it. Fix: `clean_tag = (tag or "").lstrip("#")` — strips leading `#` before encoding so `%23` never appears. Applied to `cassie-deploy/cassie_server.py` and `Cassie API Server/cassie_server.py`.
- **Fix — Adelphi address**: `#04-35` → `No.04-35` in `LOCATION_ADDRESSES` to prevent the same `#` fragment bug in booking links.
- **Fix — Wikilink stripping**: `load_vault()` now strips Obsidian `[[Page|alias]]` → alias and `[[Page]]` → page name at load time. Prevents bracket syntax leaking into Cassie's replies. Applied to all 3 server files.
- **Fix — Context-aware classifier**: `classify_message()` now receives `last_cassie_reply` (up to 300 chars); prevents false positives on short follow-ups like "dim sum please" after a baking course reply. Applied to all 3 server files.
- **Fix — Booking URL null end_date**: `run.get("end_date") or "TBC"` handles null from CATS API; booking URL only generated when end date is a real value. Applied to all 3 server files.
- **Fix — CLASSIFIER_SYSTEM missing `"""`**: `Cassie API Server/cassie_server.py` had unclosed triple-quote on CLASSIFIER_SYSTEM constant, making the file completely unparseable (Python swallowed ~800 lines as string). Closing `"""` inserted; truncated `health()` route and file tail restored.
- **Fix — Corrupted `load_vault()`**: `cassie-deploy/cassie_server.py` had entry point code injected into function body from prior Edit tool truncation. Cleaned up.
- **Persona — PSEA/UTAP tool trigger**: `cassie-persona.md` Rule 1 + Rule 5 updated: PSEA/UTAP live only in tool (never KB); pricing/funding queries for named courses trigger immediate tool call; broad eligibility queries handled gracefully.
- **Persona — brevity rewrite**: `cassie-persona.md` Response Style strengthened: 1–2 sentences for simple questions, explicit ban on trailing offers, no dumping all schedule/pricing at once.
- All 6 issues confirmed PASS via live local testing (cassie-deploy server).

## [2026-05-18] update | Bug fixes: classifier markdown stripping + history trim safety

- **Fix 1 — Classifier JSON parse failure**: Haiku wraps JSON in ` ```json ``` ` fences despite instructions; `json.loads` failed at char 0 on every message. Added markdown-fence stripping (`re.sub`) before `json.loads` in `classify_message()`. Applied to `cassie-deploy/cassie_server.py` (prod server already had partial fix from Claude Code, completed with closing-fence strip).
- **Fix 2 — History trim 400 errors**: `history[-20:]` could start on a `tool_result` user message (orphaned from its `tool_use` block), causing Anthropic 400 "unexpected tool_use_id" errors on the next request. Fixed by advancing the trim window to the first clean user text message. Applied to both `Cassie API Server/cassie_server.py` and `cassie-deploy/cassie_server.py`.
- No vault KB changes; server-only bug fixes.

## [2026-05-17] build | cassie-deploy repo created — Docker deployment package for friend's server

- Created `cassie-deploy/` folder inside Cassie Chatbot workspace
- `cassie_server.py` — deploy copy with relative vault paths + PORT from env + debug=False
- `requirements.txt` — anthropic, flask, flask-cors, python-dotenv
- `Dockerfile` — python:3.11-slim, copies cassie-vault into image
- `docker-compose.yml` — single service, env_file .env, healthcheck on /health
- `.env.example` — template with ANTHROPIC_API_KEY, ZOBOT_SECRET, optional PORT/paths
- `.gitignore` — excludes .env, __pycache__, venv, logs
- `copy-vault.bat` — Windows batch script to xcopy cassie-vault into deploy folder before building
- Vault files must be copied with copy-vault.bat before `docker compose up --build`

## [2026-05-17] update | Input guardrails added to cassie_server.py

- Added `flask-limiter` (requirements.txt): 20 msg/hour + 150 msg/day per IP on both /chat and /webhook/zobot
- Added `check_input_length()`: rejects messages over 500 chars before any API call
- Added `classify_message()`: Claude Haiku classifier blocks off-topic, prompt injection, and spam; fails open on error
- Added `@app.errorhandler(429)` for friendly rate-limit message in correct format for each endpoint
- No changes to vault KB or persona; server-only update

## [2026-05-15] build | Human feedback Excel (130 questions) prepared for agent review

- Script: `Cassie API Server/build_feedback_excel.py`
- Runner batch: `Cassie API Server/run_build_feedback_excel.bat`
- Output (when run): `Cassie Chatbot/cassie_human_feedback.xlsx`
- 3 sheets: Instructions, Feedback (130 rows, yellow input cols), Summary (auto-calc)
- Data source: cassie_test_results_graded.csv + cassie_dev_grades_new.json
- Purpose: dad's live agents rate each Cassie reply (1–5, Yes/No, comments)

## [2026-05-15] update | Persona response style tightened for conversational brevity

- Response style: changed from "2–4 short paragraphs" to "1–2 sentences for simple answers, 2–3 dates for schedules"
- Added explicit guidance: answer the immediate question, let follow-ups draw out more detail
- Added note that accuracy is unaffected — full tool result stays in context for follow-ups
- num_results default reduced from 5 to 3
- Booking link: removed verbose "Ready to book?" preamble — link now woven inline naturally
- Rule 3: "classes found" guidance updated to match briefer style

## [2026-05-15] update | Persona Rule 1 rebalanced — "one question max, then call"

- Reverted overly aggressive "CALL IMMEDIATELY, NEVER clarify" framing after user review
- New rule: one focused clarifying question is natural and acceptable; a chain of questions is not
- Hard constraint: after any one clarifying answer, call the tool immediately — no follow-up questions
- Specific enough queries (named course + level, pricing questions, location + topic) still trigger immediate call
- Rationale: single clarification feels like a real front-desk person; the original problem was chains of 2–3 clarifications before ever calling

## [2026-05-15] update | Persona Rule 1 rewrite — stronger "call first, clarify after" enforcement

- Rewrote Rule 1 in cassie-persona.md to be significantly more forceful
- Added explicit NEVER list: never ask "which level?", "which language?", "which location?", "which month?" before calling the tool
- Expanded "enough to call" examples to cover language-without-level and level-without-language cases
- Rationale: eval analysis (N=116) showed ~30 Rule 1 violations in new run — prompt_gap Y count rose 35→65, actionable C count rose 13→34

## [2026-05-13] update | Architecture — pricing moved from vault to live CATS API

**cassie_mcp.py (Cassie MCP Server):**
- Added `GST_RATE`, `SUBSIDY_SC_PR`, `SUBSIDY_MCES` constants (9%, 50%, 70%)
- Added `calculate_pricing_tiers()` function computing full/sc_pr/mces fees from raw `full_fee` in CATS API response
- `get_course_schedule` now returns `pricing` object with: `full`, `sc_pr`, `mces`, `utap_eligible`, `psea_eligible`, `mces_top_up` — all GST-inclusive
- Tool description updated to note pricing is the only source of truth for fees
- `tgs_code` now included in all tool responses (from `course_ref_no`)
- Empty-result path also returns pricing + tgs_code for the matched course

**cassie-persona.md:**
- Section renamed to "Live Schedule & Pricing Tool"
- Added: all pricing (full, sc_pr, mces, psea, utap, mces_top_up) comes live from tool — vault intentionally has no prices
- Rule 1 trigger list expanded to include pricing/fee questions as immediate call triggers
- Rule 5 (Pricing) rewritten: defines each pricing field, specifies "all GST-inclusive", SC two-tier distinction (21-39 = sc_pr rate, 40+ = mces rate), forbids quoting `deal_value`

**Vault — 28 WSQ course files (pricing sections removed):**
- Removed `## Pricing` table + `## Subsidies & Funding` sections from all standard-format WSQ pages (food-safety x9, maintenance x5, baking x3, ai-tech x5)
- Removed `**Pricing:** Full $X / PR $Y / MCES $Z` inline lines from multi-course pages (cleaning x7, ms-office x4, drone-media x5, ecommerce x2, beauty x2, admin-hr x2)
- Kept: private/non-WSQ course prices (private-workshops.md, first-aid-courses.md, other-courses.md, Copilot Training Workshop private entry, beauty private courses)
- Kept: qualitative funding notes (`**Funding:** SFC eligible, UTAP eligible...`), "No UTAP, no PSEA" caveats, funding expiry warnings
- Kept: special notes like drone CT11 "Funding period ended Jul 2025 — confirm with staff"

**Vault — funding pages:**
- `funding/pricing-tiers.md`: added Cassie note — actual fees from `get_course_schedule` tool, not the vault
- `funding/ssg-subsidies.md`: added Cassie note — actual subsidised fees from tool, all prices GST-inclusive

**cassie_server.py (production Flask API) — pricing sync:**
- Added `GST_RATE`, `SUBSIDY_SC_PR`, `SUBSIDY_MCES` constants
- Added `calculate_pricing_tiers()` — same logic as cassie_mcp.py
- `execute_get_course_schedule()` now returns full `pricing` object + `tgs_code` (matching cassie_mcp.py output)
- Booking URL `course_fee` param now uses `pricing["full"]` (GST-inclusive) instead of raw pre-GST `full_fee`
- Tool description updated to mention live pricing + eligibility fields
- Empty-result path also returns `pricing` and `tgs_code`

**API key fix (separate session):**
- `cassie_server_dev.py` + `grade_and_report.py`: added `clean_env` to strip `ANTHROPIC_API_KEY` from subprocess env, preventing paid API credits from being consumed when using OAuth Claude CLI

## [2026-05-14] update | Persona — natural speech rule added

- cassie-persona.md Response Style: added rule forbidding meta-references ("knowledge base", "my records", "according to my data", etc.)
- Cassie now speaks as a knowledgeable person — states facts directly, uses "I'm not sure" instead of "that's not in my knowledge base"
- Also tweaked adjacent line to remove the word "knowledge base" from the persona's own wording ("not covered by your training or tool results")

## [2026-05-13] update | Persona fixes from 130-question eval grading
- cassie-persona.md Rule 1: strengthened with explicit list of what counts as "enough to call" the schedule tool; removed ambiguity that caused Cassie to ask before calling
- cassie-persona.md Rule 5: added GST-inclusive clarification ("never add GST on top of a KB price") and explicit SC pricing tier explanation (SC 21–39 = PR rate, SC 40+/MCES = lower rate)
- faq/general.md: added Q&A clarifying Food Safety only has Level 1 and Level 3 — no Level 2 or Level 4 — to prevent recurring Level 4 hallucination

## [2026-05-12] update | Sanity check — persona/server retry alignment fix
- cassie-persona.md Rule 3: removed "retry with num_results=15" instruction — server now handles retry internally; redundant Cassie-level retry removed
- cassie-persona.md, ssg-subsidies.md, faq/general.md: last_updated bumped to 2026-05-12

## [2026-05-12] update | 10-fix patch applied — vault, persona, and tool-fix

**Vault fixes:**
- `wiki/funding/ssg-subsidies.md` — restructured Self-Sponsored table into 4 separate rows (SC 21–39, SC 40+, PR, LTVP+); added PR/SPR callout box explicitly stating PR = 50% always, never 70%
- `wiki/faq/general.md` — rewrote food safety cert renewal Q&A: 5-year mark = Refresher, 10-year mark = Full Course required (not Refresher); added ⚠️ callout for 10-year rule
- `wiki/funding/mid-career-sfc.md` — NEW PAGE: covers Mid-Career Enhanced SFC top-up ($4,000), MCES subsidy, how to check balance breakdown, confirmed course list caveat, and explicit instruction to email/WhatsApp before registering when using Mid-Career credit
- `index.md` — added mid-career-sfc entry to Funding table

**Persona fixes (cassie-persona.md):**
- Live Schedule Tool section rewritten as 5 numbered rules:
  - Rule 1: Call tool first, clarify after (fixes over-clarification before tool call)
  - Rule 2: How to call (clarified)
  - Rule 3: Handling results — empty result retry (num_results=15, then soft fallback); month-mismatch flagging
  - Rule 4: Timing questions — give 9am–6pm upfront, don't ask for clarification
  - Rule 5: Pricing — never cite deal_value; always use vault pricing tiers

**Pending (bash unavailable):**
- `cassie_server.py` retry logic: retry with num_results=15 on empty result, then return soft fallback message

## [2026-05-12] query | Cassie graded against 130 real visitor questions — gap analysis complete
- Graded all 130 test responses from `cassie_test_results_20260512_161458.csv`
- 88 Type A (gradeable), 35 Type C (clarification), 7 OOS/trivial
- Pass rate (Type A): 62.5% | Partial: 25% | Fail: 12.5% | Mean score: 1.63/2.0
- 12 vault gaps, 19 prompt gaps, 9 CATS tool gaps identified
- Top failures: tool loop error (row 4), empty schedule for Food Safety L1 English (row 112), PR subsidy rate hallucination (30% stated, should be 50%) (row 102), Mid-Career SFC hallucination (row 70), 10yr cert logic error (row 93)
- Output files: `cassie_test_results_graded.csv` + `cassie_gap_analysis.html`
- Priority fixes: Mid-Career SFC vault page needed; tool retry logic for empty results; PR subsidy rate correction in persona; refresher pricing to use vault tiers not deal_value

## [2026-05-12] query | SalesIQ scrape complete — 100 additional real visitor questions extracted (ids 31–130)
- Continued browsing SalesIQ closed chats from #18683 down to #18642
- Collected 100 new questions (ids 31–130) appended to cassie_test_questions.csv (now 130 total)
- New topics covered: course_timing, course_availability, pricing_registration, schedule_location, language_option, course_requirements, certificate_retrieval, registration, funding_skillsfuture, accreditation, course_inquiry, eligibility_foreign
- Notable patterns: many chats missed or idle timeout; agents often only said "hi" then redirected to WhatsApp; Cassie should do far better on straightforward factual questions
- Skipped non-Singapore visitors (Pakistan, India) and job-seekers (telemarketer vacancy, safety job inquiries)

## [2026-05-12] query | Cassie evaluation setup — 30 real questions extracted from SalesIQ, test harness built
- Browsed 30+ real visitor chats from SalesIQ (salesiq.zoho.com/coursemology/allchats)
- Extracted 30 real questions covering: funding/SkillsFuture, eligibility, prerequisites, schedule/location, registration, certification, halal, corporate enrollment, course discovery, Chinese-language, accreditation
- Created `cassie_test_questions.csv` — 30 questions with topic tags and human agent answers
- Created `cassie_tester.py` — test harness that sends each question to `/chat` endpoint and saves responses with scoring columns to CSV
- Key patterns observed: many chats were missed or deflected to WhatsApp by agents without answering — Cassie needs to do better on these

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

## [2026-05-19] update | Post-live-test bug fixes — server + persona
- `cassie-deploy/cassie_server.py` — fixed corrupted `load_vault()` (entry point code had been injected into function body from prior edit tool truncation bug)
- `Cassie API Server/cassie_server.py` — fixed missing closing `"""` on `CLASSIFIER_SYSTEM` constant (caused Python to swallow ~800 lines as string content, making file completely unparseable; root cause of all past syntax errors in this file)
- All 3 server files — added Obsidian wikilink stripping at vault load time (`[[Page|alias]]` → alias, `[[Page]]` → Page name); prevents raw bracket syntax from leaking into Cassie's responses
- All 3 server files — context-aware classifier: `classify_message()` now receives `last_cassie_reply` for context, replacing the fragile 5-word rule; prevents false positives on short follow-up messages
- All 3 server files — booking URL fix: `run.get("end_date") or "TBC"` (handles null from CATS API); booking URL only generated when end date is a real value
- `cassie-vault/cassie-persona.md` — Rule 1 updated: added explicit "do not consult knowledge base first" for pricing/funding queries; Rule 5 updated: PSEA/UTAP live ONLY in tool (never KB); guidance added for broad "which courses have PSEA?" queries
- `cassie-vault/cassie-persona.md` — Response Style section rewritten: stronger brevity rules, explicit ban on trailing "Is there anything else?" offers, guidance on not dumping all schedule/pricing info at once
- **Status:** All fixes local only. Mark to test locally tomorrow, then push cassie-deploy → friend rebuilds Docker.
