## Tasks
### 1 - Extraction of contract terms
Main code: `extractor.py`
### 2 - Validate travel costs
Main code: `check_limits.py`


## App
The app is available on
https://legal-docs-coluyclhiq-uc.a.run.app/ 

## How to

How to run locally (without Docker):
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 
streamlit run app.py --server.port 8080
```

How to run on Google Cloud:
```bash
docker buildx build --platform linux/amd64 -t gcr.io/coherent-racer-388118/legal-doc-extraction .  

docker push gcr.io/coherent-racer-388118/legal-doc-extraction  
 
gcloud run deploy legal-docs --image gcr.io/coherent-racer-388118/legal-doc-extraction --platform managed --region us-central1 --project coherent-ra
cer-388118 --port 8080 --set-env-vars OPENAI_API_KEY=KEYVALUE --memory 2Gi
```
