"""
Expense Tracker — FastAPI Application
Main entry point: initializes app, CORS, routes, and database.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.db.init_db import init_db
from backend.app.api.auth import router as auth_router
from backend.app.api.expenses import router as expenses_router
from backend.app.api.income import router as income_router
from backend.app.api.categories import router as categories_router
from backend.app.api.summary import router as summary_router
from backend.app.api.budgets import router as budgets_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables and seed default data."""
    init_db()
    yield


app = FastAPI(
    title="Expense Tracker API",
    description="Track your income and expenses with categories, filters, and monthly summaries.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(expenses_router)
app.include_router(income_router)
app.include_router(categories_router)
app.include_router(summary_router)
app.include_router(budgets_router)


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint — returns 200 if the server is running."""
    return {"status": "healthy", "message": "Expense Tracker API is running"}
