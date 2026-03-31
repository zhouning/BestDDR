# Stage 1: Build the React frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

# Install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# Copy the rest of the frontend source code and build it
COPY frontend/ ./
RUN npm run build

# Stage 2: Build the FastAPI backend
FROM python:3.12-slim

# Install uv for fast python package management
RUN pip install uv

WORKDIR /app/backend

# Copy python dependencies definitions
COPY backend/pyproject.toml backend/uv.lock* ./

# Install dependencies into the system python
RUN uv pip install --system -r pyproject.toml

# Copy backend source code
COPY backend/ ./

# Copy the built frontend from Stage 1 into the correct path
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose the port Cloud Run expects (8080 by default, though we'll use the PORT env var)
ENV PORT=8080
EXPOSE 8080

# Run Uvicorn and bind to 0.0.0.0 and $PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
