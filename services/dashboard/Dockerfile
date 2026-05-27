FROM python:3.11-slim
WORKDIR /app
COPY services/dashboard/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY source_schemas /app/source_schemas
COPY recommendation_rules /app/recommendation_rules
COPY common /app/common
COPY services/__init__.py /app/services/__init__.py
COPY services/dashboard /app/services/dashboard
ENV PYTHONPATH=/app:/app/common
CMD ["streamlit", "run", "services/dashboard/app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
