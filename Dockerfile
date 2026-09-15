# EMP-12: Job & Skill Terminology Simplifier
# Reproducible Docker Container Definition

FROM python:3.11-slim

# Set environment variables for non-interactive and unbuffered execution
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Set working directory
WORKDIR /app

# Install system dependencies if required for C-extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies first for layer caching
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application source, data, models, and UI configuration
COPY src/ ./src/
COPY data/ ./data/
COPY models/ ./models/
COPY .streamlit/ ./.streamlit/
COPY app.py .
COPY .env.example .

# Create non-root user for security hardening
RUN useradd -m -u 1000 emp12user && \
    chown -R emp12user:emp12user /app
USER emp12user

# Expose Streamlit port
EXPOSE 8501

# Healthcheck for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Start Streamlit application
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
