# Nubi Challenge

The Customers API is a CRUD for customer entities built using Django and DRF (Django Rest Framework), employing Token Authentication as an authentication class. This project has been dockerized, including a PostgreSQL service. It includes developed tests.

## Getting Started

### Prerequisites
- Clone the repository.
- Request the '.env' file from a team member and place it in the root of the project.

### Installation (for Linux):
- Install Docker Compose:
    ```bash
    sudo apt update && sudo apt upgrade -y
    sudo apt install docker-compose -y
    ```

- Add your user to the Docker Compose group:
    ```bash
    sudo usermod -aG docker $USER
    ```

- Restart the session from the terminal to apply changes (recommended to restart the OS to apply changes permanently):
    ```bash
    su - ${USER}
    ```

### Usage
- First, Docker Compose must build the images defined in the docker-compose.yml file:
    ```bash
    docker-compose build
    ```

- Then, start Docker Compose:
    ```bash
    docker-compose up
    ```

## Virtual Environment
To create migrations or new apps using Django's commands, follow these steps:

### Requirements:
- Install dependency from psycopg2-binary:
    ```bash
    sudo apt-get install libpq-dev python3-dev build-essential -y
    ```

### Setup:
- Create a virtual environment (inside the 'challenge' folder):
    ```bash
    sudo apt update && sudo apt upgrade -y
    sudo apt install python3-venv -y
    python3 -m venv ve
    ```

- Activate the virtual environment:
    ```bash
    source ve/bin/activate
    ```

- Install the requirements_dev.txt:
    ```bash
    pip install -r requirements_dev.txt
    ```

## Testing
Ensure Docker is running:
```bash
docker exec -it challenge_web_1 python manage.py test
```
