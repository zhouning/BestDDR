# Full-Stack Project Initialization Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Initialize a full-stack application with FastAPI backend, React+Vite frontend, and PostgreSQL database, with working dev environment and basic health-check endpoint.

**Architecture:** Monorepo with `backend/` (FastAPI + SQLAlchemy async + Alembic) and `frontend/` (React + TypeScript + Vite). Backend serves API on port 8000, frontend dev server on port 5173 with proxy to backend. PostgreSQL accessed via async SQLAlchemy with Alembic migrations.

**Tech Stack:** Python 3.14, FastAPI, SQLAlchemy (async), Alembic, PostgreSQL, asyncpg, uv (package manager), React 19, TypeScript, Vite, pnpm/npm

---

## File Structure

```
money/
├── backend/
│   ├── pyproject.toml          # Python project config + dependencies
│   ├── alembic.ini             # Alembic migration config
│   ├── alembic/
│   │   ├── env.py              # Alembic environment (uses async engine)
│   │   └── versions/           # Migration scripts
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app factory + root router
│   │   ├── config.py           # Settings via pydantic-settings
│   │   ├── database.py         # Async engine + session factory
│   │   └── models/
│   │       ├── __init__.py
│   │       └── base.py         # SQLAlchemy declarative base
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py         # Fixtures (async client, test db)
│       └── test_health.py      # Health endpoint test
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts          # Vite config with API proxy
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   └── App.css
│   └── public/
├── docker-compose.yml          # PostgreSQL service
├── .env.example                # Environment variable template
├── .gitignore
└── CLAUDE.md
```

---

### Task 1: Git + root config files

**Files:**
- Create: `.gitignore`
- Create: `.env.example`
- Create: `docker-compose.yml`

- [ ] **Step 1: Initialize git repo**

```bash
cd /d/money
git init
```

- [ ] **Step 2: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
.venv/

# Node
node_modules/
frontend/dist/

# Environment
.env

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 3: Create .env.example**

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/money
```

- [ ] **Step 4: Create docker-compose.yml**

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: money
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

- [ ] **Step 5: Commit**

```bash
git add .gitignore .env.example docker-compose.yml
git commit -m "chore: add gitignore, env template, and docker-compose for postgres"
```

---

### Task 2: Backend project scaffolding

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/database.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/base.py`
- Create: `backend/app/main.py`
- Create: `backend/tests/__init__.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "money-backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.34",
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.30",
    "alembic>=1.14",
    "pydantic-settings>=2.7",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.25",
    "httpx>=0.28",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- [ ] **Step 2: Create app/config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/money"

    model_config = {"env_file": "../.env"}


settings = Settings()
```

- [ ] **Step 3: Create app/database.py**

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(settings.database_url)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session
```

- [ ] **Step 4: Create app/models/base.py and app/models/__init__.py**

`backend/app/models/base.py`:
```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

`backend/app/models/__init__.py`:
```python
from app.models.base import Base

__all__ = ["Base"]
```

- [ ] **Step 5: Create app/main.py**

```python
from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="Money API")

    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
```

- [ ] **Step 6: Create empty __init__.py files**

```bash
touch backend/app/__init__.py backend/tests/__init__.py
```

- [ ] **Step 7: Install dependencies**

```bash
cd /d/money/backend
uv sync --all-extras
```

- [ ] **Step 8: Commit**

```bash
cd /d/money
git add backend/
git commit -m "feat: scaffold FastAPI backend with config, database, and health endpoint"
```

---

### Task 3: Backend tests

**Files:**
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_health.py`

- [ ] **Step 1: Write test fixtures in conftest.py**

```python
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
```

- [ ] **Step 2: Write health endpoint test**

```python
import pytest


async def test_health_returns_ok(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 3: Run test to verify it passes**

```bash
cd /d/money/backend
uv run pytest tests/test_health.py -v
```

Expected: PASS — `test_health_returns_ok PASSED`

- [ ] **Step 4: Commit**

```bash
cd /d/money
git add backend/tests/
git commit -m "test: add health endpoint test with async client fixture"
```

---

### Task 4: Alembic migration setup

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/` (empty dir)

- [ ] **Step 1: Initialize alembic**

```bash
cd /d/money/backend
uv run alembic init alembic
```

- [ ] **Step 2: Edit alembic.ini — set sqlalchemy.url to empty (we use env.py)**

In `backend/alembic.ini`, change:
```
sqlalchemy.url = driver://user:pass@localhost/dbname
```
to:
```
sqlalchemy.url =
```

- [ ] **Step 3: Replace alembic/env.py with async version**

```python
import asyncio

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings
from app.models import Base

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(url=settings.database_url, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    engine = create_async_engine(settings.database_url)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

- [ ] **Step 4: Commit**

```bash
cd /d/money
git add backend/alembic.ini backend/alembic/
git commit -m "chore: configure alembic with async PostgreSQL support"
```

---

### Task 5: Frontend scaffolding

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/App.css`

- [ ] **Step 1: Scaffold React+Vite project**

```bash
cd /d/money
npm create vite@latest frontend -- --template react-ts
```

- [ ] **Step 2: Install frontend dependencies**

```bash
cd /d/money/frontend
npm install
```

- [ ] **Step 3: Configure Vite proxy for API**

Replace `frontend/vite.config.ts` with:

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
```

- [ ] **Step 4: Replace App.tsx with minimal app that calls health endpoint**

```tsx
import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [status, setStatus] = useState<string>("loading...");

  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then((data) => setStatus(data.status))
      .catch(() => setStatus("error"));
  }, []);

  return (
    <div>
      <h1>Money</h1>
      <p>API status: {status}</p>
    </div>
  );
}

export default App;
```

- [ ] **Step 5: Commit**

```bash
cd /d/money
git add frontend/
git commit -m "feat: scaffold React+Vite frontend with API proxy"
```

---

### Task 6: CLAUDE.md

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Create CLAUDE.md with project-specific guidance**

(Content defined in the main task — see below)

- [ ] **Step 2: Commit**

```bash
cd /d/money
git add CLAUDE.md
git commit -m "docs: add CLAUDE.md for Claude Code"
```
