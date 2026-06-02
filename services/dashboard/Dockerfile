FROM python:3.11-slim
WORKDIR /app

COPY services/dashboard/requirements.txt /app/requirements.txt
COPY simulator/requirements.txt /app/simulator-requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt -r /app/simulator-requirements.txt

COPY config /app/config
COPY source_schemas /app/source_schemas
COPY recommendation_rules /app/recommendation_rules
COPY timeline_stages /app/timeline_stages
COPY common /app/common
COPY simulator /app/simulator
COPY sql /app/sql
COPY notebooks /app/notebooks
COPY docs /app/docs
COPY openapi /app/openapi
COPY infra /app/infra
COPY tools /app/tools
COPY services/__init__.py /app/services/__init__.py
COPY services/dashboard /app/services/dashboard
COPY services/dashboard/assets /app/services/dashboard/assets

RUN mkdir -p /app/data

ENV PYTHONPATH=/app:/app/common
CMD ["streamlit", "run", "services/dashboard/app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
