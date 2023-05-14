import os

import pandas as pd
from pandas import DataFrame

from src.base import Base, engine, Session
from src.models import MainLibrary


def read_from_csv(filename: str) -> DataFrame:
    """
    Read data from CSV and out it as a pandas dataframe for manipulation.
    Place the csv file in library_csv folder
    :return: DataFrame
    """
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "library_csv")
    latest_csv = os.path.join(path, filename)
    lib_dataframe = pd.read_csv(latest_csv, na_filter=False)
    return lib_dataframe


def write_to_table(lib_dataframe: DataFrame):
    """
    Write the contents of the dataframe to the database
    :param lib_dataframe: Dataframe
    """
    args = lib_dataframe.to_dict(orient="records")
    Base.metadata.create_all(engine)
    session = Session()
    for book in args:
        session.merge(MainLibrary(**book))
    session.commit()
    session.close()


if __name__ == '__main__':
    df = read_from_csv("20230514.csv")
    write_to_table(df)
