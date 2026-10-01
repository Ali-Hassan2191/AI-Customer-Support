"""Tools for the single-agent customer-support assistant."""

from pathlib import Path
import json

import pandas as pd
import faiss

from sentence_transformers import SentenceTransformer
from crewai.tools import tool


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

INDEX_PATH = DATA_DIR / "faiss.index"
CHUNKS_PATH = DATA_DIR / "chunks.json"
ORDERS_PATH = DATA_DIR / "orders.xlsx"


# ---------------------------------------------------------
# CACHE
# ---------------------------------------------------------

_EMBEDDER = None
_INDEX = None
_CHUNKS = None
_ORDERS = None


# ---------------------------------------------------------
# KNOWLEDGE BASE
# ---------------------------------------------------------

def _load_chunks():
    """Load chunks.json once and cache it."""

    global _CHUNKS

    if _CHUNKS is not None:
        return _CHUNKS

    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            f"Knowledge-base file not found: {CHUNKS_PATH}"
        )

    with CHUNKS_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if isinstance(data, list):
        chunks = data

    elif isinstance(data, dict):
        chunks = data.get("chunks")

        if chunks is None:
            chunks = data.get("data")

        if not isinstance(chunks, list):
            raise ValueError(
                "chunks.json must contain a list under "
                "'chunks' or 'data'."
            )

    else:
        raise ValueError(
            "Unsupported chunks.json format."
        )

    _CHUNKS = chunks

    return _CHUNKS


def _get_chunk_text(item):
    """Extract text from different possible chunk formats."""

    if isinstance(item, str):
        return item

    if not isinstance(item, dict):
        return ""

    possible_keys = (
        "text",
        "chunk_text",
        "content",
        "page_content",
        "document",
    )

    for key in possible_keys:
        value = item.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return ""


def _get_embedder():
    """Load the same embedding model used to create the FAISS index."""

    global _EMBEDDER

    if _EMBEDDER is None:
        _EMBEDDER = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

    return _EMBEDDER


def _get_index():
    """Load the FAISS index once and cache it."""

    global _INDEX

    if _INDEX is not None:
        return _INDEX

    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            f"FAISS index not found: {INDEX_PATH}"
        )

    _INDEX = faiss.read_index(
        str(INDEX_PATH)
    )

    return _INDEX


