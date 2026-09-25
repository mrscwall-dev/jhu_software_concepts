import subprocess
import sys
from pathlib import Path

from flask import Flask, render_template
from sqlalchemy import func, or_, select

from src.models import Applicant, SessionLocal
from src.orm_queries import (
    question_1,
    question_4,
    question_5,
    question_8,
    question_9,
    question_10,
)


BASE_DIR = Path(__file__).resolve().parent
MODULE_DIR = BASE_DIR.parent

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
                func.lower(
                    func.trim(
                        Applicant.us_or_international
                    )
                )
                == "international"
            )
        )

        results["q2"] = (
            (international / total_classified) * 100
            if total_classified
            else 0
        )

        results["gpa"] = session.scalar(
            select(func.avg(Applicant.gpa))
        )

        results["gre"] = session.scalar(
            select(func.avg(Applicant.gre))
        )

        results["gre_v"] = session.scalar(
            select(func.avg(Applicant.gre_v))
        )

        results["gre_aw"] = session.scalar(
            select(func.avg(Applicant.gre_aw))
        )

        results["q6"] = session.scalar(
            select(func.avg(Applicant.gpa)).where(
                func.lower(
                    func.trim(Applicant.term)
                )
                == "fall 2026",
                func.lower(
                    func.trim(Applicant.status)
                )
                == "accepted",
                Applicant.gpa.is_not(None),
            )
        )

        results["q7"] = session.scalar(
            select(func.count())
            .select_from(Applicant)
            .where(
                or_(
                    func.lower(
                        Applicant.program
                    ).like("%johns hopkins%"),
                    Applicant.program.op("~*")(
                        r"(^|[^a-z])JHU([^a-z]|$)"
                    ),
                ),
                or_(
                    func.lower(
                        Applicant.program
                    ).like("%computer science%"),
                    Applicant.program.op("~*")(
                        r"(^|[^a-z])CS([^a-z]|$)"
                    ),
                ),
                or_(
                    func.lower(
                        func.trim(
                            Applicant.degree
                        )
                    ).like("master%"),
                    func.lower(
                        func.trim(
                            Applicant.degree
                        )
                    ).in_(["ms", "m.s."]),
                ),
            )
        )

        results["q11"] = session.scalar(
            select(func.avg(Applicant.gpa)).where(
                func.lower(
                    func.trim(Applicant.term)
                )
                == "fall 2026",
                func.lower(
                    func.trim(
                        Applicant.us_or_international
                    )
                )
                == "international",
                Applicant.gpa.is_not(None),
            )
        )

    results["q4"] = question_4()
    results["q5"] = question_5()
    results["q8"] = question_8()
    results["q9"] = question_9()
    results["difference"] = (
        results["q9"] - results["q8"]
    )
    results["q10"] = question_10()

    return results


def create_app(
    test_config=None,
    scraper=None,
    loader=None,
    query_func=None,
):
    """Create and configure the Flask application."""

    app = Flask(__name__)
    app.secret_key = "module-3-development-key"

    if test_config is not None:
        app.config.update(test_config)

    if query_func is None:
        query_func = get_analysis_results

    @app.route("/")
    @app.route("/analysis")
    def analysis():
        pull_running = (
            app.config.get(
                "PULL_IN_PROGRESS",
                False,
            )
            or pull_is_running()
        )

        return render_template(
            "analysis.html",
            results=query_func(),
            pull_running=pull_running,
        )

    @app.route("/pull-data", methods=["POST"])
    def pull_data():
        global pull_process

        if app.config.get(
            "PULL_IN_PROGRESS",
            False,
        ):
            return {"busy": True}, 409

        if pull_is_running():
            return {"busy": True}, 409

        if (
            scraper is not None
            and loader is not None
        ):
            rows = scraper()
            loader(rows)

            return {"ok": True}, 200

        pull_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "src.pull_data",
            ],
            cwd=MODULE_DIR,
        )

        return {"ok": True}, 202

    @app.route(
        "/update-analysis",
        methods=["POST"],
    )
    def update_analysis():
        if app.config.get(
            "PULL_IN_PROGRESS",
            False,
        ):
            return {"busy": True}, 409

        if pull_is_running():
            return {"busy": True}, 409

        query_func()

        return {"ok": True}, 200

    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    app.run(
        debug=True,
        port=5001,
    )