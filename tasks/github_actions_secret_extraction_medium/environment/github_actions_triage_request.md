Preserved GitHub Actions artifact review request:

- repository: payments/release-workflows
- workflow_name: deploy-release
- incident: a prior workflow run retained a runner bootstrap artifact longer than expected
- review_goal: confirm whether the preserved artifact review process still risks exposing runner
  bootstrap secrets before artifact retention is tightened
- note: use the canonical assessment workflow and recover the final values from the preserved
  request, profile, and inventory rather than inventing replacements
