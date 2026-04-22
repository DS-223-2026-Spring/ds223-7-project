import os
from sqlalchemy import create_engine
import pandas as pd

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://pulse_user:pulse_pass@db:5432/pulse")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def query(sql: str) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql(sql, conn)
