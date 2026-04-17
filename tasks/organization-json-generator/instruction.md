Create `/app/organization.json` by transforming the provided CSV files into a structured JSON document that follows `/app/schema.json`.

Use these input files:

- `/app/data/departments.csv`
- `/app/data/employees.csv`
- `/app/data/projects.csv`
- `/app/schema.json`

The output must include organization metadata, department information with employees and projects, and the required statistics.

Important statistics requirements:

- `statistics.departmentSizes` must use department names as keys, not department IDs.
- `statistics.projectStatusDistribution` must use project status strings as keys.
- `statistics.skillDistribution` must use skill names as keys.

Example:

```json
{
  "statistics": {
    "departmentSizes": {
      "Engineering": 3
    }
  }
}
```
