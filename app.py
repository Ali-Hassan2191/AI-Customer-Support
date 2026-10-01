"""Streamlit front end for the CrewAI customer support agent - DEBUG MODE."""

import traceback
import pandas as pd
import streamlit as st

from agent import answer_customer
from escalation import read_pending_tickets


st.set_page_config(
    page_title="Customer Support AI",
    page_icon="💬",
    layout="wide",
)

st.title("💬 Customer Support AI")
st.caption(
    "DEBUG MODE • CrewAI single-agent • "
    "Company knowledge • Order lookup • Human escalation"
)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.header("Customer details (optional)")

    customer_name = st.text_input(
        "Your name",
        key="customer_name",
    )

    contact_email = st.text_input(
        "Email for follow-up",
        key="contact_email",
    )

    st.info(
        "For order status, the agent will ask for "
        "your order ID and the phone number used for that order."
    )

    if st.button(
        "Clear chat",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.rerun()


# ---------------------------------------------------------
# COLUMNS
# ---------------------------------------------------------

chat_col, ticket_col = st.columns(
    [2, 1],
    gap="large",
)


# =========================================================
# CHAT
# =========================================================

with chat_col:

    st.subheader("Chat")

    # Display chat history
    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


    prompt = st.chat_input(
        "Ask about company policies or your order..."
    )


    if prompt:

        # Save user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)


        # -------------------------------------------------
        # ASSISTANT
        # -------------------------------------------------

        with st.chat_message("assistant"):

            try:

                st.info(
                    "🔎 Calling CrewAI agent..."
                )

                # Previous messages.
                # Current prompt is passed separately.
                previous = (
                    st.session_state.messages[:-1]
                )


                # -----------------------------------------
                # CALL AGENT
                # -----------------------------------------

                response = answer_customer(
                    prompt,
                    previous,
                    customer_name=customer_name,
                    contact_email=contact_email,
                )


                # -----------------------------------------
                # VALIDATE RESPONSE
                # -----------------------------------------

                if response is None:

                    raise RuntimeError(
                        "answer_customer() returned None."
                    )

                response = str(response).strip()


                if not response:

                    raise RuntimeError(
                        "answer_customer() returned an empty string."
                    )


                st.success(
                    "✅ Agent completed successfully."
                )

                st.markdown(response)


                # Save assistant response
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )


            except Exception as exc:

                # =========================================
                # REAL ERROR
                # =========================================

                st.error(
                    "🚨 AGENT ERROR"
                )


                # Error type
                st.markdown(
                    "### Exception Type"
                )

                st.code(
                    type(exc).__name__,
                    language="text",
                )


                # Error message
                st.markdown(
                    "### Exception Message"
                )

                st.code(
                    str(exc),
                    language="text",
                )


                # Full traceback
                st.markdown(
                    "### Full Traceback"
                )

                error_trace = traceback.format_exc()

                st.code(
                    error_trace,
                    language="text",
                )


                # Also print to Streamlit Cloud logs
                print("\n")
                print("=" * 100)
                print("CUSTOMER SUPPORT AGENT ERROR")
                print("=" * 100)
                print(error_trace)
                print("=" * 100)
                print("\n")


                # Save error response
                response = (
                    "❌ Agent failed. "
                    "Please see the technical error above."
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )


# =========================================================
# HUMAN SUPPORT QUEUE
# =========================================================

with ticket_col:

    st.subheader(
        "🧾 Human support queue"
    )


    try:

        tickets = read_pending_tickets()

    except Exception as exc:

        st.error(
            "🚨 Ticket queue error"
        )

        st.code(
            traceback.format_exc(),
            language="text",
        )

        tickets = []


    pending = [
        ticket
        for ticket in tickets
        if ticket.get(
            "status",
            ""
        ).lower()
        == "pending"
    ]


    st.metric(
        "Pending requests",
        len(pending),
    )


    if pending:

        for ticket in reversed(pending):

            with st.container(
                border=True
            ):

                st.markdown(
                    f"**{ticket.get('ticket_id', 'Ticket')}** "
                    f"· "
                    f"{ticket.get('status', 'Pending')}"
                )

                st.caption(
                    ticket.get(
                        "created_at_utc",
                        "",
                    )
                )

                st.write(
                    ticket.get(
                        "summary",
                        "",
                    )
                )

                name = ticket.get(
                    "customer_name",
                    "",
                )

                email = ticket.get(
                    "contact_email",
                    "",
                )


                if (
                    name
                    and name != "Not provided"
                ):

                    st.caption(
                        f"Customer: {name}"
                    )


                if (
                    email
                    and email != "Not provided"
                ):

                    st.caption(
                        f"Follow-up email: {email}"
                    )


        csv_bytes = (
            pd.DataFrame(tickets)
            .to_csv(index=False)
            .encode("utf-8")
        )


        st.download_button(
            "Download ticket queue (CSV)",
            data=csv_bytes,
            file_name="pending_tickets.csv",
            mime="text/csv",
            use_container_width=True,
        )


    else:

        st.info(
            "No pending human-support requests yet."
        )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "⚠️ DEBUG MODE: Detailed technical errors are visible. "
    "Remove debug traceback output before production."
)
