import os
from datetime import date

from sqlalchemy import Date, Float, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://localhost/gradcafe",
)


class Base(DeclarativeBase):
    pass


class Applicant(Base):
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

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)