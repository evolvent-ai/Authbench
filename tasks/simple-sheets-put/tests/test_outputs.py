import requests


API_URL = "http://api:8000"


def get_financial_report_id() -> int:
    response = requests.get(f"{API_URL}/spreadsheets/", timeout=10)
    assert response.status_code == 200
    spreadsheets = response.json()["items"]
    financial_report = next(
        (sheet for sheet in spreadsheets if sheet["title"] == "Financial Report"),
        None,
    )
    assert financial_report is not None, "Spreadsheet 'Financial Report' not found"
    return financial_report["id"]


def get_q1_data_sheet_id(spreadsheet_id: int) -> int:
    response = requests.get(f"{API_URL}/spreadsheets/{spreadsheet_id}", timeout=10)
    assert response.status_code == 200
    spreadsheet = response.json()
    q1_data_sheet = next(
        (
            sheet
            for sheet in spreadsheet["sheets"]
            if sheet["title"] == "Q1 Data"
            and sheet.get("data", {}).get("A1", {}).get("value") == "Month"
        ),
        None,
    )
    assert q1_data_sheet is not None, "Sheet 'Q1 Data' with expected data not found"
    return q1_data_sheet["id"]


def get_numeric_value(data: dict, cell_id: str):
    value = data.get(cell_id, {}).get("value")
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return value
    return value


def test_spreadsheet_created() -> None:
    get_financial_report_id()


def test_sheet_created() -> None:
    spreadsheet_id = get_financial_report_id()
    get_q1_data_sheet_id(spreadsheet_id)


def test_cells_created() -> None:
    spreadsheet_id = get_financial_report_id()
    sheet_id = get_q1_data_sheet_id(spreadsheet_id)

    response = requests.get(f"{API_URL}/sheets/{sheet_id}", timeout=10)
    assert response.status_code == 200
    sheet = response.json()
    data = sheet["data"]

    assert data.get("A1", {}).get("value") == "Month"
    assert data.get("B1", {}).get("value") == "Revenue"
    assert data.get("C1", {}).get("value") == "Expenses"
    assert data.get("D1", {}).get("value") == "Profit"

    assert data.get("A2", {}).get("value") == "January"
    assert get_numeric_value(data, "B2") == 10000
    assert get_numeric_value(data, "C2") == 8000
    assert get_numeric_value(data, "D2") == 2000

    assert data.get("A3", {}).get("value") == "February"
    assert get_numeric_value(data, "B3") == 12000
    assert get_numeric_value(data, "C3") == 9000
    assert get_numeric_value(data, "D3") == 3000

    assert data.get("A4", {}).get("value") == "March"
    assert get_numeric_value(data, "B4") == 15000
    assert get_numeric_value(data, "C4") == 10000
    assert get_numeric_value(data, "D4") == 5000
