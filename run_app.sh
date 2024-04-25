#!/bin/sh

streamlit run streamlit_app.py & uvicorn fastapi_app:app --reload
