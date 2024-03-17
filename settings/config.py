from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    TEST_DATA_DIR: str = os.path.join(BASE_DIR, "test_data")
    PNL_FILE_NAME: str = "pnl.csv"
    WORKING_CAPITAL_FILE_NAME: str = "working_capital.csv"
