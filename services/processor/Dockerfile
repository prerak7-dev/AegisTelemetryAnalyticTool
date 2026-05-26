FROM python:3.11-slim
WORKDIR /app
COPY common /app/common
COPY services/processor/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY services/processor /app/services/processor
ENV PYTHONPATH=/app/common
CMD ["python", "-m", "services.processor.main"]
