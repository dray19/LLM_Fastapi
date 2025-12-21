import streamlit as st
import pandas as pd
import requests

API_URL = "http://127.0.0.1:8000/analyze"

st.set_page_config(page_title="Chat Trade Bot", layout="wide")
st.title("Chat Trade Bot")

uploaded = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
    st.subheader("Preview")
    st.dataframe(df.head())

    question = st.text_input("Ask a question about the data")

    if question:
        payload = {
            "csv_data": df.to_dict(orient="records"),
            "question": question
        }

        with st.spinner("Thinking..."):
            resp = requests.post(API_URL, json=payload).json()

        st.subheader("Generated Python Code")
        try:
            # Try to display the code
            st.code(resp["code"], language="python")
        except Exception as code_error:
            # Show fallback if st.code encounters an issue
            st.error("An error occurred while displaying the code.")
            st.write("Here is the raw code as text:")
            st.text(resp.get("code", ""))

        st.subheader("Result")

        if resp["result_type"] == "dataframe":
            st.dataframe(pd.DataFrame(resp["result"]))

        elif resp["result_type"] == "series":
            st.json(resp["result"])

        else:
            st.write(resp["result"])