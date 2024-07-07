import streamlit as st
import requests
import pandas as pd


st.title("Streamlit and FastAPI Integration")

# Create a sidebar with a selectbox for tabs
# tab = st.sidebar.selectbox("Choose a task", ["Terms Extraction", "Validation of travel expenses"])
tab1, tab2 = st.tabs(["Terms Extraction", "Validation of travel expenses"])

# Task 1
# if tab == "Terms Extraction":
with tab1:
    st.header("Terms Extraction")
    # File uploader
    uploaded_file = st.file_uploader("Upload a DOCX file", type=["docx"])

    if uploaded_file:
        # Display the 'Run extraction' button
        if st.button("Run extraction"):
            with st.spinner("Extracting data..."):
                # Call the FastAPI extract endpoint
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
# elif tab == "Validation of travel expenses":
with tab2:
    st.header("Validation of travel expenses")
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])
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
                    print(result)
                    df_out = pd.DataFrame(result["result"])
                    st.dataframe(df_out)
                else:
                    st.error("Failed to validate. Please check the file and try again.")
