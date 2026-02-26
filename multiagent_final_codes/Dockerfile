# ==========================================
# Use ARM64 Python Base Image (Required)
# ==========================================
FROM --platform=linux/arm64 python:3.12-slim

# ==========================================
# Environment Configuration
# ==========================================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Prevent torch from trying to use CUDA
ENV CUDA_VISIBLE_DEVICES=""
ENV TRANSFORMERS_CACHE=/app/model_cache
ENV HF_HOME=/app/model_cache
ENV SENTENCE_TRANSFORMERS_HOME=/app/model_cache
ENV LAMBDA_TASK_ROOT=/var/task

WORKDIR /app


# ==========================================
# Install Python Dependencies
# ==========================================
COPY requirements.txt .

RUN pip install --upgrade pip

# Important: Install CPU Torch first (ARM compatible)
RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    torch

# Install remaining dependencies
RUN pip install --no-cache-dir -vv -r requirements.txt

# =========================
# Download model at build time
# =========================
RUN python -c "from sentence_transformers import SentenceTransformer; \
    model = SentenceTransformer('all-MiniLM-L6-v2'); \
    model.save('/var/task/model_cache')"

# ==========================================
# Copy Application Code
# ==========================================
COPY rag_agent.py .

# ==========================================
# Expose Port (AgentCore uses 8080 internally)
# ==========================================
EXPOSE 8080

# ==========================================
# Start AgentCore Runtime
# ==========================================
CMD ["python", "rag_agent.py"]
