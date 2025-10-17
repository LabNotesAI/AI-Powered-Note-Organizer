FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy your watcher script into the image
COPY watcher.py /app/watcher.py

# Install dependencies once at build time
#RUN pip install --no-cache-dir watchdog pymongo requests
RUN pip install --no-cache-dir watchdog pymongo requests python-dotenv

# Run the watcher when the container starts
CMD ["python", "-u", "watcher.py"]
