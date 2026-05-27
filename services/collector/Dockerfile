FROM python:3.11-slim
WORKDIR /app
COPY common /app/common
COPY schemas /app/schemas
COPY source_schemas /app/source_schemas
COPY recommendation_rules /app/recommendation_rules
COPY services/collector/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY services/collector /app/services/collector
ENV PYTHONPATH=/app/common
CMD ["uvicorn", "services.collector.main:app", "--host", "0.0.0.0", "--port", "8000"]
