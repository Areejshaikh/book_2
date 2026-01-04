# 1. Python image select karein
FROM python:3.11-slim

# 2. Work directory banayein
WORKDIR /app

# 3. Zaroori system tools install karein
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# 4. Requirements copy aur install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Saara code copy karein
COPY . .

# 6. Railway ka PORT use karne ke liye setup
EXPOSE 8000

# 7. App ko start karne ki command (Aapki file app.py hai)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]