# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV TERRAFORM_VERSION=1.0.11
ENV ANSIBLE_VERSION=2.10.7

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
    curl \
    unzip \
    sshpass \
    && rm -rf /var/lib/apt/lists/*

# Install Terraform
RUN curl -O https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    mv terraform /usr/local/bin/ && \
    rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip

# Install Ansible
RUN pip install ansible==${ANSIBLE_VERSION}

# Verify installations
RUN terraform --version && ansible --version

# Set the default command to bash
CMD ["bash"]