import os

import pandas as pd

from src.base import Base, engine, Session
from src.models import MainLibrary


def read_from_csv():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "library_csv")
    latest_csv = os.path.join(path, "20230423.csv")
    df = pd.read_csv(latest_csv, na_filter=False)
    return df


def write_to_table(df):
    args = df.to_dict(orient="records")
    Base.metadata.create_all(engine)
    session = Session()
    for book in args:
        session.merge(MainLibrary(**book))
    session.commit()
    session.close()


df = read_from_csv()
write_to_table(df)
