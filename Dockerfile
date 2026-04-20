FROM python:3.11-slim

# SECURITY: Set environment variables to prevent python from writing pyc files to disc
# and to prevent python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# SECURITY: Create a non-root user to run the application
RUN adduser --disabled-password --gecos "" appuser

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and frontend directories
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appuser /app

# SECURITY: Switch to non-root user
USER appuser

# Expose port (Cloud Run expects 8080 by default)
EXPOSE 8080

# Command to run the application securely
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
