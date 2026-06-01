# 💰 Expense Tracker

A full-stack personal finance tracker built with **FastAPI**, **Streamlit**, and **SQLite/PostgreSQL**.

Track your income, expenses, and savings with beautiful charts and a modern dark-mode UI.

## ✨ Features

- **User Authentication** — JWT-based login and registration
- **Expense Tracking** — Add, edit, delete expenses with categories
- **Income Tracking** — Record multiple income sources
- **Dashboard** — Monthly summary cards, pie charts, and bar charts
- **Transaction History** — Filterable, editable transaction list
- **Custom Categories** — Add your own expense categories
- **Monthly Summaries** — Income vs expenses breakdown by month

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Frontend | Streamlit, Plotly, Pandas |
| Database | SQLite (default) / PostgreSQL |
| Auth | JWT (python-jose), bcrypt |

## 📁 Project Structure

```
expense-tracker/
  backend/
    app/
      api/          # Route handlers (auth, expenses, income, categories, summary)
      models/       # SQLAlchemy ORM models
      schemas/      # Pydantic request/response schemas
      services/     # Business logic layer
      core/         # Config, security helpers
      db/           # Database connection, initialization
    tests/          # Unit tests
  frontend/
    pages/          # Dashboard, Add Expense, Add Income, History
    utils/          # API client, auth helpers
    .streamlit/     # Streamlit theme config
  .env.example
  requirements.txt
```

## 🚀 Local Setup

### 1. Clone and install

```bash
git clone <your-repo-url>
cd expense-tracker
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 2. Configure environment

```bash
copy .env.example .env
# Edit .env if needed (defaults work out of the box with SQLite)
```

### 3. Start the backend

```bash
cd expense-tracker
uvicorn backend.app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 4. Start the frontend (new terminal)

```bash
cd expense-tracker
streamlit run frontend/app.py
```

App opens at: http://localhost:8501

## 🧪 Running Tests

```bash
cd expense-tracker
pytest backend/tests/ -v
```

## 📝 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./expense_tracker.db` | Database connection string |
| `SECRET_KEY` | `dev-secret-key-...` | JWT signing secret |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Token lifetime (24h) |
| `BACKEND_URL` | `http://localhost:8000` | Backend URL for frontend |

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login, get JWT token |
| GET | `/api/expenses/` | List expenses (filterable) |
| POST | `/api/expenses/` | Create expense |
| PUT | `/api/expenses/{id}` | Update expense |
| DELETE | `/api/expenses/{id}` | Delete expense |
| GET | `/api/income/` | List income |
| POST | `/api/income/` | Create income |
| PUT | `/api/income/{id}` | Update income |
| DELETE | `/api/income/{id}` | Delete income |
| GET | `/api/categories/` | List categories |
| POST | `/api/categories/` | Create custom category |
| GET | `/api/summary/?month=YYYY-MM` | Monthly summary |
