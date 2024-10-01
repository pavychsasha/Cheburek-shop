# Cheburek Shop

This project is a FastAPI + React application that provides a marketplace-like functionality with PostgreSQL and MongoDB databases.

## Getting Started

### Prerequisites

Make sure you have the following installed on your machine:

- **Git**: To clone the repository.
- **Docker** and **Docker Compose**: To build and run the services.
- **Bash**: To run the `setup.sh` script. (For Windows users, use WSL or Git Bash.)

### Pulling the Repository

To get started, clone the project from the GitHub repository by running the following command:

```bash
git clone https://github.com/ost1qq/Cheburek-shop.git
```

This will create a local copy of the repository on your machine.

## Running the Setup Script

After cloning the repository, navigate into the project directory:

```bash
cd Cheburek-shop
```

Now, you need to run the `setup.sh` script to build and set up the environment:

### Ensure the script has executable permissions (macOS/Linux):

```bash
chmod +x setup.sh
```

### Run the setup script:

```bash
./setup.sh
```

This script will:
- Check if the `.env` file exists in the `back-end` folder, and create it with necessary environment variables if it doesn't.
- Build and start the Docker containers for the FastAPI, React, PostgreSQL, and MongoDB services in daemon mode.

## Verifying the Setup

Once the script finishes running, Docker will have all your services running in the background. You can verify this by running:

```bash
docker-compose ps
```

You should see the `postgres`, `fastapi`, `react`, and `mongo` services running.

To stop the services, use:

```bash
docker-compose down
```

## Notes

- If you need to make any adjustments to the `.env` file, it's located at `./back-end/.env`.
- The Docker containers expose the following ports:
  - **PostgreSQL**: `5432`
  - **FastAPI**: `8000`
  - **React**: `5173`
  - **MongoDB**: `27017`

## Future Enhancements

This setup is designed to work on both macOS and Windows (via WSL). Make sure to use an environment that supports Bash for seamless execution.
