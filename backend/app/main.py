from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: conditionally create tables & seed based on env var
    import os
    import asyncio
    from app.database import async_session, engine
    from app.models import Base

    # Only run migration/seed if SKIP_DB_INIT is not set
    # In Cloud Run, it's safer to run migrations via a dedicated Job instead of web instances.
    skip_db_init = os.getenv("SKIP_DB_INIT", "false").lower() == "true"
    
    if not skip_db_init:
        # Retry connection with backoff
        for attempt in range(3):
            try:
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                break
            except Exception as e:
                if attempt == 2:
                    raise
                await asyncio.sleep(1)

        from app.seed import seed_all

        async with async_session() as session:
            await seed_all(session)
    else:
        print("SKIP_DB_INIT is set to true. Skipping automatic DB creation and seeding.")

    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Money API", lifespan=lifespan)

    app.add_middleware(SecurityHeadersMiddleware)

    from app.config import settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.allowed_origins.split(",")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Register routers ──────────────────────────────────
    from app.routers.auth import router as auth_router
    from app.routers.companies import router as companies_router
    from app.routers.export import router as export_router
    from app.routers.line_items import router as line_items_router
    from app.routers.periods import router as periods_router
    from app.routers.scenarios import router as scenarios_router
    from app.routers.templates import router as templates_router

    app.include_router(auth_router)
    app.include_router(companies_router)
    app.include_router(templates_router)
    app.include_router(periods_router)
    app.include_router(scenarios_router)
    app.include_router(export_router)
    app.include_router(line_items_router)

    # ── Health check ──────────────────────────────────────

    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    # ── Serve Frontend SPA ────────────────────────────────

    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    from fastapi import Request
    import os

    # Go up from `app` -> `backend` -> `money` -> `frontend/dist`
    frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))
    
    if os.path.exists(frontend_dist):
        # Serve static assets
        app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
        
        # Serve public files like favicon, etc.
        for item in os.listdir(frontend_dist):
            item_path = os.path.join(frontend_dist, item)
            if os.path.isfile(item_path) and item != "index.html":
                # We can't mount a single file, but we can serve the directory at root
                pass # Handled below by catch-all or we can just mount the root safely for known files
                
        # Better: Mount everything except index.html and index.html is served as a fallback
        # First, add a route for specifically requested files in the root (like favicon.svg)
        @app.get("/{file_name:path}")
        async def serve_root_files(file_name: str, request: Request):
            # Exclude api paths
            if file_name.startswith("api/"):
                from fastapi import HTTPException
                raise HTTPException(status_code=404, detail="API route not found")
                
            file_path = os.path.join(frontend_dist, file_name)
            if os.path.isfile(file_path):
                return FileResponse(file_path)
            
            # SPA fallback
            index_path = os.path.join(frontend_dist, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
            return {"error": "Frontend not built"}

    return app

app = create_app()
