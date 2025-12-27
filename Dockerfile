# Multi-stage build for smallest image
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Copy and build Python packages
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt && \
    pip wheel --no-cache-dir --wheel-dir /app/wheels google-genai

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget unzip && \
    wget -q https://releases.hashicorp.com/terraform/1.7.0/terraform_1.7.0_linux_amd64.zip && \
    unzip -q terraform_1.7.0_linux_amd64.zip && \
    mv terraform /usr/local/bin/ && \
    rm terraform_1.7.0_linux_amd64.zip && \
    apt-get purge -y wget unzip && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copy pre-built wheels from builder
COPY --from=builder /app/wheels /wheels

# Install Python packages from wheels
RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Copy application
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]