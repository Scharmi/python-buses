#!/bin/bash

while true; do
    python3 gather_data.py $1
    if [ $? -ne 0 ]; then
        echo "gather_data.py stopped. Restarting..."
        sleep 5
    else
        break
    fi
done
