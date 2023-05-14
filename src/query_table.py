import itertools
import json
import datetime
from typing import Set, Dict, Any

from src.base import Session, engine
from src.models import MainLibrary
from sqlalchemy import ARRAY, cast, String, func


class QueryLibrary:
    """
    List Arguments example:

    'tags': [['discworld'], ['fiction']]

    Will return
    Feet of Clay ['discworld', 'fiction']

    'tags': ['discworld', 'fiction']

    Will return
    Feet of Clay ['discworld', 'fiction']
    Harry Potter ['fiction']

    """
    PARTIAL_SEARCH = ["title", "author", "my_review", "private_notes"]

    def __init__(self, input_json: str):
        """
        Create Session. Set Input Json query. Check keys of input are valid
        :param input_json: str (But is actually a json)
        """
        self.session = Session(bind=engine)
        self.input_json = json.loads(input_json)
        self.columns = self._check_col(self.input_json)

    @staticmethod
    def _check_col(input_json: Dict[str, Any]) -> Set[str]:
        """
        Check if all the cols mentioned are in the database table
        :param input_json: Dict (But basically is a json)
        :return: set of valid cols
        """
        ret_col = set()
        for key in input_json.keys():
            if hasattr(MainLibrary, key):
                ret_col.add(key)
            else:
                raise Exception(f"{key} column is not found.")

        return ret_col

    @staticmethod
    def _type_builder(cols: Set[str]) -> Dict[str, Any]:
        """
        Create a dict. Key -> Col Name. Value -> Col DataType
        :param cols: Set of column names
        :return: Dict
        """
        ret = dict()

        for key in cols:
            column = MainLibrary.__table__.columns.get(key)
            column_type = column.type.python_type
            if column_type == list:
                column_type = column.type.item_type.python_type
            ret[key] = column_type

        return ret

    def _check_dates(self, key: str, value: Dict[str, str] | str):
        """
        Check if the date strings provided are valid and within proper range
        :param key: Date col name
        :param value: Dict containing Date range or a single date
        """
        if isinstance(value, dict):
            lower = datetime.datetime.strptime(value.get('lower'), "%Y/%m/%d").date()
            higher = datetime.datetime.strptime(value.get('higher'), "%Y/%m/%d").date()
            if lower > higher:
                raise Exception(f"For {key}, the lower and higher values need to be interchanged")
            else:
                self.input_json[key]['lower'] = lower
                self.input_json[key]['higher'] = higher
        else:
            self.input_json[key] = datetime.datetime.strptime(value, "%Y/%m/%d").date()

    def _check_val(self):
        """
        Check if the values in the input json query are valid
        """
        col_type = self._type_builder(self.columns)

        for key, value in self.input_json.items():
            key_type = col_type.get(key)

            # Checking the date values
            try:
                if key_type is datetime.date:
                    self._check_dates(key, value)
                    continue
            except Exception:
                raise Exception(f"For {key}, the date format is off. Please use YYYY/MM/DD.")

            # Checking the other values
            try:
                match value:
                    # In case of dict, check if the range is in ascending order
                    case dict():
                        lower = key_type(value.get('lower'))
                        higher = key_type(value.get('higher'))
                        if lower > higher:
                            raise Exception(f"For {key}, the lower and higher values need to be interchanged")
                    # In case of list, check if all the nested values are of proper datatypes
                    case list():
                        flat_values = itertools.chain(*value)
                        for item in flat_values:
                            if not isinstance(item, key_type):
                                raise Exception(f"For {key}, the data_type of {item} if off. It needs to be of "
                                                f"{key_type}")
                    case key_type():
                        pass
                    case _:
                        raise Exception(f"For {key}, the data_type of {value} if off. It needs to be of {key_type}")

            except Exception:
                raise Exception(f"For {key}, the data_type of {value} if off.")

    def _select_from_database(self) -> str:
        """
        Query the database based on the input json
        :return: Str but actually Dict (Json Dumps). Key -> book titles. Value -> Json book info
        """
        query = self.session.query(MainLibrary)

        try:
            for key in self.columns:
                value = self.input_json.get(key)

                match value:
                    # In case of dict, using between to get the values in range
                    case dict():
                        query = query.filter(
                            getattr(MainLibrary, key).between(value.get('lower'), value.get('higher')))
                    case list():
                        # In case, it is a nested list, using Overlap (AND Operation)
                        if any(isinstance(i, list) for i in value):
                            for inner_value in value:
                                query = query.filter(getattr(MainLibrary, key).overlap(cast(inner_value,
                                                                                            ARRAY(String))))
                        # This following is more OR operation
                        else:
                            query = query.filter(getattr(MainLibrary, key).overlap(cast(value, ARRAY(String))))
                    case _:
                        if key not in self.PARTIAL_SEARCH:
                            query = query.filter(getattr(MainLibrary, key) == value)
                        else:
                            query = query.filter(func.lower(getattr(MainLibrary, key)).contains(value.lower()))

            result_list = dict()
            for item in query:
                result_list[item.title] = item.as_dict()
            return json.dumps(result_list, indent=4, sort_keys=True, default=str)
        except Exception:
            raise Exception

    def select_query_db(self):
        self._check_val()
        return self._select_from_database()


if __name__ == '__main__':
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
