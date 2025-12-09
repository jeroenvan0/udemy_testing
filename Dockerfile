FROM python:slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps + Google Cloud CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        gnupg \
        ca-certificates \
        libgomp1 \
    # Download and store the GCP APT key in the keyring file that 'signed-by' uses
    # Add the repo exactly once (no -a for append)
    && apt-get update 

# Copy your application code into the image


COPY . .





# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Run your training pipeline at build time (if intended)
RUN python pipeline/training_pipeline.py

EXPOSE 8080

CMD ["python", "application.py"]
