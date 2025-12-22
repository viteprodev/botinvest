FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Claw Cloud/Render usually provide PORT env var, but 8080 is a good default to expose)
EXPOSE 8080

# Command to run the application
# We use the module approach which launches our main.py (and the dummy server thread)
CMD ["python", "-m", "app.main"]
