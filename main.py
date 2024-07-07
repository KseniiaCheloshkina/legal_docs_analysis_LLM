from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from dotenv import load_dotenv, find_dotenv
import pandas as pd

from extractor import full_extraction
from check_limits import create_retriever, initialize_agent_validator, PROCESS_SUMS
from prompts import QUESTION

load_dotenv(find_dotenv())

app = FastAPI()


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
        retriever = create_retriever()
        agent_executor = initialize_agent_validator(retriever)
        output_values = []
        for idx, row in df.iterrows():
            condition = row["Task Description"]
            given_sum = row["Amount"]
            try:
                price = PROCESS_SUMS(given_sum)
                price = int(price)
            except:
                return JSONResponse(
                    content={
                        "error": f"Error in price conversion to int (row {idx}, value {given_sum}). Check your file"
                    },
                    status_code=400,
                )

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

            if not bad_answer:
                limit = PROCESS_SUMS(result.split(" ")[0])
                if int(limit) < price:
                    decision = f"Prohibited. Current cost limit: {result} which is lower than current price {price}"
                else:
                    decision = f"Allowed. Current cost limit: {result} which is higher than current price {price}"

            output_values.append(
                {
                    "condition": condition,
                    "requested_sum": given_sum,
                    "limit": limit,
                    "decision": decision,
                }
            )
            if idx > 2:
                break
        return JSONResponse(content={"result": output_values})
    else:
        return JSONResponse(content={"error": "Invalid file type"}, status_code=400)
