#!/bin/bash

# Create .env file in the ./back-end folder with specified environment variables
cat <<EOL > ./back-end/.env
APP_CONFIG__DB__URL=postgresql+asyncpg://postgres:postgres@postgres:5432/cheburek_db
APP_CONFIG__DB__ECHO=0
APP_CONFIG__ACCESS_TOKEN__RESET_PASSWORD_TOKEN_SECRET=$(openssl rand -base64 32)
APP_CONFIG__ACCESS_TOKEN__VERIFICATION_TOKEN_SECRET=$(openssl rand -base64 32)
EOL

echo ".env file created in the ./back-end folder."

# Run Docker Compose with build and detached options
docker-compose up --build -d

echo "Docker Compose is up and running."
