from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import re

from extractor import full_extraction
from check_limits import create_retriever, initialize_agent_validator, PROCESS_SUMS
from prompts import QUESTION

load_dotenv(find_dotenv())

app = FastAPI()

retriever = create_retriever()
agent_executor = initialize_agent_validator(retriever)


@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    if file.filename.endswith(".docx"):
        result = full_extraction(file.file)
        return JSONResponse(content=result)
    else:
        return JSONResponse(content={"error": "Invalid file type"}, status_code=400)


@app.post("/validate")
async def validate(file: UploadFile = File(...)):
    if file.filename.endswith(".xlsx"):
        df = pd.read_excel(file.file)
        if "Task Description" not in df.columns:
            return JSONResponse(
                content={"error": "No field 'Task Description' in file"},
                status_code=400,
            )
        if "Amount" not in df.columns:
            return JSONResponse(
                content={"error": "No field 'Amount' in file"}, status_code=400
            )
        output_values = []
        for idx, row in df.iterrows():
            condition = row["Task Description"]
            given_sum = row["Amount"]

            # predict
            bad_answer = True
            attempts = 0
            while bad_answer and attempts < 3:
                result = agent_executor.invoke(
                    {"input": QUESTION.format(conditions=condition)}
                )
                result = result["output"]
                print(result)
                if result.startswith("Agent stopped"):
                    decision = "Failed to make decision"
                    limit = "unknown"
                else:
                    bad_answer = False
                attempts += 1

            decision = None
            if not bad_answer:
                limit = PROCESS_SUMS(result).strip().split(" ")[0]
                try:
                    price = PROCESS_SUMS(given_sum)
                    price = int(price)
                except:
                    decision = f"Unknown (because cant parse current price from doc - {given_sum}). Current cost limit: {result}"
                if decision is None:
                    try:
                        limit = int(limit)
                        if limit < price:
                            decision = f"Prohibited. Current cost limit: {result} which is lower than current price {price}"
                        else:
                            decision = f"Allowed. Current cost limit: {result} which is higher than current price {price}"
                    except:
                        print(f"Failed to extract limit from {limit}, full text {result}")
                        decision = f"Unknown. Current cost limit: {result}"

            if isinstance(limit, str):
                limit = "unknown"
            if limit == "unknown":
                decision = "Failed to make decision"
            output_values.append(
                {
                    "condition": condition,
                    "requested_sum": given_sum,
                    "limit": limit,
                    "decision": decision,
                }
            )
        return JSONResponse(content={"result": output_values})
    else:
        return JSONResponse(content={"error": "Invalid file type"}, status_code=400)
