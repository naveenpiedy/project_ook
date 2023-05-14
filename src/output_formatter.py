import json
import re
from random import shuffle

import pandas as pd
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


def get_output(query, parameters_to_print=None, title_to_use=None):
    data = json.dumps(query)
    db = QueryLibrary(data)
    result = json.loads(db.select_query_db())
    result_items = [i for i in result.values()]
    df = pd.DataFrame(result_items)
    df['title'] = df['title'].apply(title_cleaner)
    if parameters_to_print:
        df = df[parameters_to_print]

    print_data(df, title_to_use)


def print_data(df, title):
    console = Console(record=True, width=100)
    table = Table(title=title, title_style="blue bold", border_style="dodger_blue2")

    headers = df.columns.values.tolist()
    shuffled_colors = COLORS
    shuffle(shuffled_colors)

    for header in headers:
        if header in ["title"]:
            table.add_column(header, justify="left", style="blue_violet", no_wrap=True)
        else:
            table.add_column(header, justify="center", style=shuffled_colors.pop(), no_wrap=True)

    for value in df.values:
        value = [str(i) for i in value]
        table.add_row(*value)

    console.print(table, justify="center")

    console.save_svg(f"output_imgs/{title}.svg", title=title, theme=MONOKAI)


def title_cleaner(title):
    cleaned_title = re.sub(r"\(.*\)", "", title)
    cleaned_title = cleaned_title.strip()
    return cleaned_title


if __name__ == '__main__':
    data = {
        "author": "Agatha",
        "status": "read",
        "my_rating": {
            "lower": "4.0",
            "higher": "6.0"
        }
    }

    get_output(data, ["title", "og_year_pub", "avg_rating"], title_to_use="Agatha Christie Books I like")