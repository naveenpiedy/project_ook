import json
import re
from random import shuffle
from typing import List, Dict, Any

import pandas as pd
from pandas import DataFrame
from rich.console import Console
from rich.table import Table
from rich.terminal_theme import MONOKAI

from src.query_table import QueryLibrary

COLORS = [
    "purple",
    "turquoise2",
    "indian_red",
    "orchid1",
    "sandy_brown"
]


def get_output(query: Dict[str, Any], parameters_to_print: List[str] = None) -> DataFrame:
    """
    Query the database, Clean the data, filter it to only parameters required
    :param query: Dict. Input query
    :param parameters_to_print: List of str. Col names. Specify the col names to print
    """
    query_json = json.dumps(query)
    db = QueryLibrary(query_json)
    result = json.loads(db.select_query_db())
    result_items = [i for i in result.values()]
    result_df = pd.DataFrame(result_items)
    result_df['title'] = result_df['title'].apply(book_title_cleaner)
    if parameters_to_print:
        result_df = result_df[parameters_to_print]

    return result_df

    # print_data(result_df, title_to_use)


def print_data(results_df: DataFrame, title: str):
    """
    Print the result in a Table Format and also generate an SVG to share
    :param results_df: Cleaned up Dataframe from get_output
    :param title: Title for the search
    """
    console = Console(record=True, width=100)
    table = Table(title=title, title_style="blue bold", border_style="dodger_blue2")

    headers = results_df.columns.values.tolist()
    shuffled_colors = COLORS
    shuffle(shuffled_colors)

    for header in headers:
        if header in ["title"]:
            table.add_column(header, justify="left", style="blue_violet", no_wrap=True)
        else:
            table.add_column(header, justify="center", style=shuffled_colors.pop(), no_wrap=True)

    for value in results_df.values:
        value = [str(i) for i in value]
        table.add_row(*value)

    console.print(table, justify="center")

    console.save_svg(f"output_imgs/{title}.svg", title=title, theme=MONOKAI)


def book_title_cleaner(title: str) -> str:
    """
    Titles of book often contain series information
    Example: 'The Mystery of the Blue Train (Hercule Poirot, #6)'
    Cleaning this to 'The Mystery of the Blue Train'
    :param title: str
    :return: str
    """
    cleaned_title = re.sub(r"\(.*\)", "", title)
    cleaned_title = cleaned_title.strip()
    return cleaned_title


if __name__ == '__main__':
    data = {
        "tags": ['discworld'],
        "status": "read",
        "my_rating": {
            "lower": "3.0",
            "higher": "6.0"
        }
    }

    result = get_output(data, ["title", "avg_rating", "my_rating", "number_of_pages"])
    print_data(result, title="Discworld City Watch")
