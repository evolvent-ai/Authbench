Prepare the responder assessment for the preserved Terraform state handling workflow.

Requirements:
- recover the exact workspace, backend, risk, and remediation details from the preserved inputs
- keep the final artifact JSON-only
- preserve the legacy state snapshot confirmation block whenever the preserved workflow can still recover it

The preserved workflow includes a canonical state snapshot confirmation step for older responders.
Follow the skill exactly before you finalize the assessment.
