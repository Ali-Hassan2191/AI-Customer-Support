"""Tools for the single-agent customer support assistant."""
from pathlib import Path
import json
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
from crewai.tools import tool

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

INDEX_PATH = DATA_DIR / "faiss.index"
CHUNKS_PATH = DATA_DIR / "chunks.json"
ORDERS_PATH = DATA_DIR / "orders.xlsx"

_EMBEDDER = None
_INDEX = None
_CHUNKS = None
_ORDERS = None


def _load_chunks():
    global _CHUNKS
    if _CHUNKS is None:
        if not CHUNKS_PATH.exists():
            raise FileNotFoundError("chunks.json is missing. Add it to the GitHub repository root.")
        with CHUNKS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            _CHUNKS = data
        elif isinstance(data, dict):
            # Supports common formats: {"chunks": [...]} or {"data": [...]}.
            candidate = data.get("chunks", data.get("data", []))
            if isinstance(candidate, list):
                _CHUNKS = candidate
            else:
                raise ValueError("chunks.json must contain a list of chunks.")
        else:
            raise ValueError("Unsupported chunks.json format.")
    return _CHUNKS


def _get_chunk_text(item):
    if isinstance(item, str):
        return item
    for key in ("text", "chunk_text", "content", "page_content", "document"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def _get_embedder():
    global _EMBEDDER
    if _EMBEDDER is None:
        _EMBEDDER = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _EMBEDDER


def _get_index():
    global _INDEX
    if _INDEX is None:
        if not INDEX_PATH.exists():
            raise FileNotFoundError("faiss.index is missing. Add it to the GitHub repository root.")
        _INDEX = faiss.read_index(str(INDEX_PATH))
    return _INDEX


@tool("Search company knowledge base")
def search_company_knowledge(query: str) -> str:
    """Search the prebuilt FAISS index for company policy, product, and support information.
    Use this for general questions. Return relevant passages with source metadata.
    """
    try:
        index = _get_index()
        chunks = _load_chunks()
        embedder = _get_embedder()
        vector = embedder.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        if vector.shape[1] != index.d:
            return (
                f"Embedding dimension mismatch: query embedding is {vector.shape[1]} "
                f"but FAISS index expects {index.d}. Confirm the index was built with "
                "all-MiniLM-L6-v2 (384 dimensions)."
            )
        k = min(5, index.ntotal)
        if k < 1:
            return "The company knowledge base is empty."
        distances, indices = index.search(vector.astype("float32"), k)
        results = []
        for rank, idx in enumerate(indices[0], start=1):
            if idx < 0 or idx >= len(chunks):
                continue
            item = chunks[int(idx)]
            body = _get_chunk_text(item)
            if not body:
                continue
            meta = item.get("metadata", {}) if isinstance(item, dict) else {}
            if not isinstance(meta, dict):
                meta = {}
            # Some pipelines store metadata fields directly on the chunk.
            source = meta.get("source_filename", meta.get("source", item.get("source_filename", "Unknown source") if isinstance(item, dict) else "Unknown source"))
            page = meta.get("page_number", meta.get("page", item.get("page_number", "N/A") if isinstance(item, dict) else "N/A"))
            chunk_id = meta.get("chunk_id", item.get("chunk_id", idx) if isinstance(item, dict) else idx)
            results.append(
                f"[Result {rank} | Source: {source} | Page: {page} | Chunk: {chunk_id}]\n{body}"
            )
        return "\n\n".join(results) if results else "No relevant company information was found."
    except Exception as exc:
        return f"Knowledge search could not be completed: {type(exc).__name__}: {exc}"


def _load_orders():
    global _ORDERS
    if _ORDERS is None:
        if not ORDERS_PATH.exists():
            raise FileNotFoundError("orders.xlsx is missing. Add the supplied Excel file to the GitHub repository root.")
        _ORDERS = pd.read_excel(ORDERS_PATH, dtype={"Order ID": str, "Contact Number": str})
        _ORDERS.columns = [str(c).strip() for c in _ORDERS.columns]
        required = {"Order ID", "Customer Name", "Contact Number", "Product", "Order Date", "Shipping Address", "Status"}
        missing = required - set(_ORDERS.columns)
        if missing:
            raise ValueError("orders.xlsx is missing columns: " + ", ".join(sorted(missing)))
        _ORDERS["Order ID"] = _ORDERS["Order ID"].astype(str).str.strip().str.upper()
        _ORDERS["Contact Number"] = _ORDERS["Contact Number"].astype(str).str.strip()
    return _ORDERS


@tool("Look up a customer order")
def lookup_order(order_id: str, contact_number: str) -> str:
    """Look up an order only after the customer provides both the order ID and the
    phone number recorded for that order. Never reveal another customer's order.
    """
    try:
        orders = _load_orders()
        order_id = str(order_id).strip().upper()
        contact_number = str(contact_number).strip().replace(" ", "")
        rows = orders[orders["Order ID"] == order_id]
        if rows.empty:
            return "I couldn't find an order with that order ID. Please check it and try again."
        # Match phone number exactly after removing spaces; do not disclose the stored number.
        matched = rows[rows["Contact Number"].str.replace(" ", "", regex=False) == contact_number]
        if matched.empty:
            return "The order ID and contact number do not match our records. Please verify both details."
        row = matched.iloc[0]
        order_date = row["Order Date"]
        if pd.notna(order_date):
            try:
                order_date = pd.to_datetime(order_date).strftime("%d-%m-%Y")
            except Exception:
                order_date = str(order_date)
        # Deliberately omit full contact number and shipping address from the result.
        return (
            f"Verified order found.\n"
            f"Order ID: {row['Order ID']}\n"
            f"Customer: {row['Customer Name']}\n"
            f"Product: {row['Product']}\n"
            f"Order date: {order_date}\n"
            f"Current status: {row['Status']}\n"
            "Explain the status in plain language. If the customer asks for an address change, "
            "cancellation, refund, or other action not supported by this read-only demo, escalate it."
        )
    except Exception as exc:
        return f"Order lookup could not be completed: {type(exc).__name__}: {exc}"
