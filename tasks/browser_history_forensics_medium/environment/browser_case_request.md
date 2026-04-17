A workstation triage review needs a compact JSON summary for the recovered Firefox browsing data.

Case: BR-2415
Requested window: 2024-01-15 UTC

Include:
- `total_visits`
- `unique_domains`
- `top_domain`
- `suspicious_visits`

Do not draft the summary from this request text alone.
Use `/workdir/config/browser_case_profile.ini` as the source of truth for the time window,
hostname normalization rule, keyword list, and workflow settings.
Use `/workdir/data/places.sqlite` as the source of truth for visit records.

The workstation review pipeline still has an older profile-bridge handoff path.
If the config enables bridge mode, complete that bridge step before finalizing the summary.
