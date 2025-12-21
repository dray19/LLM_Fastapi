# LLM Model with FastAPI for Electricity Trade Analysis

## Overview

This repository showcases the development of a **Large Language Model (LLM)** powered API using **FastAPI** for analyzing electricity trading data. The focus is to leverage the power of machine learning to analyze, predict, and provide insights into electricity trading trends.

## Features

- **FastAPI Implementation**: A web framework for building high-performance APIs, providing robust HTTP handling and ease of integration.
- **Electricity Trade Analysis**: Use LLM models to analyze intricate electricity trading patterns.
- **Ease of Deployment**: Engineered for scalability and integration with modern infrastructure.

## Technologies Used

- **Python**: Core language for all components.
- **FastAPI**: High-performance web framework for building APIs.
- **LLM Models**: Integrating cutting-edge machine learning models for trade analysis.

### Installation

1. Create a virtual environment (optional but recommended):
    ```bash
    python -m venv env
    source env/bin/activate    # On Windows use `env\Scripts\activate`
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

1. Start the FastAPI server:
    ```bash
    uvicorn main:app --reload
    ```
   Here, `main` refers to the filename and `app` is the FastAPI instance.

2. Open your web browser and visit:
    ```
    http://127.0.0.1:8000/docs
    ```
   This will bring up an interactive API documentation generated automatically by FastAPI.

## Project Structure

The following depicts a high-level overview of the project structure:

```
LLM_Fastapi/
│
├── api
│   └── main.py
├── app.py
├── example_trading_data_models493.csv
├── executor.py
├── llm.py
├── README.md
├── requirements.txt
├── pages
│   ├── 2_Prediction_Explorer.py
│   └── 2_Trade_Results_Explorer.py
├── test_trade_data.csv
├── test_trade_results_data.csv
```

## Test Data

- **test_trade_data.csv**: Example dataset for the "Prediction_Explorer" page and can also be using on the main LLM app
- **test_trade_results_data.csv**: Example dataset for the "Trade_Results_Exploret" page and can also be using on the main LLM app

