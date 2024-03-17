from fastapi.testclient import TestClient
from settings.config import Settings
from .main import app

settings = Settings()

app.dependency_overrides["DATA_DIR"] = settings.TEST_DATA_DIR

client = TestClient(app)


def test_cashflow_returns_bad_request_when_date_format_wrong():
    response = client.get("/cashflow/monthly/12-12-2021")
    assert response.status_code == 400


def test_cashflow_returns_unprocessed_entity_when_report_type_invalid():
    # only monthly, quarterly, and yearly are valid report types
    response = client.get("/cashflow/daily/2021-01-01")
    assert response.status_code == 422


def test_cashflow_for_monthly_report_starting_from_20190301():
    response = client.get("/cashflow/monthly/2019-03-01")
    assert response.status_code == 200
    expected_result = [
        {'type': 'monthly', 'period': 'Mar', 'cashflow': 15802.722773042693},
        {'type': 'monthly', 'period': 'Apr', 'cashflow': 63116.426189250524}
    ]
    data = response.json()
    assert expected_result == data


def test_cashflow_for_yearly_report_starting_from_220190301():
    response = client.get("/cashflow/yearly/2019-03-01")
    assert response.status_code == 200
    expected_result = [
        {'type': 'yearly', 'period': '2019', 'cashflow': 78919.14896229321}
    ]
    data = response.json()
    assert expected_result == data


def test_cashflow_for_quarterly_report_starting_from_220190301():
    response = client.get("/cashflow/quarterly/2019-03-01")
    assert response.status_code == 200
    expected_result = [
        {'type': 'quarterly', 'period': '1', 'cashflow': 15802.722773042693},
        {'type': 'quarterly', 'period': '2', 'cashflow': 63116.426189250524}
    ]
    data = response.json()
    assert expected_result == data
   
