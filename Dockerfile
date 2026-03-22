# Stage 1: Build Frontend
FROM node:18-slim AS frontend-builder
WORKDIR /app/frontend
# Copy package files first for better caching
COPY frontend/package*.json ./
RUN npm install
# Copy the rest and build
COPY frontend/ ./
RUN npm run build

# Stage 2: Final Image
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Copy built frontend from Stage 1
# This replaces the empty/missing frontend/dist in the current context
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose the mandatory HF Spaces port
EXPOSE 7860

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=7860
ENV PYTHONUNBUFFERED=1

# Create logs directory
RUN mkdir -p logs

# Command to run the application
# main.py handles initialization and starts uvicorn
CMD ["python", "main.py"]
