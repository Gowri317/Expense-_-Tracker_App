"""
Simple wrapper to start the backend.
Adds explicit path management and debug output.
"""
import sys
import os

# Ensure the current directory is in Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print(f"[DEBUG] Python version: {sys.version}", flush=True)
print(f"[DEBUG] Current directory: {os.getcwd()}", flush=True)
print(f"[DEBUG] Script directory: {current_dir}", flush=True)
print(f"[DEBUG] sys.path: {sys.path[:5]}", flush=True)
print(f"[DEBUG] Directory contents: {os.listdir('.')}", flush=True)

# Check if backend directory exists
if os.path.isdir("backend"):
    print(f"[DEBUG] backend/ contents: {os.listdir('backend')}", flush=True)
    if os.path.isdir("backend/app"):
        print(f"[DEBUG] backend/app/ contents: {os.listdir('backend/app')}", flush=True)
else:
    print("[DEBUG] ERROR: 'backend/' directory NOT FOUND!", flush=True)
    print(f"[DEBUG] Looking for it in parent dirs...", flush=True)
    for d in ['..', '../expense-tracker']:
        full = os.path.join(current_dir, d)
        if os.path.isdir(os.path.join(full, 'backend')):
            print(f"[DEBUG] Found backend/ in: {os.path.abspath(full)}", flush=True)

try:
    from backend.app.main import app
    print(f"[DEBUG] App imported successfully!", flush=True)
    print(f"[DEBUG] Registered routes:", flush=True)
    for route in app.routes:
        methods = getattr(route, 'methods', set())
        print(f"[DEBUG]   {methods} {route.path}", flush=True)
except Exception as e:
    print(f"[DEBUG] Failed to import app: {e}", flush=True)
    import traceback
    traceback.print_exc()
    
    # Create a minimal fallback app
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    def fallback_root():
        return {"error": "Main app failed to load", "detail": str(e)}
    
    @app.get("/health")
    def fallback_health():
        return {"status": "error", "detail": str(e)}
