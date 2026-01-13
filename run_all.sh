#!/bin/bash

mkdir -p logs

echo "Starting FastAPI..."
python -m uvicorn api.main:app --reload > logs/fastapi.out 2>&1 &

echo "Starting Streamlit..."
python -m streamlit run app.py > logs/streamlit.out 2>&1 &

echo "Started both apps"
echo "FastAPI log:   logs/fastapi.out"
echo "Streamlit log: logs/streamlit.out"