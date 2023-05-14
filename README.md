
# Project Ook

This is a digital library management tool I created for the following purposes

- Backing up my GoodReads data locally
- Ease of querying and managing my books
- Ease of creating book lists and sharing them

The name is insipired by the Librarian from the Discworld novels. 

## Usage

The tool at it's current state has three important functions. 

- Importing Data from GoodReads
- Querying the Data
- Creating and sharing lists

__Importing to Database__

GoodReads allows you to export one's own data as a csv. Create a folder `library_csv` on the root. 

`csv_to_table.py`

```    
df = read_from_csv("20230514.csv")
 write_to_table(df)
```

The schema for the database exists in `models.py`

__Querying the Database__

`query_table.py`

```
    data = {
        "date_added": {
            "lower": "2022/12/01",
            "higher": "2023/04/24"
        },
        "author": "Agatha",
    }

    data = json.dumps(data)
    db = QueryLibrary(data)
    result = json.loads(db.select_query_db())

    print(result.keys())
```

Gives the output as json object where the keys are book titles and values are info about the books. 

__Creating and Sharing Lists__

`output_formatter.py`

```
data = {
        "author": "Agatha",
        "status": "read",
        "my_rating": {
            "lower": "4.0",
            "higher": "6.0"
        }
    }

    result = get_output(data, ["title", "og_year_pub", "avg_rating"])
    print_data(result, title="Agatha Christie Books I like")
```

Will create an SVG image to the folder called `output_imgs` inside src. The Output will be something like below

![Output](sample_img/Agatha Christie Books I like.svg)
## Authors

- [@naveenpiedy](https://github.com/naveenpiedy)

