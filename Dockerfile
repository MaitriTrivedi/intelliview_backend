FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create data directory for SQLite
RUN mkdir -p /app/intelliview/data && chmod 777 /app/intelliview/data

# Default command
CMD ["sh", "-c", "cd intelliview && python manage.py runserver 0.0.0.0:8000"]
