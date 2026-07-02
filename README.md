# Quizora — Online Exam System

A colorful, responsive MCQ examination portal built with Flask, MongoDB, HTML, CSS, and vanilla JavaScript. Candidates can enter their details, complete a timed assessment, navigate between questions, and receive instant results.

## Features

- 10-question MCQ assessment with category labels
- Live countdown with automatic submission
- Question palette, answer progress, and browser auto-save
- Instant pass/fail result and score breakdown
- MongoDB result storage with graceful in-memory fallback
- Responsive, accessible interface for desktop and mobile
- Flask health endpoint, automated tests, Docker, GitHub Actions, and Render blueprint

## Tech stack

Python 3.12 · Flask · MongoDB/PyMongo · HTML5 · CSS3 · JavaScript · Pytest · Gunicorn

## Run locally

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
python app.py
```

Open `http://localhost:5000`. Start MongoDB locally to persist results. If MongoDB is unavailable, the app remains fully functional with temporary in-memory result storage.

## Run with Docker

```bash
docker compose up --build
```

This starts both the web application and MongoDB. Data is retained in the `mongo_data` Docker volume.

## Configuration

| Variable | Purpose | Default |
| --- | --- | --- |
| `SECRET_KEY` | Signs Flask sessions | Random per process |
| `MONGO_URI` | MongoDB connection URI | `mongodb://localhost:27017/online_exam` |
| `EXAM_SECONDS` | Exam duration in seconds | `600` |
| `PORT` | Local server port | `5000` |

For production, always set a persistent `SECRET_KEY` and a MongoDB Atlas `MONGO_URI`.

## Test

```bash
pytest -q
```

GitHub Actions runs the test suite on every push and pull request to `main`.

## Deploy on Render

1. Create a MongoDB Atlas database and copy its connection string.
2. In Render, create a new Blueprint and select this repository.
3. Render detects `render.yaml`.
4. Enter `MONGO_URI` when prompted and deploy.

The `/api/health` endpoint reports application and database availability.

## Project structure

```text
.
├── .github/workflows/ci.yml
├── static/css/style.css
├── static/js/exam.js
├── templates/
├── tests/test_app.py
├── app.py
├── docker-compose.yml
├── Dockerfile
├── render.yaml
└── requirements.txt
```

## License

This project is provided for educational use.
