
### `lambda_agent_final_code`

This repository contains the code for a Lambda-oriented agent server that exposes LLM-powered capabilities behind an AWS-friendly interface. It focuses on handling incoming requests, invoking language models and tools, and returning structured responses suitable for use in serverless or containerized deployments. It contains the agent created using strands framework.

### `multiagent_final_codes`

This repository implements multi-agent and retrieval-augmented generation (RAG) workflows. It coordinates multiple specialized agents, manages retrieval from backing stores (such as OpenSearch), and composes their outputs into a unified response for complex tasks. It uses 3 langgraph agents and 1 strands agent from lambda_agent_final code.

### `lambda_indexing_function_code`

This repository hosts the Lambda-based indexing or ingestion function that prepares data for RAG-style retrieval. It is responsible for processing raw documents, generating embeddings, and writing them into the configured search or vector index so they can be queried efficiently by the agent systems.It gets triggered when you upload a .txt or .pdf file into a S3 bucket.

=======
# aws_lambda_and_agentcore
AWS Lambda and AgentCore Learning Project
>>>>>>> 3e9286f88dbdb0c5e95470da5c6c682b0a00a222

