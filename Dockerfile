# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Firefox and other dependencies
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install GeckoDriver (Firefox driver for Selenium)
RUN wget -q https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz \
    && tar -xzf geckodriver-v0.30.0-linux64.tar.gz -C /usr/local/bin/ \
    && rm geckodriver-v0.30.0-linux64.tar.gz

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the Flask application to the Docker image
COPY . /app
WORKDIR /app

# Expose the Flask port
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "your_script_name.py"]
