"""Streamlit client for the CSV RAG API in main2.py."""

import io

import pandas as pd
import requests
import streamlit as st

API_URL = "http://127.0.0.1:5000"


def upload_csv(uploaded_file):
    response = requests.post(
        f"{API_URL}/upload",
        files={"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")},
        timeout=120,
    )
    if response.ok:
        return response.json()
    try:
        st.error(response.json().get("error", "Upload failed."))
    except ValueError:
        st.error("Upload failed.")
    return None


def api_post(endpoint, payload):
    try:
        response = requests.post(f"{API_URL}/{endpoint}", json=payload, timeout=120)
        body = response.json()
        if response.ok:
            return body
        st.error(body.get("error", "Request failed."))
    except requests.RequestException:
        st.error("Cannot reach the Flask API. Start it with: python main2.py")
    return None


st.set_page_config(page_title="Business Analytics RAG", page_icon="📊")
st.title("Business Analytics with Gemini RAG")
st.caption("CSV → row-aware chunks → Gemini embeddings → Chroma vector DB → retrieval → Gemini answer")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is None:
    st.info("Upload a CSV to create embeddings and start querying it.")
    st.stop()

# Streamlit reruns on interaction: index each selected file only once.
file_key = f"{uploaded_file.name}:{uploaded_file.size}"
if st.session_state.get("file_key") != file_key:
    with st.spinner("Chunking and embedding the CSV…"):
        result = upload_csv(uploaded_file)
    if result:
        st.session_state.file_key = file_key
        st.session_state.document_id = result["document_id"]
        st.session_state.description = result["description"]
        st.session_state.chunks_indexed = result["chunks_indexed"]

document_id = st.session_state.get("document_id")
if not document_id:
    st.stop()

st.success(f"Indexed {st.session_state.chunks_indexed} chunks in the persistent vector database.")
with st.expander("Dataset schema and preview"):
    st.code(st.session_state.description)
    try:
        st.dataframe(pd.read_csv(io.BytesIO(uploaded_file.getvalue())), use_container_width=True)
    except (pd.errors.ParserError, UnicodeDecodeError):
        st.warning("The API indexed the file, but the preview could not be rendered.")

tab_query, tab_summary = st.tabs(["Ask the data", "Summary"])
with tab_query:
    question = st.text_input("Question", placeholder="Which product has the highest sales?")
    top_k = st.slider("Retrieved chunks", 1, 10, 4)
    if st.button("Answer with RAG", type="primary") and question:
        with st.spinner("Retrieving relevant chunks and asking Gemini…"):
            result = api_post("query", {"document_id": document_id, "question": question, "top_k": top_k})
        if result:
            st.subheader("Answer")
            st.write(result["answer"])
            with st.expander("Retrieved sources"):
                st.dataframe(pd.DataFrame(result["sources"]), use_container_width=True)

with tab_summary:
    if st.button("Create RAG summary"):
        with st.spinner("Retrieving representative chunks…"):
            result = api_post("summarize", {"document_id": document_id})
        if result:
            st.write(result["summary"])
