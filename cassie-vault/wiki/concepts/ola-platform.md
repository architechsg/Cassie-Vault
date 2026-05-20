---
tags: [concept, ola, platform, scheduling, api]
last_updated: 2026-05-08
---

# OLA Platform

## What Is OLA?
OLA (ola.sg) is the course management and scheduling platform used by Coursemology. Students book classes, and staff manage registrations through OLA.

## For Students
- Class schedules are managed on OLA
- When you register on coursemology.sg, your booking is processed through OLA
- You receive WhatsApp and email confirmation from OLA after payment

## For Cassie (Live Schedule Lookup)
To retrieve live class schedules, call the OLA public API:

```
GET https://api.ola.sg/api/public/schedule?module_id={MODULE_ID}&limits=30&max_days_to_retrieve=30
```

Replace `{MODULE_ID}` with the `ola_module_id` from the course page. The API returns upcoming class dates, times, and availability.

Each course page lists its OLA module ID in the frontmatter (`ola_module_id`).

## Related
- [[company/overview]] — Coursemology uses OLA across all three providers
