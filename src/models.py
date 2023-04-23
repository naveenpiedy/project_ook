import hashlib
from datetime import datetime

from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Float,
    Date,
    ARRAY,
    Enum,
    Text,
    Boolean,
)

from src.base import Base


def sha_gen(book_id, date_added):
    wanted_sha = f"{book_id}{date_added}"
    return hashlib.sha1(wanted_sha.encode()).hexdigest()


class MainLibrary(Base):
    __tablename__ = "main_library"

    id = Column(Integer, primary_key=True)
    book_id = Column(BigInteger, index=True, unique=True)
    sha = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, index=True)
    author = Column(String, index=True)
    author_lf = Column(String, index=True)
    author_adds = Column(String)
    isbn = Column(String, index=True)
    isbn_13 = Column(String, index=True)
    number_of_pages = Column(Integer)
    my_rating = Column(Float)
    avg_rating = Column(Float)
    publisher = Column(String)
    binding = Column(String)
    year_pub = Column(Integer)
    og_year_pub = Column(Integer)
    date_read = Column(Date)
    date_added = Column(Date)
    tags = Column(ARRAY(String))
    tags_with_ranks = Column(ARRAY(String))
    status = Column(String, index=True)
    my_review = Column(Text)
    spoiler = Column(Boolean)
    private_notes = Column(Text)
    read_count = Column(Integer)
    owned_copies = Column(Integer)

    def __init__(self, **kwargs):
        self.book_id = kwargs.get("Book Id")
        self.sha = sha_gen(kwargs.get("Book Id"), kwargs.get("Date Added"))
        self.title = kwargs.get("Title")
        self.author = kwargs.get("Author")
        self.author_lf = kwargs.get("Author l-f")
        self.author_adds = kwargs.get("Additional Authors")
        self.isbn = self.convert_isbn(kwargs.get("ISBN"))
        self.isbn_13 = self.convert_isbn(kwargs.get("ISBN13"))
        self.number_of_pages = self.check_int(kwargs.get("Number of Pages"))
        self.my_rating = self.check_float(kwargs.get("My Rating"))
        self.avg_rating = self.check_float(kwargs.get("Average Rating"))
        self.publisher = kwargs.get("Publisher")
        self.binding = kwargs.get("Binding")
        self.year_pub = self.check_int(kwargs.get("Year Published"))
        self.og_year_pub = self.check_int(kwargs.get("Original Publication Year"))
        self.date_read = self.convert_date(kwargs.get("Date Read"))
        self.date_added = self.convert_date(kwargs.get("Date Added"))
        self.tags = self.convert_to_list(kwargs.get("Bookshelves"))
        self.tags_with_ranks = self.convert_to_list(
            kwargs.get("Bookshelves with positions")
        )
        self.status = kwargs.get("Exclusive Shelf")
        self.my_review = kwargs.get("My Review")
        self.spoiler = self.convert_boolean(kwargs.get("Spoiler"))
        self.private_notes = kwargs.get("Private Notes")
        self.read_count = self.check_int(kwargs.get("Read Count"))
        self.owned_copies = self.check_int(kwargs.get("Owned Copies"))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @staticmethod
    def check_int(value):
        try:
            if value and int(value):
                return value
        except ValueError:
            return

    @staticmethod
    def check_float(value):
        try:
            if value and float(value):
                return value
        except ValueError:
            return

    @staticmethod
    def convert_date(date_str):
        if date_str and isinstance(date_str, str):
            return datetime.strptime(date_str, "%Y/%m/%d").date()

    @staticmethod
    def convert_to_list(list_str):
        if list_str:
            return list_str.split(",")

    @staticmethod
    def convert_boolean(boolean_str):
        if boolean_str == "true":
            return True
        else:
            return False

    @staticmethod
    def convert_isbn(isbn_str):
        # ="9780060853976"

        isbn_str.replace("=", "")
        return isbn_str
