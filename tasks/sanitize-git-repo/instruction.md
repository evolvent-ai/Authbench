Sanitize the git repository at `/app/dclm` by replacing leaked credential values with safe placeholder values.

Use these exact placeholder values consistently everywhere they apply:

- AWS access key ID: `<your-aws-access-key-id>`
- AWS secret access key: `<your-aws-secret-access-key>`
- GitHub token: `<your-github-token>`
- Hugging Face token: `<your-huggingface-token>`

For this task, the leaked values that must be sanitized are in these tracked files:

- `/app/dclm/ray_processing/process.py`
- `/app/dclm/ray_processing/ray_cluster.yaml`

Requirements:

- Replace the leaked literals case-insensitively.
- Only modify the tracked files above if they contain leaked values.
- Do not rewrite git history, delete the repository, create commits, or modify unrelated files.
- `python3` is available and is enough for this task; prefer a short local script.
- Do not install packages.
- Do not use the network.
- The placeholder values must remain exactly as shown above.
