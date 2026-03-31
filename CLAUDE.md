# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

中小企业财务报表自动生成 SaaS — 输入历史财务数据和假设参数，自动生成符合中国企业会计准则的三年财务预测（利润表、资产负债表、现金流量表），三表联动。

Tech stack: FastAPI (Python) backend + React (TypeScript) frontend + PostgreSQL.

## Commands

### Backend (run from `backend/`)

```bash
uv sync --all-extras              # Install dependencies
uv run uvicorn app.main:app --reload  # Dev server (port 8000)
uv run pytest                     # All tests
uv run pytest tests/test_forecast_engine.py::test_name -v  # Single test
uv run alembic revision --autogenerate -m "description"    # New migration
uv run alembic upgrade head       # Apply migrations
```

### Frontend (run from `frontend/`)

```bash
npm install           # Install dependencies
npm run dev           # Dev server (port 5173, proxies /api → backend:8002)
npx tsc --noEmit      # Type-check
npm run build         # Production build
```

### Database

```bash
docker compose up -d db  # Start PostgreSQL
# Connection: postgresql+asyncpg://postgres:postgres@localhost:5432/money
```

## Architecture

```
backend/
├── app/
│   ├── main.py          # FastAPI app factory + lifespan (creates tables, seeds data)
│   ├── config.py        # pydantic-settings, loads ../.env (DB + JWT config)
│   ├── database.py      # async SQLAlchemy engine + session (pool_pre_ping=True)
│   ├── auth.py          # JWT tokens, PBKDF2 password hashing, get_current_user dependency
│   ├── seed.py          # Seeds line item definitions + general template on startup
│   ├── models/
│   │   ├── base.py      # DeclarativeBase
│   │   ├── user.py      # User model (money_users table)
│   │   └── financial.py # Company (has owner_id FK → User), IndustryTemplate, LineItemDef,
│   │                    #   FinancialPeriod, FinancialData, ForecastScenario, Assumption
│   ├── schemas/
│   │   ├── auth.py      # Register/Login/Token/User schemas
│   │   └── financial.py # Pydantic request/response schemas
│   ├── routers/
│   │   ├── auth.py        # POST /api/auth/register, login, me, refresh
│   │   ├── companies.py   # CRUD /api/companies (auth required, owner-scoped)
│   │   ├── templates.py   # GET /api/templates
│   │   ├── periods.py     # /api/companies/:id/periods (auth required)
│   │   ├── scenarios.py   # /api/companies/:id/scenarios (auth required)
│   │   └── line_items.py  # GET /api/line-items
│   └── engine/
│       ├── line_items.py        # Line item code definitions + default assumptions
│       ├── income_statement.py  # IS calculation (pure function)
│       ├── balance_sheet.py     # BS calculation (pure function)
│       ├── cash_flow.py         # CF calculation, indirect method (pure function)
│       ├── balancer.py          # Auto-balance BS via debt plug
│       └── forecast.py          # ForecastEngine class + run_forecast() wrapper
frontend/
├── src/
│   ├── types/
│   │   ├── financial.ts    # TypeScript types matching API schemas
│   │   └── auth.ts         # User, TokenResponse types
│   ├── contexts/
│   │   └── AuthContext.tsx  # Auth state management (login/register/logout, token refresh)
│   ├── api.ts              # Fetch wrappers with auto Authorization header
│   ├── pages/
│   │   ├── LoginPage.tsx      # Login form
│   │   ├── RegisterPage.tsx   # Registration form
│   │   ├── Dashboard.tsx      # Company list + create (with user header)
│   │   └── CompanyDetail.tsx  # Tabs: historical data | assumptions | statements | export
│   └── App.tsx             # AuthProvider + ProtectedRoute + Router
```

## Key Patterns

- **Authentication**: JWT-based auth (access + refresh tokens). Password hashing uses PBKDF2-SHA256 (stdlib). All `/api/companies/*` routes require auth; Company data is owner-scoped via `owner_id` FK.
- **Three-statement model**: IS drives BS, BS + IS drive CF (indirect method), CF closing cash writes back to BS. Iterative convergence handles circular debt/interest dependency.
- **EAV data storage**: Financial data stored as `(period_id, line_item_code, value)` rows — flexible for different industry templates.
- **Line item codes**: `IS_xxx` (Income Statement), `BS_A_xxx` (Assets), `BS_L_xxx` (Liabilities), `BS_E_xxx` (Equity), `CF_O/I/F_xxx` (Cash Flow). Defined in `engine/line_items.py`.
- **Pure engine functions**: The forecast engine is pure Python (dict in → dict out), no DB access. The API layer handles DB loading/saving.
- **Auto-balance**: When BS doesn't balance, the gap is added to `BS_L_001` (short-term debt). Cash (`BS_A_001`) is always determined by CF closing balance.
- **Assumptions are per-year per-scenario**: Each forecast year can have different growth rates, margins, etc.
- **Startup seeding**: `app/seed.py` seeds line item definitions and the "general" industry template on first run.
- All API routes prefixed with `/api/`
- DB sessions via `get_db()` dependency in `app/database.py`
- Python packages managed via `uv`
