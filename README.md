
### `lambda_agent_final_code`

This repository contains the code for a Lambda-oriented agent server that exposes LLM-powered capabilities behind an AWS-friendly interface. It focuses on handling incoming requests, invoking language models and tools, and returning structured responses suitable for use in serverless or containerized deployments. It contains the agent created using strands framework.

### `multiagent_final_codes`

This repository implements multi-agent and retrieval-augmented generation (RAG) workflows. It coordinates multiple specialized agents, manages retrieval from backing stores (such as OpenSearch), and composes their outputs into a unified response for complex tasks. It uses 3 langgraph agents and 1 strands agent from lambda_agent_final code. This is deployed in the agentcore.

### `lambda_indexing_function_code`

This repository hosts the Lambda-based indexing or ingestion function that prepares data for RAG-style retrieval. It is responsible for processing raw documents, generating embeddings, and writing them into the configured search or vector index so they can be queried efficiently by the agent systems.It gets triggered when you upload a .txt or .pdf file into a S3 bucket.

=======

To build docker images for lambda function the command is docker build -t <image_name> .
But for Agentcore, since it uses ARM64 architecture, the command is docker buildx build --platform linux/arm64 -t <image_name> . 

Proper IAM permissions need to be given to the agentcore and lambda functions.


