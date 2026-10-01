"""Streamlit front end for the CrewAI customer support agent."""
import io
import pandas as pd
import streamlit as st
from agent import answer_customer
from escalation import read_pending_tickets, TICKETS_PATH

st.set_page_config(page_title="Customer Support AI", page_icon="💬", layout="wide")
st.title("💬 Customer Support AI")
st.caption("CrewAI single-agent demo • Company knowledge search • Verified order lookup • Human escalation")

with st.sidebar:
    st.header("Customer details (optional)")
    customer_name = st.text_input("Your name", key="customer_name")
    contact_email = st.text_input("Email for follow-up", key="contact_email")
    st.info("For order status, the agent will ask for your order ID and the phone number used for that order.")
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

chat_col, ticket_col = st.columns([2, 1], gap="large")

with chat_col:
    st.subheader("Chat")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask about company policies or your order...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Checking company information..."):
                try:
                    # Pass previous turns (excluding the new user message, which is passed separately).
                    previous = st.session_state.messages[:-1]
                    response = answer_customer(
                        prompt,
                        previous,
                        customer_name=customer_name,
                        contact_email=contact_email,
                    )
                except Exception as exc:
    st.exception(exc)
    response = (
        "Sorry, I couldn't process your request right now. "
        "The technical team has been notified."
    )
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

with ticket_col:
    st.subheader("🧾 Human support queue")
    tickets = read_pending_tickets()
    pending = [t for t in tickets if t.get("status", "").lower() == "pending"]
    st.metric("Pending requests", len(pending))
    if pending:
        for ticket in reversed(pending):
            with st.container(border=True):
                st.markdown(f"**{ticket.get('ticket_id', 'Ticket')}** · {ticket.get('status', 'Pending')}")
                st.caption(ticket.get("created_at_utc", ""))
                st.write(ticket.get("summary", ""))
                name = ticket.get("customer_name", "")
                email = ticket.get("contact_email", "")
                if name and name != "Not provided":
                    st.caption(f"Customer: {name}")
                if email and email != "Not provided":
                    st.caption(f"Follow-up email: {email}")
        csv_bytes = pd.DataFrame(tickets).to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download ticket queue (CSV)",
            data=csv_bytes,
            file_name="pending_tickets.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.info("No pending human-support requests yet.")

st.divider()
st.caption(
    "Demo note: Streamlit Cloud's local filesystem is not durable storage. The ticket queue is "
    "visible while this app instance retains its files, but may reset on restart/redeploy. "
    "Use a persistent database for production."
)
