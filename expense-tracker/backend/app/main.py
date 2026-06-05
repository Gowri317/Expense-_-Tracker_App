"""
Expense Tracker — FastAPI Application
Main entry point: initializes app, CORS, routes, and database.
"""

import sys
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure the current directory is in Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

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
    try:
        init_db()
        print("[STARTUP] Database initialized successfully!", flush=True)
    except Exception as e:
        print(f"[STARTUP] Database init failed (non-fatal): {e}", flush=True)
        logging.error(f"Database initialization failed: {e}")
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


@app.api_route("/", methods=["GET", "HEAD"], tags=["Root"])
def root():
    """Root endpoint — Render health check (supports both GET and HEAD)."""
    return JSONResponse(
        content={"status": "ok", "app": "Expense Tracker API", "version": "1.0.0"},
        status_code=200,
    )


@app.api_route("/health", methods=["GET", "HEAD"], tags=["Health"])
def health_check():
    """Health check endpoint — returns 200 if the server is running."""
    return JSONResponse(
        content={"status": "healthy", "message": "Expense Tracker API is running"},
        status_code=200,
    )
