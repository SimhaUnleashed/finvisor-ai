# Finvisor-AI
An AI agent built with Agno which uses multiple tools to give users the latest financial news and advices for their queries.

## Tech Stack:
Python, Agno framework for AI agents and streamlit for front end interface.

## How to run:
Get the following keys for the environment variable
```
GOOGLE_API_KEY=
EXA_API_KEY=
DB_USER=ai
DB_PASSWORD=ai
DB_NAME=ai
FINANCIAL_DATASETS_API_KEY=
FINNHUB_API_KEY=
ASSEMBLYAI_API_KEY =
REV_AI_KEY =
```

- Install docker desktop and run `docker compose up -d`
- Run the streamlit file using  `python -m streamlit-interface.py`

- The FastAPI server is running on localhost:8000.
- The PostgreSQL database is accessible on localhost:5432.
-  
Once started, you can:
- Test the API at localhost:8000/docs.
- Connect to Agno Playground or Agent UI:
- Open the Agno Playground app.agno.com/playground/agents.
- Add http://localhost:8000 as a new endpoint. You can name it Agent API (or any name you prefer).
- Select your newly added endpoint and start chatting with your Agents.
