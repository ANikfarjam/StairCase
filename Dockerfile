# Use slim Python base image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy only needed folders and files
COPY Agent/ ./Agent/
COPY BackEnd/ ./BackEnd/
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask API port
EXPOSE 5001

# Start Flask using the module path (good for modular packages)
CMD ["python3", "-m", "BackEnd.stairCase_Server"]
