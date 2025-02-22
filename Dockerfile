# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV RESOURCE_TIMEOUT=60

# Set the working directory
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Add a health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
