"""ORM-модель SQLAlchemy описывает таблицу и объекты, связанные с ней."""

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("length(author) BETWEEN 1 AND 120", name="review_author_length"),
        CheckConstraint("length(text) BETWEEN 1 AND 10000", name="review_text_length")
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String(120))
    text: Mapped[str] = mapped_column(String(10000))

    def is_valid(self):
        return self.author and self.text

    def normalize(self):
        self.author = self.author.strip()
        self.text = self.text.strip()
