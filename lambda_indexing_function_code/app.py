import os
import json
import boto3
import numpy as np
from typing import List
from io import BytesIO
from urllib.parse import unquote_plus

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# =========================
# Configuration (Env Vars)
# =========================

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
OPENSEARCH_ENDPOINT = os.getenv("OPENSEARCH_ENDPOINT")
INDEX_NAME = os.getenv("INDEX_NAME")
REGION = os.getenv("REGION")
SERVICE = os.getenv("SERVICE_NAME")  # "aoss" or "es"

MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TEXT_THRESHOLD = 1000


# =========================
# AWS Clients
# =========================

s3 = boto3.client("s3")
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    REGION,
    SERVICE,
    session_token=credentials.token,
)

opensearch = OpenSearch(
    hosts=[{"host": OPENSEARCH_ENDPOINT.replace("https://", ""), "port": 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
)

os.environ["HF_TOKEN"] = HUGGINGFACE_TOKEN

# =========================
# Load Embedding Model (Global for Reuse)
# =========================
model_path = os.path.join(os.environ['LAMBDA_TASK_ROOT'], 'model_cache')

# Load the model from the LOCAL path, not the internet
# This prevents the "Read-only file system" error
model = SentenceTransformer(model_path)

# =========================
# File Readers
# =========================

def read_txt(content: bytes) -> str:
    return content.decode("utf-8")


def read_pdf(content: bytes) -> str:
    
    reader = PdfReader(BytesIO(content))
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text


# =========================
# Text Splitting
# =========================

def split_text(text: str) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start = end - CHUNK_OVERLAP
    return chunks


def prepare_chunks(text: str) -> List[str]:
    if len(text) > TEXT_THRESHOLD:
        return split_text(text)
    return [text]


# =========================
# Create Index if Not Exists
# =========================

def ensure_index_exists():
    if not opensearch.indices.exists(index=INDEX_NAME):

        index_body = {
            "settings": {
                "index": {
                    "knn": True
                }
            },
            "mappings": {
                "properties": {
                    "content": {"type": "text"},
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": 384
                    }
                }
            }
        }

        opensearch.indices.create(
            index=INDEX_NAME,
            body=index_body
        )
        print("Index Created")


# =========================
# Store Embeddings
# =========================

def index_documents(chunks: List[str]):
    embeddings = model.encode(
        chunks,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    
    print("started embeddings")

    for i, chunk in enumerate(chunks):
        doc = {
            "content": chunk,
            "embedding": embeddings[i].tolist()
        }

        opensearch.index(
            index=INDEX_NAME,
            body=doc
        )


# =========================
# Lambda Handler
# =========================

def lambda_handler(event, context):

    try:
        # Parse S3 event
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = unquote_plus(event["Records"][0]["s3"]["object"]["key"])

        # Get file from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response["Body"].read()

        # Detect file type
        if key.lower().endswith(".txt"):
            text = read_txt(content)

        elif key.lower().endswith(".pdf"):
            text = read_pdf(content)

        else:
            return {"statusCode": 400, "body": "Unsupported file type"}

        # Prepare chunks
        chunks = prepare_chunks(text)
        
        print("These are chunks")
        print(chunks)

        # Ensure index
        print("check index started")
        ensure_index_exists()
        print("check index completed")
        
        print("index started")
        # Index documents
        index_documents(chunks)
        print("index completed")

        return {
            "statusCode": 200,
            "body": f"Indexed {len(chunks)} chunks from {key}"
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": str(e)
        }
