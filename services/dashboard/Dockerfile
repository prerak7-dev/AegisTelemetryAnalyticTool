FROM python:3.11-slim
WORKDIR /app
COPY services/dashboard/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY services/dashboard /app/services/dashboard
CMD ["streamlit", "run", "services/dashboard/app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
