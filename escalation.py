"""Human escalation tool and ticket storage."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import uuid
from crewai.tools import tool

BASE_DIR = Path(__file__).resolve().parent
TICKETS_PATH = BASE_DIR / "pending_tickets.csv"
FIELDS = ["ticket_id", "created_at_utc", "customer_name", "contact_email", "summary", "status"]


def _append_ticket(customer_name: str, contact_email: str, summary: str) -> dict:
    ticket = {
        "ticket_id": "TKT-" + uuid.uuid4().hex[:8].upper(),
        "created_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "customer_name": (customer_name or "Not provided").strip()[:120],
        "contact_email": (contact_email or "Not provided").strip()[:160],
        "summary": (summary or "Customer requested human support.").strip()[:1500],
        "status": "Pending",
    }
    file_exists = TICKETS_PATH.exists()
    with TICKETS_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(ticket)
    return ticket


@tool("Escalate issue to human support")
def escalate_to_human(customer_name: str, contact_email: str, summary: str) -> str:
    """Create a pending human-support ticket when the customer requests a human or
    the agent cannot confidently resolve the issue. Provide a short factual summary.
    Do not include passwords, payment card details, or other secrets.
    """
    try:
        ticket = _append_ticket(customer_name, contact_email, summary)
        return (
            f"Escalation created successfully. Ticket ID: {ticket['ticket_id']}. "
            "Status: Pending. Tell the customer their request has been escalated to human support."
        )
    except Exception as exc:
        return (
            "The escalation ticket could not be saved automatically. Tell the customer this "
            "demo could not record the ticket and ask them to contact the support team through "
            f"the official channel. Technical detail: {type(exc).__name__}: {exc}"
        )


def read_pending_tickets():
    """Return pending tickets for display in the Streamlit sidebar/queue."""
    if not TICKETS_PATH.exists():
        return []
    with TICKETS_PATH.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
