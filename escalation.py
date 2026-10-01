"""Human escalation tool and pending ticket storage."""

from pathlib import Path
from datetime import datetime, timezone

import csv
import uuid

from crewai.tools import tool


# ---------------------------------------------------------
# PATH
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

# Tickets are stored beside the application.
TICKETS_PATH = BASE_DIR / "pending_tickets.csv"

FIELDS = [
    "ticket_id",
    "created_at_utc",
    "customer_name",
    "contact_email",
    "summary",
    "status",
]


# ---------------------------------------------------------
# CREATE TICKET
# ---------------------------------------------------------

def _append_ticket(
    customer_name: str,
    contact_email: str,
    summary: str,
) -> dict:
    """Create and save a pending support ticket."""

    ticket = {
        "ticket_id": (
            "TKT-"
            + uuid.uuid4().hex[:8].upper()
        ),

        "created_at_utc": (
            datetime.now(timezone.utc)
            .strftime("%Y-%m-%d %H:%M:%S UTC")
        ),

        "customer_name": (
            (customer_name or "Not provided")
            .strip()[:120]
        ),

        "contact_email": (
            (contact_email or "Not provided")
            .strip()[:160]
        ),

        "summary": (
            (summary or "Customer requested human support.")
            .strip()[:1500]
        ),

        "status": "Pending",
    }

    file_exists = TICKETS_PATH.exists()

    with TICKETS_PATH.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS,
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(ticket)

    return ticket


# ---------------------------------------------------------
# CREWAI TOOL
# ---------------------------------------------------------

@tool("Escalate issue to human support")
def escalate_to_human(
    customer_name: str,
    contact_email: str,
    summary: str,
) -> str:
    """
    Create a pending human-support ticket.

    Use this when the customer requests human support or
    the issue cannot be confidently resolved.
    """

    try:
        ticket = _append_ticket(
            customer_name=customer_name,
            contact_email=contact_email,
            summary=summary,
        )

        return (
            "Escalation created successfully.\n"
            f"Ticket ID: {ticket['ticket_id']}\n"
            "Status: Pending\n"
            "Tell the customer that their request "
            "has been escalated to human support."
        )

    except Exception as exc:

        return (
            "The escalation ticket could not be saved automatically. "
            "Tell the customer that the request could not be recorded "
            "by this demo and that they should contact the support team "
            "through the official support channel. "
            f"Technical error: {type(exc).__name__}: {exc}"
        )


# ---------------------------------------------------------
# READ PENDING TICKETS
# ---------------------------------------------------------

def read_pending_tickets():
    """
    Return all saved pending tickets.

    This can be used by Streamlit to display the support queue.
    """

    if not TICKETS_PATH.exists():
        return []

    try:
        with TICKETS_PATH.open(
            "r",
            newline="",
            encoding="utf-8",
        ) as file:

            return list(
                csv.DictReader(file)
            )

    except Exception:
        return []
