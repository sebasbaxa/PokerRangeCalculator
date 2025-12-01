# Python backend (Flask)
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first (better layer caching)
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy app
COPY . .

# Create instance dir for SQLite
RUN mkdir -p instance

EXPOSE 5000

# Start the API
RUN pip install --no-cache-dir gunicorn
CMD ["gunicorn", "-w", "1", "--threads", "8", "-b", "0.0.0.0:5000", "main:app"]