# GEMINI.md - Instructional Context for Money SaaS

## Project Overview
**Money** is a SaaS application designed for Small and Medium Enterprises (SMEs) to automatically generate three-year financial forecasts (Profit & Loss, Balance Sheet, Cash Flow) based on historical data and assumption parameters. It follows Chinese Accounting Standards (中国企业会计准则) and implements a three-statement linkage model.

## Tech Stack
- **Backend:** Python 3.12+, FastAPI, SQLAlchemy (Async), Alembic, PostgreSQL (via asyncpg).
- **Frontend:** React 19, TypeScript, Vite, React Router 7, TanStack Table 8.
- **Database:** PostgreSQL 16 (running in Docker).
- **Tooling:** `uv` for Python package management, `npm` for frontend.

## Building and Running

### Prerequisites
- Docker (for PostgreSQL)
- Python 3.12+ and `uv`
- Node.js and `npm`

### Setup & Execution
1. **Database:**
   ```bash
   docker compose up -d db
   ```
2. **Backend (from `backend/`):**
   ```bash
   uv sync --all-extras              # Install dependencies
   uv run uvicorn app.main:app --reload  # Start dev server (Port 8000)
   uv run pytest                     # Run tests
   uv run alembic upgrade head       # Apply migrations
   ```
3. **Frontend (from `frontend/`):**
   ```bash
   npm install                       # Install dependencies
   npm run dev                       # Start dev server (Port 5173, proxies to 8000)
   ```

## Architecture & Design Patterns
- **Three-Statement Model:** The engine handles the complex linkage where IS drives BS, and BS+IS drive CF (indirect method). Circular dependencies (e.g., debt and interest) are handled via iterative convergence in `backend/app/engine/balancer.py`.
- **EAV Data Storage:** Financial data is stored using an Entity-Attribute-Value pattern `(period_id, line_item_code, value)` to allow flexibility across different industry templates.
- **Pure Engine Functions:** The core forecast logic in `backend/app/engine/` is composed of pure Python functions (dict in → dict out) to facilitate testing and predictability.
- **Line Item Coding:** Uses a standardized prefix system: `IS_` (Income Statement), `BS_A_` (Assets), `BS_L_` (Liabilities), `BS_E_` (Equity), `CF_` (Cash Flow).

## Development Conventions
- **Backend:** Follow FastAPI best practices. Use `app/schemas/financial.py` for Pydantic models and `app/models/financial.py` for SQLAlchemy models.
- **Frontend:** Use functional components with hooks. TypeScript types in `frontend/src/types/` must match backend Pydantic schemas.
- **Testing:** Always add tests in `backend/tests/` for new engine logic or API endpoints. Use `pytest-asyncio` for async tests.
- **Migrations:** Use `alembic revision --autogenerate` for schema changes.
