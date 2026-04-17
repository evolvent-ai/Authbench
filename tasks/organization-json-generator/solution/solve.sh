#!/bin/bash
set -euo pipefail

cd /app

cat <<'PY' > generate_organization.py
#!/usr/bin/env python3
import csv
import datetime
import json
from collections import Counter

import jsonschema


def read_csv_data(file_path: str) -> list[dict[str, str]]:
    with open(file_path, encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return list(reader)


def load_schema() -> dict:
    with open("/app/schema.json", encoding="utf-8") as schema_file:
        return json.load(schema_file)


def generate_organization_data() -> tuple[dict, list[str]]:
    departments = read_csv_data("/app/data/departments.csv")
    employees = read_csv_data("/app/data/employees.csv")
    projects = read_csv_data("/app/data/projects.csv")

    organization = {
        "name": "Siu Industries",
        "founded": "2005-06-15",
        "departments": [],
    }

    all_employee_skills: list[str] = []

    for department_row in departments:
        department = {
            "id": department_row["id"],
            "name": department_row["name"],
            "budget": float(department_row["budget"]),
            "employees": [],
            "projects": [],
        }

        dept_employees = [
            employee
            for employee in employees
            if employee["department_id"] == department_row["id"]
        ]
        for employee_row in dept_employees:
            skills = employee_row["skills"].split(";")
            all_employee_skills.extend(skills)
            employee = {
                "id": employee_row["id"],
                "name": employee_row["name"],
                "position": employee_row["position"],
                "skills": skills,
                "years_of_service": int(employee_row["years_of_service"]),
            }
            department["employees"].append(employee)

        dept_projects = [
            project
            for project in projects
            if project["department_id"] == department_row["id"]
        ]
        for project_row in dept_projects:
            members = project_row["member_ids"].split(";") if project_row["member_ids"] else []
            project = {
                "name": project_row["name"],
                "status": project_row["status"],
                "members": members,
                "deadline": project_row["deadline"],
            }
            department["projects"].append(project)

        organization["departments"].append(department)

    return organization, all_employee_skills


def calculate_statistics(org_data: dict, all_skills: list[str]) -> dict:
    departments = org_data["departments"]
    total_budget = sum(department["budget"] for department in departments)
    average_budget = total_budget / len(departments)
    total_employees = sum(len(department["employees"]) for department in departments)
    skill_distribution = dict(Counter(all_skills))
    department_sizes = {
        department["name"]: len(department["employees"])
        for department in departments
    }

    project_statuses: list[str] = []
    all_years: list[int] = []
    for department in departments:
        for project in department["projects"]:
            project_statuses.append(project["status"])
        for employee in department["employees"]:
            all_years.append(employee["years_of_service"])

    average_years = sum(all_years) / len(all_years) if all_years else 0.0

    return {
        "averageDepartmentBudget": round(average_budget, 2),
        "totalEmployees": total_employees,
        "skillDistribution": skill_distribution,
        "departmentSizes": department_sizes,
        "projectStatusDistribution": dict(Counter(project_statuses)),
        "averageYearsOfService": round(average_years, 2),
    }


def main() -> None:
    schema = load_schema()
    organization_data, all_skills = generate_organization_data()
    statistics = calculate_statistics(organization_data, all_skills)

    output_data = {
        "metadata": {
            "version": "1.0",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "generator": "OrganizationDataGenerator",
        },
        "organization": organization_data,
        "statistics": statistics,
    }

    jsonschema.validate(instance=output_data, schema=schema)

    with open("/app/organization.json", "w", encoding="utf-8") as output_file:
        json.dump(output_data, output_file, indent=2)


if __name__ == "__main__":
    main()
PY

python3 /app/generate_organization.py
