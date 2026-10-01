
"""Customer Support AI - Streamlit frontend."""

import pandas as pd
import streamlit as st

from agent import answer_customer
from escalation import read_pending_tickets


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Customer Support AI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* ---------- Global ---------- */

    .stApp {
        background: #f7f8fc;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* ---------- Header ---------- */

    .main-header {
        background: linear-gradient(
            135deg,
            #111827 0%,
            #1f2937 100%
        );
        padding: 28px 32px;
        border-radius: 18px;
        margin-bottom: 22px;
        color: white;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
    }

    .main-header h1 {
        margin: 0;
        font-size: 32px;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    .main-header p {
        margin: 8px 0 0 0;
        color: #d1d5db;
        font-size: 15px;
    }

    /* ---------- Welcome Card ---------- */

    .welcome-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 26px;
        margin-bottom: 20px;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.04);
    }

    .welcome-card h3 {
        margin-top: 0;
        color: #111827;
    }

    .welcome-card p {
        color: #6b7280;
        margin-bottom: 0;
    }

    /* ---------- Feature Cards ---------- */

    .feature-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 18px;
        min-height: 120px;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.03);
    }

    .feature-icon {
        font-size: 24px;
        margin-bottom: 8px;
    }

    .feature-title {
        font-weight: 650;
        color: #111827;
        margin-bottom: 5px;
    }

    .feature-text {
        color: #6b7280;
        font-size: 13px;
        line-height: 1.5;
    }

    /* ---------- Ticket Card ---------- */

    .ticket-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.03);
    }

    .ticket-id {
        font-weight: 700;
        color: #111827;
    }

    .ticket-status {
        display: inline-block;
        background: #fff7ed;
        color: #c2410c;
        padding: 3px 9px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 600;
    }

    /* ---------- Sidebar ---------- */

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    /* ---------- Chat ---------- */

    [data-testid="stChatMessage"] {
        border-radius: 14px;
    }

    /* ---------- Buttons ---------- */

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

    /* ---------- Footer ---------- */

    .footer {
        text-align: center;
        color: #9ca3af;
        font-size: 12px;
        padding-top: 18px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="main-header">
        <h1>💬 Customer Support AI</h1>
        <p>
            Get help with company information, products, orders,
            and support requests.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 👤 Customer Profile")

    st.caption(
        "Optional information helps our support team "
        "follow up when needed."
    )

    customer_name = st.text_input(
        "Your name",
        placeholder="e.g. Ali Hassan",
        key="customer_name",
    )

    contact_email = st.text_input(
        "Email address",
        placeholder="e.g. you@example.com",
        key="contact_email",
    )

    st.divider()

    st.markdown("### 📦 Order Support")

    st.info(
        "To check an order, please provide both your "
        "**Order ID** and the **phone number used for the order**."
    )

    st.divider()

    if st.button(
        "🗑️ Clear conversation",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.markdown("### 🔒 Privacy")

    st.caption(
        "Order information is only returned after "
        "the order ID and contact number are verified."
    )


# =========================================================
# MAIN COLUMNS
# =========================================================

chat_col, support_col = st.columns(
    [2.2, 1],
    gap="large",
)


# =========================================================
# CHAT AREA
# =========================================================

with chat_col:

    st.markdown("### 💬 Support Chat")

    # -----------------------------------------------------
    # Welcome screen
    # -----------------------------------------------------

    if not st.session_state.messages:

        st.markdown(
            """
            <div class="welcome-card">
                <h3>👋 Welcome!</h3>
                <p>
                    I'm your customer support assistant.
                    Ask me about company policies, products,
                    orders, or any support issue.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        feature_col1, feature_col2, feature_col3 = st.columns(3)

        with feature_col1:
            st.markdown(
                """
                <div class="feature-card">
                    <div class="feature-icon">📚</div>
                    <div class="feature-title">
                        Company Knowledge
                    </div>
                    <div class="feature-text">
                        Get answers from the company's
                        knowledge base.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with feature_col2:
            st.markdown(
                """
                <div class="feature-card">
                    <div class="feature-icon">📦</div>
                    <div class="feature-title">
                        Order Tracking
                    </div>
                    <div class="feature-text">
                        Check your order status after
                        secure verification.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with feature_col3:
            st.markdown(
                """
                <div class="feature-card">
                    <div class="feature-icon">👨‍💼</div>
                    <div class="feature-title">
                        Human Support
                    </div>
                    <div class="feature-text">
                        Issues that need human attention
                        can be escalated.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # -----------------------------------------------------
    # Existing messages
    # -----------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    # -----------------------------------------------------
    # Chat input
    # -----------------------------------------------------

    prompt = st.chat_input(
        "Type your message..."
    )

    if prompt:

        # Save user message.
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        # -------------------------------------------------
        # Agent response
        # -------------------------------------------------

        with st.chat_message("assistant"):

            with st.spinner(
                "Thinking..."
            ):

                try:

                    # Exclude current message because
                    # it is passed separately.
                    previous_history = (
                        st.session_state.messages[:-1]
                    )

                    response = answer_customer(
                        prompt,
                        previous_history,
                        customer_name=customer_name,
                        contact_email=contact_email,
                    )

                    response = str(
                        response
                    ).strip()

                    if not response:
                        response = (
                            "I'm sorry, I couldn't generate "
                            "a response. Please try again."
                        )

                except Exception:

                    response = (
                        "I'm sorry, something went wrong "
                        "while processing your request. "
                        "Please try again."
                    )

                    # Detailed error goes to Streamlit logs,
                    # not to the customer UI.
                    st.exception(
                        Exception(
                            "Customer support agent failed."
                        )
                    )

            st.markdown(response)

        # Save assistant response.
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response,
            }
        )

        st.rerun()


# =========================================================
# HUMAN SUPPORT PANEL
# =========================================================

with support_col:

    st.markdown(
        "### 🧾 Human Support"
    )

    try:

        tickets = read_pending_tickets()

    except Exception:

        tickets = []

    pending_tickets = [
        ticket
        for ticket in tickets
        if ticket.get(
            "status",
            "",
        ).lower()
        == "pending"
    ]

    # -----------------------------------------------------
    # Queue metric
    # -----------------------------------------------------

    st.metric(
        "Pending requests",
        len(pending_tickets),
    )

    if pending_tickets:

        st.markdown(
            "#### Open Requests"
        )

        for ticket in reversed(
            pending_tickets
        ):

            ticket_id = ticket.get(
                "ticket_id",
                "Ticket",
            )

            status = ticket.get(
                "status",
                "Pending",
            )

            created = ticket.get(
                "created_at_utc",
                "",
            )

            summary = ticket.get(
                "summary",
                "No summary available.",
            )

            st.markdown(
                f"""
                <div class="ticket-card">

                    <div>
                        <span class="ticket-id">
                            {ticket_id}
                        </span>
                        &nbsp;
                        <span class="ticket-status">
                            {status}
                        </span>
                    </div>

                    <div style="
                        color:#9ca3af;
                        font-size:11px;
                        margin-top:5px;
                    ">
                        {created}
                    </div>

                    <div style="
                        color:#4b5563;
                        font-size:13px;
                        margin-top:10px;
                        line-height:1.5;
                    ">
                        {summary}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        # -------------------------------------------------
        # Download queue
        # -------------------------------------------------

        csv_data = (
            pd.DataFrame(tickets)
            .to_csv(index=False)
            .encode("utf-8")
        )

        st.download_button(
            label="⬇️ Download Ticket Queue",
            data=csv_data,
            file_name="pending_tickets.csv",
            mime="text/csv",
            use_container_width=True,
        )

    else:

        st.success(
            "✓ No pending support requests"
        )

        st.caption(
            "Requests escalated to human support "
            "will appear here."
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <div class="footer">
        Customer Support AI · Powered by CrewAI & Gemini
        <br>
        Secure order verification · Company knowledge · Human escalation
    </div>
    """,
    unsafe_allow_html=True,
)
