"""
Expense Tracker — FastAPI Application
Main entry point: initializes app, CORS, routes, and database.
"""

import sys
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Debug: Print import diagnostics
print(f"[STARTUP] Python: {sys.version}", flush=True)
print(f"[STARTUP] CWD: {os.getcwd()}", flush=True)
print(f"[STARTUP] Dir contents: {os.listdir('.')}", flush=True)
print(f"[STARTUP] sys.path[0:3]: {sys.path[0:3]}", flush=True)

if os.path.isdir("backend"):
    print(f"[STARTUP] backend/ found: {os.listdir('backend')}", flush=True)
else:
    print(f"[STARTUP] WARNING: 'backend/' dir NOT found in CWD!", flush=True)
    # Check parent directories
    for check_dir in ['..', '../expense-tracker', 'expense-tracker']:
        check_path = os.path.join(os.getcwd(), check_dir, 'backend')
        if os.path.isdir(check_path):
            print(f"[STARTUP] Found backend/ at: {os.path.abspath(check_path)}", flush=True)
            # Add the parent to sys.path so imports work
            parent = os.path.abspath(os.path.join(os.getcwd(), check_dir))
            sys.path.insert(0, parent)
            os.chdir(parent)
            print(f"[STARTUP] Changed CWD to: {os.getcwd()}", flush=True)
            break

from backend.app.db.init_db import init_db
from backend.app.api.auth import router as auth_router
from backend.app.api.expenses import router as expenses_router
from backend.app.api.income import router as income_router
from backend.app.api.categories import router as categories_router
from backend.app.api.summary import router as summary_router
from backend.app.api.budgets import router as budgets_router

print("[STARTUP] All imports successful!", flush=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables and seed default data."""
    try:
        init_db()
        print("[STARTUP] Database initialized successfully!", flush=True)
    except Exception as e:
        print(f"[STARTUP] Database init failed: {e}", flush=True)
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


@app.get("/", tags=["Root"])
def root():
    """Root endpoint — confirms the API is running and lists routes."""
    routes = [{"path": r.path, "methods": list(r.methods) if hasattr(r, 'methods') else []} for r in app.routes]
    return {
        "app": "Expense Tracker API",
        "status": "running",
        "routes_count": len(routes),
        "routes": routes,
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint — returns 200 if the server is running."""
    return {"status": "healthy", "message": "Expense Tracker API is running"}


# Log all routes at import time
print(f"[STARTUP] Total routes registered: {len(app.routes)}", flush=True)
for _route in app.routes:
    _methods = getattr(_route, 'methods', set())
    print(f"[STARTUP]   Route: {_methods} {_route.path}", flush=True)
