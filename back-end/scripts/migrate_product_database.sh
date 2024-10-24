#!/bin/bash


echo "Pulling latest changes"
git pull

echo "Building and running Docker containers..."
docker compose up -d --build

# Step 4: Run the script to create a superuser
echo "Populating products with translations"
docker exec -it cheburek-shop-fastapi-1 sh -c "PYTHONPATH=. python3 app/actions/migrate_all_database.py"
docker exec -it cheburek-shop-fastapi-1 sh -c "PYTHONPATH=. python3 app/actions/create_super_user.py"


