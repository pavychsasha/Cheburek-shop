#!/bin/bash


echo "Pulling latest changes"
git pull


# Check if .env file exists in back-end directory, create if not
ENV_FILE="./back-end/.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "Creating .env file in back-end directory..."
  cat <<EOT >> $ENV_FILE
APP_CONFIG__DB__URL=postgresql+asyncpg://postgres:postgres@postgres:5432/cheburek_db
APP_CONFIG__DB__ECHO=0
APP_CONFIG__DB__TEST_POSTGRES_URL="postgresql+asyncpg://postgres:postgres@postgres:5432/test_db"
APP_CONFIG__ACCESS_TOKEN__RESET_PASSWORD_TOKEN_SECRET=340787e504c359bd96270e367ba9a086bce56b79c5036abc77d11e0a5d2436fc
APP_CONFIG__ACCESS_TOKEN__VERIFICATION_TOKEN_SECRET=e68695768d118ba00c94348efb5d14725c74a4c2831c1f81c9a4e28de0b6f6d3
APP_CONFIG__MONGO_DB__HOST=mongo
APP_CONFIG__MONGO_DB__DATABASE_NAME=cheburek_mongo_db
APP_CONFIG__MONGO_DB__TEST_DATABASE_NAME=test_cheburek_mongo_db
APP_CONFIG__REDIS__HOST=redis
APP_CONFIG__REDIS__PORT=6379
APP_CONFIG__REDIS__DB=0
APP_CONFIG__SESSION__SECRET_KEY="93B306A6-7D22-4EBC-B3E8-2F268DE90CE7"
EOT
  echo ".env file created."
else
  echo ".env file already exists."
fi

# Build and run the Docker containers
echo "Building and running Docker containers..."
docker compose up -d --build

# Step 2: Go into the container shell and run beanie migrations
echo "Running Beanie migrations inside 'cheburek-shop-fastapi-1'..."
docker exec -it cheburek-shop-fastapi-1 sh -c "PYTHONPATH=. beanie migrate -uri 'mongodb://mongo:27017/' -db cheburek_mongo_db -p ./beanie_migrations/"

# Step 3: Run Alembic migrations and populating products
echo "Running Alembic migrations inside 'cheburek-shop-fastapi-1'..."
docker exec -it cheburek-shop-fastapi-1 sh -c "alembic upgrade head"
docker exec -it cheburek-shop-fastapi-1 sh -c "PYTHONPATH=. python3 app/actions/migrate_all_database.py"

# Step 4: Run the script to create a superuser
echo "Creating superuser..."
docker exec -it cheburek-shop-fastapi-1 sh -c "PYTHONPATH=. python3 app/actions/create_super_user.py"

echo "Setup complete!"