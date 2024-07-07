FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN  pip install --upgrade pip & pip install --no-cache-dir -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
COPY . .
# Expose port for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000 8080
# Start both FastAPI and Streamlit
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run app.py --server.port 8080"]
