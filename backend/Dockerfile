FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Django specifically for the web service
RUN pip install django

# Copy the application code
COPY . .

# Expose the port
EXPOSE 8000

# Start the Django development server
CMD ["python", "backend/manage.py", "runserver", "0.0.0.0:8000"]