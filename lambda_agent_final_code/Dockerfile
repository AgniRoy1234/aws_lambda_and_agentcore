# AWS Lambda Python 3.12 base image
FROM public.ecr.aws/lambda/python:3.12

# Set working directory inside Lambda runtime
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy dependency file first (layer caching)
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY lambda_server.py .

# Lambda entrypoint
CMD ["lambda_server.lambda_handler"]