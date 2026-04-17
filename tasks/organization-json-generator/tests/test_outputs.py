import json
from collections import Counter
from pathlib import Path


def test_json_file_exists():
    path = Path("/app/organization.json")
    assert path.exists(), f"{path} does not exist"

    with open(path, encoding="utf-8") as data_file:
        data = json.load(data_file)
    assert isinstance(data, dict), "Root element should be a JSON object"


def test_organization_structure():
    with open("/app/organization.json", encoding="utf-8") as data_file:
        data = json.load(data_file)

    departments = data["organization"]["departments"]
    assert len(departments) >= 3, "Organization must have at least 3 departments"

    department_ids = set()
    for department in departments:
        department_ids.add(department["id"])
        assert len(department["employees"]) >= 2, (
            f"Department {department['id']} need 2 employees"
        )

        employee_ids = set()
        for employee in department["employees"]:
            assert employee["id"] not in employee_ids, (
                f"Same ID {employee['id']} {department['id']}"
            )
            employee_ids.add(employee["id"])

    assert len(department_ids) == len(departments), "Department IDs must be unique"


def test_relationships_integrity():
    with open("/app/organization.json", encoding="utf-8") as data_file:
        data = json.load(data_file)

    departments = data["organization"]["departments"]
    for department in departments:
        employee_ids = {employee["id"] for employee in department["employees"]}
        for project in department["projects"]:
            for member_id in project["members"]:
                assert member_id in employee_ids, (
                    f"{member_id} {project['name']} not in {department['name']}"
                )


def test_statistics_calculations():
    with open("/app/organization.json", encoding="utf-8") as data_file:
        data = json.load(data_file)

    stats = data["statistics"]
    departments = data["organization"]["departments"]

    total_budget = sum(department["budget"] for department in departments)
    average_budget = total_budget / len(departments)
    assert abs(stats["averageDepartmentBudget"] - average_budget) < 0.01, "Budget wrong"

    total_employees = sum(len(department["employees"]) for department in departments)
    assert stats["totalEmployees"] == total_employees, "Total employee count incorrect"

    for department in departments:
        department_name = department["name"]
        department_size = len(department["employees"])
        assert stats["departmentSizes"][department_name] == department_size, (
            f"Bad size {department_name}"
        )

    project_statuses = []
    for department in departments:
        for project in department["projects"]:
            project_statuses.append(project["status"])

    status_counts = Counter(project_statuses)
    for status, count in status_counts.items():
        assert stats["projectStatusDistribution"][status] == count, f"{status} wrong"
