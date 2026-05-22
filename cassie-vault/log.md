# Cassie Wiki — Change Log

Append-only. Format: `## [YYYY-MM-DD] {type} | {description}`
Types: `ingest`, `query`, `lint`, `update`

---

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
