# Use an official Ubuntu image as the base
FROM ubuntu:22.04

# Set working directory
WORKDIR /code

# Set environment variables to non-interactive to avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and essential dependencies
RUN apt-get update && \
    apt-get install -y python3.11 python3-pip && \
    apt-get clean

# Upgrade pip
RUN python3.11 -m pip install --upgrade pip

# Copy the requirements file and install Python packages
# COPY child_accounts/requirements.txt /code/
# RUN pip3 install --no-cache-dir -r /code/requirements.txt

# Copy the Lambda functions
COPY child_accounts/lambda_function /code/lambda_function

# Copy the CloudFormation template (if needed in the container)
COPY child_accounts/aws_cfn_infrastructure.yaml /code/

# Command to run when the container starts
CMD ["python3.11", "-m", "lambda_function.handler"]
