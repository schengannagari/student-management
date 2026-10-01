unzip student-management.zip && cd student-management
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env # set SMS_SECRET_KEY
alembic upgrade head
python -m scripts.seed --admin-password 'ChangeMe!123' --students 200000 # optional
uvicorn app.main:app --reload # API docs at http://localhost:8000/docs
