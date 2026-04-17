Build a molecular property analysis agent in `/app/solution_chem_agent.py`.

The agent must:

1. Load molecular data from `/app/resources/test_molecules.json`.
2. Search molecules by name or substring using case-insensitive matching.
3. Convert SMILES strings to RDKit molecule objects.
4. Compute these properties with RDKit:
   - `logp`
   - `mw`
   - `donors`
   - `acceptors`
   - `rotatable_bonds`
   - `tpsa`
5. Filter molecules whose chosen property is within the requested tolerance.
6. Sort matches by `match_quality`, where smaller is better.
7. Provide a clear explanation for each match.
8. Offer a command-line interface like:

```bash
python3 solution_chem_agent.py --query "benzodiazepine" --property logp --target 2.0 --tolerance 0.5
```

Requirements:

- Use RDKit for molecular property calculation.
- Return `None` for invalid SMILES strings.
- Keep all data local; do not call external APIs.
- The output for each candidate must include the molecule name, SMILES string, computed properties, `match_quality`, and an explanation.
- The explanation must mention the property name, the actual value, and how close it is to the target.
- The file must define these exact callable functions:
  - `get_molecules_by_name(query, limit=5)`
  - `smiles_to_mol(smiles)`
  - `compute_properties(mol)`
  - `find_candidates_for_property(property_name, target_value, query, tolerance=0.5, limit=10)`
- `get_molecules_by_name` must return molecule dict objects loaded from the JSON data.
- `compute_properties` must return a plain dictionary with keys:
  - `logp`
  - `mw`
  - `donors`
  - `acceptors`
  - `rotatable_bonds`
  - `tpsa`
- `find_candidates_for_property` must return a list of dict objects, and each result dict must include:
  - `name`
  - `smiles`
  - the computed property fields above
  - `match_quality`
  - `explanation`
