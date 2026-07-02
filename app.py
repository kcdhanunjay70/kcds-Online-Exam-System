import os
import secrets
from datetime import datetime, timezone

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from pymongo import MongoClient
from pymongo.errors import PyMongoError


QUESTIONS = [
    {
        "id": 1,
        "category": "Python",
        "question": "Which keyword creates a function in Python?",
        "options": ["func", "define", "def", "lambda"],
        "answer": 2,
    },
    {
        "id": 2,
        "category": "Database",
        "question": "MongoDB stores records as which type of document?",
        "options": ["CSV", "BSON", "XML", "YAML"],
        "answer": 1,
    },
    {
        "id": 3,
        "category": "Web",
        "question": "Which HTTP method is normally used to create a resource?",
        "options": ["GET", "TRACE", "POST", "HEAD"],
        "answer": 2,
    },
    {
        "id": 4,
        "category": "JavaScript",
        "question": "Which declaration creates a block-scoped constant?",
        "options": ["var", "static", "let", "const"],
        "answer": 3,
    },
    {
        "id": 5,
        "category": "Flask",
        "question": "What does a Flask route decorator connect?",
        "options": ["A URL to a view function", "CSS to HTML", "MongoDB to Python", "A test to CI"],
        "answer": 0,
    },
    {
        "id": 6,
        "category": "HTML",
        "question": "Which element is intended for page navigation links?",
        "options": ["<section>", "<nav>", "<aside>", "<main>"],
        "answer": 1,
    },
    {
        "id": 7,
        "category": "CSS",
        "question": "Which layout system is best suited to rows and columns together?",
        "options": ["Float", "Position", "Grid", "Inline"],
        "answer": 2,
    },
    {
        "id": 8,
        "category": "Git",
        "question": "Which command records staged changes in repository history?",
        "options": ["git push", "git commit", "git fetch", "git clone"],
        "answer": 1,
    },
    {
        "id": 9,
        "category": "Security",
        "question": "Where should production secrets be stored?",
        "options": ["Source code", "README", "Environment variables", "Browser localStorage"],
        "answer": 2,
    },
    {
        "id": 10,
        "category": "DevOps",
        "question": "What is the main purpose of a CI workflow?",
        "options": ["Run automated checks", "Design a logo", "Store passwords", "Replace Git"],
        "answer": 0,
    },
]

_memory_results = []


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", secrets.token_hex(24)),
        MONGO_URI=os.getenv("MONGO_URI", "mongodb://localhost:27017/online_exam"),
        EXAM_SECONDS=int(os.getenv("EXAM_SECONDS", "600")),
        TESTING=False,
    )
    if test_config:
        app.config.update(test_config)

    def results_collection():
        if app.config.get("TESTING") and not app.config.get("MONGO_URI"):
            return None
        try:
            client = MongoClient(app.config["MONGO_URI"], serverSelectionTimeoutMS=800)
            client.admin.command("ping")
            return client.get_default_database()["results"]
        except (PyMongoError, TypeError):
            return None

    @app.get("/")
    def index():
        return render_template("index.html", question_count=len(QUESTIONS))

    @app.post("/start")
    def start():
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        if not name or not email:
            return redirect(url_for("index", error="Please enter your name and email."))
        session.clear()
        session.update(candidate={"name": name, "email": email}, exam_token=secrets.token_urlsafe(12))
        return redirect(url_for("exam"))

    @app.get("/exam")
    def exam():
        if "candidate" not in session:
            return redirect(url_for("index"))
        public_questions = [
            {key: value for key, value in question.items() if key != "answer"} for question in QUESTIONS
        ]
        return render_template(
            "exam.html",
            candidate=session["candidate"],
            questions=public_questions,
            exam_seconds=app.config["EXAM_SECONDS"],
        )

    @app.post("/submit")
    def submit():
        if "candidate" not in session:
            return redirect(url_for("index"))
        answers = request.form
        correct = sum(
            str(question["answer"]) == answers.get(f"question_{question['id']}")
            for question in QUESTIONS
        )
        attempted = sum(answers.get(f"question_{question['id']}") is not None for question in QUESTIONS)
        percentage = round((correct / len(QUESTIONS)) * 100)
        result = {
            "candidate": session["candidate"],
            "score": correct,
            "total": len(QUESTIONS),
            "attempted": attempted,
            "percentage": percentage,
            "passed": percentage >= 60,
            "submitted_at": datetime.now(timezone.utc),
        }
        collection = results_collection()
        if collection is not None:
            collection.insert_one(result.copy())
        else:
            _memory_results.append(result.copy())
        session["last_result"] = {
            key: value for key, value in result.items() if key != "submitted_at"
        }
        return redirect(url_for("result"))

    @app.get("/result")
    def result():
        if "last_result" not in session:
            return redirect(url_for("index"))
        return render_template("result.html", result=session["last_result"])

    @app.get("/api/health")
    def health():
        collection = results_collection()
        return jsonify(status="healthy", database="mongodb" if collection is not None else "memory")

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")
