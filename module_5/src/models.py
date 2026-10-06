"""Define the SQLAlchemy database models for the GradCafe application."""

# pylint: disable=too-few-public-methods

import os
from datetime import date

from sqlalchemy import Date, Float, Integer, String, URL, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME"),
)


class Base(DeclarativeBase):
    """Provide the base class for SQLAlchemy models."""


class Applicant(Base):
    """Represent an applicant record in the GradCafe database."""

    __tablename__ = "applicants"

    p_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    program: Mapped[str | None] = mapped_column(String, nullable=True)
    comments: Mapped[str | None] = mapped_column(String, nullable=True)
    date_added: Mapped[date | None] = mapped_column(Date, nullable=True)
    url: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)
    term: Mapped[str | None] = mapped_column(String, nullable=True)
    us_or_international: Mapped[str | None] = mapped_column(String, nullable=True)
    gpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    gre: Mapped[float | None] = mapped_column(Float, nullable=True)
    gre_v: Mapped[float | None] = mapped_column(Float, nullable=True)
    gre_aw: Mapped[float | None] = mapped_column(Float, nullable=True)
    degree: Mapped[str | None] = mapped_column(String, nullable=True)
    llm_generated_program: Mapped[str | None] = mapped_column(String, nullable=True)
    llm_generated_university: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )


engine = create_engine(DATABASE_URL)

SESSION_LOCAL = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)
