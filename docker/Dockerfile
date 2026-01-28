# Use Python 3.11 slim image
FROM python:3.11-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY ../requirements.txt .
COPY ./docker/start /start
COPY ./docker/create_super_admin app/create_super_admin

# Make start script executable
RUN chmod +x /start
RUN chmod +x app/create_super_admin

# Install Python dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt
# Copy application code
COPY .. .

# Create necessary directories
RUN mkdir -p uploads tmp

# Expose port
EXPOSE 5000

# Run the application
CMD ["/start"]
