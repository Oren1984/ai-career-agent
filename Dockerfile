FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Create data directory for SQLite
RUN mkdir -p /app/data

# Expose Streamlit port
EXPOSE 8501

# Initialize DB and start dashboard
CMD ["sh", "-c", "python scripts/init_db.py && python scripts/fetch_jobs.py && python scripts/score_jobs.py && streamlit run dashboard/streamlit_app.py --server.address=0.0.0.0 --server.port=8501"]
