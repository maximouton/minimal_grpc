# Use a lightweight Python image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
COPY dataaccessdev.planifique.eu-crt.pem .
COPY dataaccessdev.planifique.eu-key.pem .
RUN pip install --no-cache-dir -r requirements.txt && echo "Dependencies installed successfully" > /dev/stdout

# Copy your application code
COPY . .

# Expose gRPC port
EXPOSE 54329

# Optionally set environment variables if you want 
# to switch to production mode inside the container
ENV PYTHONOPTIMIZE=1

# Set environment variables
ENV database_dev=rdb_dev
ENV db_host=51.159.24.14
ENV db_port=15242
ENV dbusername=planifique
ENV keycloak_client_id=appdev
ENV keycloak_issuer=https://authdev.planifique.eu/realms/planifiquedev
ENV db_password=FcCD9J!J@MQYa6ot

# Run the gRPC server
ENTRYPOINT ["python", "server/main.py"]
