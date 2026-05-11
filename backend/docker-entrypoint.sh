#!/bin/sh

# Handle persistent configuration mapping
if [ ! -f /app/config.json ] && [ -f /app/config_data/config.json ]; then
    cp /app/config_data/config.json /app/config.json
fi

# Start the init script to create config.json and admin user if needed
python3 /app/init_env_config.py

# Persist it to the mapped volume
mkdir -p /app/config_data
if [ -f /app/config.json ]; then
    cp /app/config.json /app/config_data/config.json
fi

# Then run the main uvicorn app
exec uvicorn main:app --host 0.0.0.0 --port 8000
