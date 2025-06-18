#!/bin/bash

# set -e

# 1. Create virtual environment if it doesn't exist
if ! workon omnify 2>/dev/null; then
    echo "Creating virtualenv 'omnify'..."
    mkvirtualenv omnify 
else
    echo "Virtualenv 'omnify' already exists. Activating..."
    workon omnify
fi

# 2. Install requirements
if [ -f requirements.txt ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found!"
    exit 1
fi

# 3. Alembic migration steps
if [ ! -d alembic ]; then
    echo "Initializing Alembic..."
    alembic init alembic
    # User must edit alembic.ini and alembic/env.py as per README instructions
    echo "Please edit alembic.ini and alembic/env.py as per README, then re-run this script."
    exit 0
fi

# 4. Run migrations
alembic upgrade head

echo "Setup complete!"
