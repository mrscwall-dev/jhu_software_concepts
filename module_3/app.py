import subprocess
import sys
from pathlib import Path

from flask import Flask, flash, redirect, render_template, url_for
from sqlalchemy import func, or_, select

from models import Applicant, SessionLocal
from orm_queries import (
    question_1,
    question_4,
    question_5,
    question_8,
    question_9,
    question_10,
)


BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.secret_key = "module-3-development-key"

pull_process = None


def pull_is_running():
    """Return True if Pull Data is currently running."""

    global pull_process

    if pull_process is None:
        return False

    if pull_process.poll() is None:
        return True

    pull_process = None
    return False


def get_analysis_results():
    """Retrieve analysis results from PostgreSQL using SQLAlchemy."""

    results = {}

    results["q1"] = question_1()

    with SessionLocal() as session:
        total_classified = session.scalar(
            select(func.count())
            .select_from(Applicant)
            .where(
                Applicant.us_or_international.is_not(None),
                func.trim(Applicant.us_or_international) != "",
            )
        )

        international = session.scalar(
            select(func.count())
            .select_from(Applicant)
            .where(
                func.lower(func.trim(Applicant.us_or_international))
                == "international"
            )
        )

        results["q2"] = (
            (international / total_classified) * 100
            if total_classified
            else 0
        )

        results["gpa"] = session.scalar(select(func.avg(Applicant.gpa)))
        results["gre"] = session.scalar(select(func.avg(Applicant.gre)))
        results["gre_v"] = session.scalar(select(func.avg(Applicant.gre_v)))
        results["gre_aw"] = session.scalar(select(func.avg(Applicant.gre_aw)))

        results["q6"] = session.scalar(
            select(func.avg(Applicant.gpa)).where(
                func.lower(func.trim(Applicant.term)) == "fall 2026",
                func.lower(func.trim(Applicant.status)) == "accepted",
                Applicant.gpa.is_not(None),
            )
        )

        results["q7"] = session.scalar(
            select(func.count())
            .select_from(Applicant)
            .where(
                or_(
                    func.lower(Applicant.program).like("%johns hopkins%"),
                    Applicant.program.op("~*")(
                        r"(^|[^a-z])JHU([^a-z]|$)"
                    ),
                ),
                or_(
                    func.lower(Applicant.program).like("%computer science%"),
                    Applicant.program.op("~*")(
                        r"(^|[^a-z])CS([^a-z]|$)"
                    ),
                ),
                or_(
                    func.lower(func.trim(Applicant.degree)).like("master%"),
                    func.lower(func.trim(Applicant.degree)).in_(
                        ["ms", "m.s."]
                    ),
                ),
            )
        )

        results["q11"] = session.scalar(
            select(func.avg(Applicant.gpa)).where(
                func.lower(func.trim(Applicant.term)) == "fall 2026",
                func.lower(
                    func.trim(Applicant.us_or_international)
                )
                == "international",
                Applicant.gpa.is_not(None),
            )
        )

    results["q4"] = question_4()
    results["q5"] = question_5()
    results["q8"] = question_8()
    results["q9"] = question_9()
    results["difference"] = results["q9"] - results["q8"]
    results["q10"] = question_10()

    return results


@app.route("/")
def analysis():
    return render_template(
        "analysis.html",
        results=get_analysis_results(),
        pull_running=pull_is_running(),
    )


@app.route("/pull-data", methods=["POST"])
def pull_data():
    global pull_process

    if pull_is_running():
        flash("Pull Data is already running.")
    else:
        pull_process = subprocess.Popen(
            [sys.executable, str(BASE_DIR / "pull_data.py")],
            cwd=BASE_DIR,
        )
        flash(
            "Pull Data started. Grad Café is being checked for new records."
        )

    return redirect(url_for("analysis"))


@app.route("/update-analysis", methods=["POST"])
def update_analysis():
    if pull_is_running():
        flash(
            "New data is currently being retrieved. "
            "The analysis below uses the records currently in PostgreSQL."
        )
    else:
        flash("Analysis updated using the latest records in PostgreSQL.")

    return redirect(url_for("analysis"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)