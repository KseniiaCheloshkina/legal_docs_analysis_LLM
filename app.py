import streamlit as st
import requests
import pandas as pd


st.title("Automation of document analysis with LLM")
tab1, tab2 = st.tabs(["Terms Extraction", "Validation of travel expenses"])

# Task 1
with tab1:
    st.header("Terms Extraction")
    uploaded_file = st.file_uploader("Upload a DOCX file with Contract", type=["docx"])

    if uploaded_file:
        if st.button("Run extraction"):
            with st.spinner("Extracting data..."):
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type,
                    )
                }
                response = requests.post("http://127.0.0.1:8000/extract", files=files)
                if response.status_code == 200:
                    result = response.json()
                    st.json(result)
                else:
                    st.error(
                        "Failed to extract data. Please check the file and try again."
                    )

# Task 2
with tab2:
    st.header("Validation of travel expenses")
    uploaded_file = st.file_uploader("Upload an Excel file with Travel Costs", type=["xlsx"])
    if uploaded_file:
        if st.button("Check validity"):
            with st.spinner("Analyzing your data..."):
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type,
                    )
                }
                response = requests.post("http://127.0.0.1:8000/validate", files=files)
                if response.status_code == 200:
                    result = response.json()
                    df_out = pd.DataFrame(result["result"])
                    st.dataframe(df_out)
                else:
                    st.error("Failed to validate. Please check the file and try again.")
