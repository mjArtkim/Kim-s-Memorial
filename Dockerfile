# Stage 1: Build Vue.js Frontend for Kim's Memorial
# FROM node:18 AS frontend-builder
# WORKDIR /app/frontend
# COPY frontend/package*.json ./
# RUN npm install
# COPY frontend/ ./
# RUN npm run build

# Stage 2: Python Backend
FROM python:3.9-slim
WORKDIR /app

# Install dependencies
COPY backend/requirements.txt ./
# Update pip first to avoid issues
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend assets (Pre-built mode)
COPY frontend/dist ./frontend/dist
# COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create directories for data and photos
RUN mkdir -p backend/data backend/photos

# Expose port
EXPOSE 7554

# Run the application
WORKDIR /app/backend
CMD ["python", "app.py"]
