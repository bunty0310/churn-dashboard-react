# Dockerfile

# --- Stage 1: Build the React Frontend ---
# We start with a Node.js image, which has all the tools needed to build our React app.
# We give this stage a name, "builder", so we can refer to it later.
FROM node:18-alpine AS builder

# Set the working directory inside the container for our frontend code.
WORKDIR /app/frontend

# Copy the package description files.
COPY frontend/package.json frontend/package-lock.json ./
# 'npm ci' is a clean install, often faster and more reliable for CI/CD than 'npm install'.
RUN npm ci

# Copy the rest of the frontend source code.
COPY frontend/ ./
# This command compiles our React app into optimized, static HTML, CSS, and JS files.
# The output is placed in the '/app/frontend/build' directory.
RUN npm run build

# --- Stage 2: Build the Final Python Application ---
# Now we start fresh with a slim Python image for our final container.
FROM python:3.9-slim

# Set the working directory for the final application.
WORKDIR /app

# Install Python dependencies first, as they change less often.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy our backend and ML scripts.
COPY backend/ ./backend/
COPY scripts/ ./scripts/

# Copy the mlruns directory which contains our trained model artifact.
COPY mlruns/ ./mlruns/

# This is the key step of the multi-stage build. We copy ONLY the 'build' folder
# from the 'builder' stage into our final image. We don't need the node_modules
# or the entire Node.js environment, which keeps our final image small.
COPY --from=builder /app/frontend/build ./frontend/build

# Tell Docker that our application will run on port 7860.
# This is the standard port for Hugging Face Spaces.
EXPOSE 7860

# The command to run when the container starts.
# We use Gunicorn, a production-ready web server, to run our Flask app.
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--chdir", "backend", "api:app"]