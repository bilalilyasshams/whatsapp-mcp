FROM golang:1.24-alpine AS go-builder

WORKDIR /app
COPY whatsapp-bridge/go.mod whatsapp-bridge/go.sum ./
RUN go mod download

COPY whatsapp-bridge/ ./
RUN go build -o whatsapp-bridge main.go

FROM python:3.11-slim AS python-base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copy Python server files
COPY whatsapp-mcp-server/ ./whatsapp-mcp-server/
WORKDIR /app/whatsapp-mcp-server

# Install Python dependencies
RUN uv sync

# Copy Go binary from builder
COPY --from=go-builder /app/whatsapp-bridge /app/whatsapp-bridge

# Create directories for data persistence
RUN mkdir -p /app/store /app/media

# Expose ports
EXPOSE 8000 3000

# Create startup script
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
