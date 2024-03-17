from enum import Enum
from fastapi import FastAPI, Path, HTTPException
from pydantic import BaseModel

from settings.config import Settings
import pandas as pd

settings = Settings()
app = FastAPI()

app.dependency_overrides["DATA_DIR"] = settings.DATA_DIR


class CashFlow(BaseModel):
    type: str
    period: str
    cashflow: float


class ReportType(str, Enum):
    monthly = "monthly"
    quarterly = "quarterly"
    yearly = "yearly"


@app.get("/cashflow/{type}/{start_date}/")
def cashflow(type: ReportType, start_date: str = Path(description="The start date for the report in format YYYY-MM-DD")):
    try:
        start_date = pd.to_datetime(start_date, format="%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Date format should be YYYY-MM-DD")
    if type not in ["monthly", "quarterly", "yearly"]:
        raise HTTPException(status_code=400, detail="Invalid report type. Report type should be monthly, quarterly, or yearly")
    data = calculate_cashflow(start_date, type=type)
    if data.empty:
        raise HTTPException(status_code=404, detail="Data not found")
    data["type"] = type
    data["period"] = data["period"].astype(str)
    data = data.to_dict(orient="records")
    # map to the Cashflow Model
    return [CashFlow(**i) for i in data]


def calculate_cashflow(start_date, type="monthly"):
    data = load_data()
    if data.empty:
        return data
    # calculate changes in key variables
    data = calculate_differences(
        data, ["Inventory", "Accounts_Receivable", "Accounts_Payable"]
    )
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.loc[data["Date"] >= start_date]
    if data.empty:
        return data
    # calculate cashflow
    data["cashflow"] = (
        data["Net_Income"]
        + data["Depreciation"]
        - data["change_in_Inventory"]
        - data["change_in_Accounts_Receivable"]
        + data["change_in_Accounts_Payable"]
    )
    if type == "monthly":
        data["month"] = pd.to_datetime(data["Date"]).dt.month
        # convert month to a readable string
        data["month_readable"] = pd.to_datetime(data["Date"]).dt.strftime("%b")
        data = data.groupby(["month", "month_readable"]).cashflow.sum().rename("cashflow").reset_index()
        data.rename(columns={"month_readable": "period"}, inplace=True)
        data.drop(columns="month", inplace=True)
    elif type == "quarterly":
        data["quarter"] = pd.to_datetime(data["Date"]).dt.quarter
        data = data.groupby("quarter").cashflow.sum().rename("cashflow").reset_index()
        data.rename(columns={"quarter": "period"}, inplace=True)
    else:
        data["year"] = pd.to_datetime(data["Date"]).dt.year
        data = data.groupby("year").cashflow.sum().rename("cashflow").reset_index()
        data.rename(columns={"year": "period"}, inplace=True)
    return data


def calculate_differences(frame, cols=[]):
    # calculate change in values in the column
    frame = frame.copy()
    for col in cols:
        frame["change_in_" + col] = frame[col].diff()
        frame["change_in_" + col].astype(float)
        frame.fillna(0, inplace=True)
    return frame


def load_data():
    # provide a way to override the DATA_DIR to use test data
    DATA_DIR = app.dependency_overrides["DATA_DIR"]
    # handel for an empty file
    try:
        pnl = pd.read_csv(DATA_DIR + "/" + settings.PNL_FILE_NAME)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()
    if pnl.empty:
        return pd.DataFrame()
    # handel for an empty file
    try:
        working_capital = pd.read_csv(DATA_DIR + "/" + settings.WORKING_CAPITAL_FILE_NAME)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()
    if working_capital.empty:
        return pd.DataFrame()
    # merge files on date and return
    data = pd.merge(pnl, working_capital, on="Date")
    return data
