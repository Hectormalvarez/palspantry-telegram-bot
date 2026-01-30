FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# libpq-dev and gcc are needed for psycopg2 (though this project uses SQLite)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Copy application code
COPY . .

# Set default command
CMD ["python", "bot_main.py"]