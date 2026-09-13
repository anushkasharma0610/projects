"""Flask API for CSV Retrieval-Augmented Generation (RAG).

Set GOOGLE_API_KEY before starting. Dependencies:
    pip install flask pandas chromadb google-generativeai
"""

import logging
import os
import uuid
from pathlib import Path

import chromadb
import google.generativeai as genai
import pandas as pd
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
VECTOR_DB_FOLDER = BASE_DIR / "chroma_db"
EMBEDDING_MODEL = "models/text-embedding-004"
CHAT_MODEL = "gemini-1.5-flash"
CHUNK_ROWS = 25
MAX_CHUNK_CHARACTERS = 6_000

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
UPLOAD_FOLDER.mkdir(exist_ok=True)
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY is not set. Add it to your environment before starting the API.")
genai.configure(api_key=api_key)
model = genai.GenerativeModel(CHAT_MODEL)

# This vector database is persisted locally, so indexed uploads survive restarts.
chroma_client = chromadb.PersistentClient(path=str(VECTOR_DB_FOLDER))
collection = chroma_client.get_or_create_collection("csv_rag")


def dataset_description(df: pd.DataFrame) -> str:
    lines = [f"Rows: {len(df)}", f"Columns: {', '.join(map(str, df.columns))}", "Data types:"]
    lines.extend(f"- {column}: {dtype}" for column, dtype in df.dtypes.items())
    return "\n".join(lines)


def build_chunks(df: pd.DataFrame, filename: str) -> list[dict]:
    """Chunk by rows, retaining headers and source row range in every chunk."""
    chunks, columns = [], ", ".join(map(str, df.columns))
    for start in range(0, len(df), CHUNK_ROWS):
        end = min(start + CHUNK_ROWS, len(df))
        rows = df.iloc[start:end].fillna("").astype(str)
        row_text = "\n".join(
            f"Row {index}: " + "; ".join(f"{column}={value}" for column, value in row.items())
            for index, row in rows.iterrows()
        )
        chunks.append({"text": f"CSV file: {filename}\nColumns: {columns}\n{row_text}"[:MAX_CHUNK_CHARACTERS],
                       "row_start": start, "row_end": end - 1})
    return chunks or [{"text": f"CSV file: {filename}\nColumns: {columns}\nThe file contains no rows.",
                       "row_start": 0, "row_end": 0}]


def embed(texts: list[str], task_type: str) -> list[list[float]]:
    result = genai.embed_content(model=EMBEDDING_MODEL, content=texts, task_type=task_type)
    vectors = result["embedding"]
    return vectors if isinstance(vectors[0], list) else [vectors]


def index_chunks(document_id: str, filename: str, chunks: list[dict]) -> None:
    collection.add(
        ids=[f"{document_id}:{number}" for number in range(len(chunks))],
        documents=[chunk["text"] for chunk in chunks],
        embeddings=embed([chunk["text"] for chunk in chunks], "retrieval_document"),
        metadatas=[{"document_id": document_id, "filename": filename, "row_start": chunk["row_start"],
                    "row_end": chunk["row_end"]} for chunk in chunks],
    )


def retrieve(document_id: str, question: str, top_k: int) -> list[dict]:
    results = collection.query(
        query_embeddings=[embed([question], "retrieval_query")[0]],
        n_results=top_k, where={"document_id": document_id},
        include=["documents", "metadatas", "distances"],
    )
    return [{"text": text, "metadata": metadata, "distance": distance}
            for text, metadata, distance in zip(results["documents"][0], results["metadatas"][0],
                                                results["distances"][0])]


def answer_with_context(question: str, matches: list[dict]) -> str:
    context = "\n\n".join(
        f"[Source {i + 1}, rows {match['metadata']['row_start']}-{match['metadata']['row_end']}]\n{match['text']}"
        for i, match in enumerate(matches)
    )
    prompt = f"""You are a business-data assistant. Answer only from the retrieved CSV context.
If the context does not support the answer, say that you do not have enough information.
When useful, cite source row ranges like [rows 0-24]. Do not invent numbers.

Retrieved CSV context:
{context}

Question: {question}"""
    return (getattr(model.generate_content(prompt), "text", "") or "The model returned no answer.").strip()


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files or not request.files["file"].filename:
        return jsonify({"error": "Upload a CSV file in the 'file' field."}), 400
    file = request.files["file"]
    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only CSV files are supported."}), 400
    filename, document_id = secure_filename(file.filename), str(uuid.uuid4())
    file_path = UPLOAD_FOLDER / f"{document_id}_{filename}"
    file.save(file_path)
    try:
        df = pd.read_csv(file_path)
        chunks = build_chunks(df, filename)
        index_chunks(document_id, filename, chunks)
    except Exception as exc:
        file_path.unlink(missing_ok=True)
        logging.exception("Could not index uploaded CSV")
        return jsonify({"error": f"Could not process CSV: {exc}"}), 400
    return jsonify({"message": "File uploaded and indexed for RAG.", "document_id": document_id,
                    "description": dataset_description(df), "chunks_indexed": len(chunks)})


@app.route("/query", methods=["POST"])
def query():
    data = request.get_json(silent=True) or {}
    document_id, question = data.get("document_id", "").strip(), data.get("question", "").strip()
    try:
        top_k = max(1, min(int(data.get("top_k", 4)), 10))
    except (TypeError, ValueError):
        return jsonify({"error": "top_k must be a number."}), 400
    if not document_id or not question:
        return jsonify({"error": "document_id and question are required."}), 400
    try:
        matches = retrieve(document_id, question, top_k)
        if not matches:
            return jsonify({"error": "No indexed chunks found for this document."}), 404
        return jsonify({"answer": answer_with_context(question, matches), "sources": [
            {"filename": item["metadata"]["filename"], "row_start": item["metadata"]["row_start"],
             "row_end": item["metadata"]["row_end"], "distance": item["distance"]} for item in matches]})
    except Exception as exc:
        logging.exception("RAG query failed")
        return jsonify({"error": f"RAG query failed: {exc}"}), 500


@app.route("/summarize", methods=["POST"])
def summarize():
    document_id = (request.get_json(silent=True) or {}).get("document_id", "").strip()
    if not document_id:
        return jsonify({"error": "document_id is required."}), 400
    try:
        matches = retrieve(document_id, "Give an overview of the dataset's main fields, patterns, and values.", 8)
        if not matches:
            return jsonify({"error": "No indexed chunks found for this document."}), 404
        return jsonify({"summary": answer_with_context(
            "Summarize this dataset concisely, including important patterns and caveats.", matches)})
    except Exception as exc:
        logging.exception("Summary failed")
        return jsonify({"error": f"Summary failed: {exc}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
