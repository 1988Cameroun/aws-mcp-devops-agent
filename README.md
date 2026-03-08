## AWS MCP DevOps Agent

An AI-powered infrastructure agent that uses Anthropic's Model Context 
Protocol (MCP) to query and report on real AWS infrastructure.

## What it does

The agent exposes AWS resources as MCP tools that Claude can call 
autonomously to answer infrastructure questions:

- `list_ec2_instances` — queries running EC2 instances and their state
- `list_s3_buckets` — lists S3 buckets with creation metadata
- `check_iam_roles` — enumerates IAM roles and attached policies
- `describe_vpc_network` — maps VPC and subnet configuration

## Key observation

The agent decides which tools to call based on the query — it is not 
scripted. This demonstrates how MCP enables AI models to interact with 
real infrastructure rather than simulated environments.

## Stack

Python, Anthropic MCP, boto3, AWS (EC2, S3, IAM, VPC)

## Setup
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Add `ANTHROPIC_API_KEY` and AWS credentials to `.env`, then run:
```bash
python -m aws_mcp_agent.agent
```