@tool("Search company knowledge base")
def search_company_knowledge(query: str) -> str:
    """
    Search the prebuilt FAISS knowledge base.

    Use this tool for company policies, product information,
    support information, delivery information, returns,
    refunds, warranty information, and similar questions.
    """

    try:
        if not query or not query.strip():
            return "Please provide a question to search."

        index = _get_index()
        chunks = _load_chunks()
        embedder = _get_embedder()

        vector = embedder.encode(
            [query.strip()],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        # Make sure query embedding matches FAISS dimension.
        query_dimension = vector.shape[1]

        if query_dimension != index.d:
            return (
                "Knowledge-base configuration error: "
                f"query embedding dimension is {query_dimension}, "
                f"but the FAISS index dimension is {index.d}. "
                "The index should be compatible with "
                "all-MiniLM-L6-v2 (384 dimensions)."
            )

        if index.ntotal == 0:
            return (
                "The company knowledge base is currently empty."
            )

        # Return up to five results.
        k = min(5, index.ntotal)

        distances, indices = index.search(
            vector.astype("float32"),
            k,
        )

        results = []

        for rank, idx in enumerate(
            indices[0],
            start=1,
        ):
            idx = int(idx)

            if idx < 0 or idx >= len(chunks):
                continue

            item = chunks[idx]

            body = _get_chunk_text(item)

            if not body:
                continue

            metadata = {}

            if isinstance(item, dict):
                metadata = item.get(
                    "metadata",
                    {},
                )

            if not isinstance(metadata, dict):
                metadata = {}

            # Support both nested metadata and direct metadata fields.
            if isinstance(item, dict):
                source = metadata.get(
                    "source_filename",
                    metadata.get(
                        "source",
                        item.get(
                            "source_filename",
                            "Unknown source",
                        ),
                    ),
                )

                page = metadata.get(
                    "page_number",
                    metadata.get(
                        "page",
                        item.get(
                            "page_number",
                            "N/A",
                        ),
                    ),
                )

                chunk_id = metadata.get(
                    "chunk_id",
                    item.get(
                        "chunk_id",
                        idx,
                    ),
                )

            else:
                source = "Unknown source"
                page = "N/A"
                chunk_id = idx

            results.append(
                f"[Result {rank} | "
                f"Source: {source} | "
                f"Page: {page} | "
                f"Chunk: {chunk_id}]\n"
                f"{body}"
            )

        if not results:
            return (
                "No relevant company information was found "
                "in the knowledge base."
            )

        return "\n\n".join(results)

    except Exception as exc:
        return (
            "Knowledge search could not be completed. "
            f"Error: {type(exc).__name__}: {exc}"
        )


# ---------------------------------------------------------
# ORDERS
# ---------------------------------------------------------

def _load_orders():
    """Load orders.xlsx once and cache it."""

    global _ORDERS

    if _ORDERS is not None:
        return _ORDERS

    if not ORDERS_PATH.exists():
        raise FileNotFoundError(
            f"Order database not found: {ORDERS_PATH}"
        )

    orders = pd.read_excel(
        ORDERS_PATH,
        dtype={
            "Order ID": str,
            "Contact Number": str,
        },
    )

    # Clean column names.
    orders.columns = [
        str(column).strip()
        for column in orders.columns
    ]

    required_columns = {
        "Order ID",
        "Customer Name",
        "Contact Number",
        "Product",
        "Order Date",
        "Shipping Address",
        "Status",
    }

    missing_columns = (
        required_columns - set(orders.columns)
    )

    if missing_columns:
        raise ValueError(
            "orders.xlsx is missing columns: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    # Normalize identifiers.
    orders["Order ID"] = (
        orders["Order ID"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    orders["Contact Number"] = (
        orders["Contact Number"]
        .astype(str)
        .str.strip()
    )

    _ORDERS = orders

    return _ORDERS


@tool("Look up a customer order")
def lookup_order(
    order_id: str,
    contact_number: str,
) -> str:
    """
    Verify and look up a customer order.

    Both Order ID and contact number are required.
    """

    try:
        orders = _load_orders()

        order_id = (
            str(order_id)
            .strip()
            .upper()
        )

        contact_number = (
            str(contact_number)
            .strip()
            .replace(" ", "")
            .replace("-", "")
        )

        if not order_id:
            return (
                "Order ID is required."
            )

        if not contact_number:
            return (
                "The contact number used for the order is required."
            )

        # Find order by Order ID.
        rows = orders[
            orders["Order ID"] == order_id
        ]

        if rows.empty:
            return (
                "I couldn't find an order with that "
                "order ID. Please check the Order ID."
            )

        # Normalize stored phone numbers only for comparison.
        stored_numbers = (
            rows["Contact Number"]
            .astype(str)
            .str.strip()
            .str.replace(
                " ",
                "",
                regex=False,
            )
            .str.replace(
                "-",
                "",
                regex=False,
            )
        )

        matched = rows[
            stored_numbers == contact_number
        ]

        if matched.empty:
            return (
                "The Order ID and contact number "
                "do not match our records. "
                "Please verify both details."
            )

        row = matched.iloc[0]

        # Format order date.
        order_date = row["Order Date"]

        if pd.notna(order_date):
            try:
                order_date = pd.to_datetime(
                    order_date
                ).strftime("%d-%m-%Y")
            except Exception:
                order_date = str(order_date)

        status = str(
            row["Status"]
        ).strip()

        customer = str(
            row["Customer Name"]
        ).strip()

        product = str(
            row["Product"]
        ).strip()

        return (
            "Verified order found.\n"
            f"Order ID: {row['Order ID']}\n"
            f"Customer: {customer}\n"
            f"Product: {product}\n"
            f"Order date: {order_date}\n"
            f"Current status: {status}\n\n"
            "Explain the order status in simple language. "
            "Do not expose the customer's full contact number "
            "or shipping address. "
            "If the customer requests an address change, "
            "cancellation, refund, or another unsupported "
            "action, escalate the request to human support."
        )

    except Exception as exc:
        return (
            "Order lookup could not be completed. "
            f"Error: {type(exc).__name__}: {exc}"
        )
