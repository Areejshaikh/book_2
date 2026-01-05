FROM python:3.11-slim

WORKDIR /app

# System tools for some python packages
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway dynamic port use karne ke liye setup
# CMD mein app ka rasta sahi hona chahiye (src folder ke andar main.py)
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]