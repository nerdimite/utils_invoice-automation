#!/bin/bash

# Build the Docker image
docker build -t cellstrat-invoice-automation .

# Replace account ID in ECR repository URL
ACCOUNT_ID=800756380562

# Create ECR repository if it doesn't exist
# aws ecr create-repository --repository-name cellstrat-invoice-automation --region us-east-1 --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag and push the Docker image to ECR
docker tag cellstrat-invoice-automation:latest $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cellstrat-invoice-automation:latest
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cellstrat-invoice-automation:latest