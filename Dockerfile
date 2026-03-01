# ============================================
# Stage 1: Builder
# ============================================
FROM python:3.11-slim AS builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION=1.0.0

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Create virtual environment
RUN python -m venv /opt/venv

# Activate virtual environment and install dependencies
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 2: Runtime
# ============================================
FROM python:3.11-slim AS runtime

# Set build-time labels
ARG BUILD_DATE
ARG VERSION=1.0.0
ARG VCS_REF

# Set metadata labels
LABEL org.opencontainers.image.title="JartBROWSER Backend"
LABEL org.opencontainers.image.description="FastAPI Backend for JartBROWSER - Agentic Browser Automation Platform"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.authors="JartOS Team"
LABEL org.opencontainers.image.vendor="JartOS"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=UTF-8 \
    PATH="/opt/venv/bin:$PATH" \
    APP_USER=appuser \
    APP_HOME=/app \
    DATABASE_DIR=/app/data

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create non-root user and directories
RUN groupadd -r ${APP_USER} && \
    useradd -r -g ${APP_USER} -d ${APP_HOME} -s /sbin/nologin -c "JartBROWSER application user" ${APP_USER} && \
    mkdir -p ${APP_HOME} ${APP_HOME}/data ${APP_HOME}/logs ${DATABASE_DIR} && \
    chown -R ${APP_USER}:${APP_USER} ${APP_HOME} ${DATABASE_DIR} && \
    chmod 755 ${APP_HOME}

# Set working directory
WORKDIR ${APP_HOME}

# Copy application code
COPY backend/src/ ./src/
COPY backend/alembic.ini ./

# Set ownership
RUN chown -R ${APP_USER}:${APP_USER} ${APP_HOME}

# Switch to non-root user
USER ${APP_USER}

# Expose ports
EXPOSE 8000 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
