FROM python:3.11-slim
WORKDIR /app
COPY common /app/common
COPY recommendation_rules /app/recommendation_rules
COPY timeline_stages /app/timeline_stages
COPY services/processor/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY services/processor /app/services/processor
ENV PYTHONPATH=/app/common
CMD ["python", "-m", "services.processor.main"]
