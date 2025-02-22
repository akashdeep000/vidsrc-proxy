# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV RESOURCE_TIMEOUT=60

# Set the working directory
WORKDIR /app

#============================
# Install Linux Dependencies
#============================
RUN apt-get update
RUN apt-get install -y \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libu2f-udev \
    libvulkan1 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2

#==========================
# Install useful utilities
#==========================
RUN apt-get update
RUN apt-get install -y xdg-utils ca-certificates

#=================================
# Install Bash Command Line Tools
#=================================
RUN apt-get update
RUN apt-get -qy --no-install-recommends install \
    curl \
    sudo \
    unzip \
    vim \
    wget \
    xvfb

#================
# Install Chrome
#================
RUN apt-get update
RUN apt-get install -y chromium


# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip show gunicorn

# Copy the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Add a health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]