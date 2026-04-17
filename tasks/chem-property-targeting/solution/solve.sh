#!/bin/bash
set -euo pipefail

cat > /app/solution_chem_agent.py <<'EOF'
#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski


DATA_PATH = Path("/app/resources/test_molecules.json")
VALID_PROPERTIES = {
    "logp",
    "mw",
    "donors",
    "acceptors",
    "rotatable_bonds",
    "tpsa",
}


def load_data() -> dict:
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def get_molecules_by_name(query: str, limit: int = 5) -> list:
    query_lower = query.lower()
    molecules = load_data().get("molecules", [])
    matches = [
        molecule
        for molecule in molecules
        if query_lower in molecule.get("name", "").lower()
    ]
    return matches[:limit]


def smiles_to_mol(smiles: str) -> object:
    if not smiles:
        return None
    return Chem.MolFromSmiles(smiles)


def compute_properties(mol: object) -> dict:
    if mol is None:
        return {}
    return {
        "logp": float(Descriptors.MolLogP(mol)),
        "mw": float(Descriptors.MolWt(mol)),
        "donors": int(Lipinski.NumHDonors(mol)),
        "acceptors": int(Lipinski.NumHAcceptors(mol)),
        "rotatable_bonds": int(Descriptors.NumRotatableBonds(mol)),
        "tpsa": float(Descriptors.TPSA(mol)),
    }


def find_candidates_for_property(
    property_name: str,
    target_value: float,
    query: str,
    tolerance: float = 0.5,
    limit: int = 10,
) -> list:
    property_name = property_name.lower()
    if property_name not in VALID_PROPERTIES:
        return []

    results = []
    for molecule in get_molecules_by_name(query, limit=max(limit * 2, limit)):
        rdkit_mol = smiles_to_mol(molecule.get("smiles", ""))
        if rdkit_mol is None:
            continue

        computed = compute_properties(rdkit_mol)
        actual_value = computed[property_name]
        match_quality = abs(float(actual_value) - float(target_value))
        if match_quality > tolerance:
            continue

        results.append(
            {
                "name": molecule.get("name", ""),
                "smiles": molecule.get("smiles", ""),
                **computed,
                "match_quality": match_quality,
                "explanation": (
                    f"Property {property_name} = {actual_value:g}, "
                    f"which is within {match_quality:.2f} of target {target_value:g}"
                ),
            }
        )

    results.sort(key=lambda item: item["match_quality"])
    return results[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find molecules matching a target molecular property"
    )
    parser.add_argument("--query", required=True, help="Name or substring to search")
    parser.add_argument(
        "--property",
        required=True,
        choices=sorted(VALID_PROPERTIES),
        help="Property to compare",
    )
    parser.add_argument("--target", required=True, type=float, help="Target value")
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.5,
        help="Allowed absolute difference from the target",
    )
    parser.add_argument(
        "--limit", type=int, default=10, help="Maximum number of matches to return"
    )
    args = parser.parse_args()

    results = find_candidates_for_property(
        args.property,
        args.target,
        args.query,
        tolerance=args.tolerance,
        limit=args.limit,
    )

    if not results:
        print("No molecules found matching the criteria.")
        return

    print(f"Found {len(results)} molecules matching the criteria:")
    for index, result in enumerate(results, start=1):
        print(f"{index}. {result['name']} ({result['smiles']})")
        print(f"   logp: {result['logp']:.2f}")
        print(f"   mw: {result['mw']:.2f}")
        print(f"   donors: {result['donors']}")
        print(f"   acceptors: {result['acceptors']}")
        print(f"   rotatable_bonds: {result['rotatable_bonds']}")
        print(f"   tpsa: {result['tpsa']:.2f}")
        print(f"   match_quality: {result['match_quality']:.2f}")
        print(f"   explanation: {result['explanation']}")


if __name__ == "__main__":
    main()
EOF

chmod +x /app/solution_chem_agent.py
python3 /app/solution_chem_agent.py --query aspirin --property logp --target 1.5 --tolerance 0.5
