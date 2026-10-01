"""Customer Support AI - Streamlit frontend."""

import html
import logging

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
# LOGGING
# =========================================================

logger = logging.getLogger(__name__)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    .stApp {
        background: #f7f8fc;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.25rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {
        width: 330px !important;
        min-width: 330px !important;
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    section[data-testid="stSidebar"] > div {
        width: 330px !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding: 1.5rem 1.15rem;
    }

    /* Sidebar text inputs */

    section[data-testid="stSidebar"] input {
        color: #111827 !important;
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 9px !important;
        min-height: 42px !important;
    }

    section[data-testid="stSidebar"] input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 1px #6366f1 !important;
    }

    section[data-testid="stSidebar"] input::placeholder {
        color: #9ca3af !important;
        opacity: 1 !important;
    }

    section[data-testid="stSidebar"] label {
        color: #374151 !important;
        font-weight: 500 !important;
    }


    /* =====================================================
       HEADER
       ===================================================== */

    .app-header {
        background: linear-gradient(
            135deg,
            #111827,
            #1f2937
        );

        border-radius: 18px;
        padding: 28px 32px;
        margin-bottom: 28px;

        box-shadow:
            0 10px 30px rgba(15, 23, 42, 0.10);
    }

    .app-header-title {
        color: #ffffff;
        font-size: 32px;
        font-weight: 750;
        line-height: 1.2;
        margin: 0;
    }

    .app-header-subtitle {
        color: #d1d5db;
        font-size: 15px;
        line-height: 1.6;
        margin-top: 10px;
        margin-bottom: 0;
    }


    /* =====================================================
       SECTION HEADINGS
       ===================================================== */

    .section-title {
        color: #111827;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 14px;
    }


    /* =====================================================
       WELCOME CARD
       ===================================================== */

    .welcome-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 18px;

        box-shadow:
            0 4px 16px rgba(15, 23, 42, 0.04);
    }

    .welcome-title {
        color: #111827;
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 7px;
    }

    .welcome-text {
        color: #6b7280;
        font-size: 14px;
        line-height: 1.6;
        margin: 0;
    }


    /* =====================================================
       FEATURE CARDS
       ===================================================== */

    .feature-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 14px;

        padding: 18px;

        min-height: 145px;
        box-sizing: border-box;

        box-shadow:
            0 3px 12px rgba(15, 23, 42, 0.035);
    }

    .feature-icon {
        font-size: 25px;
        line-height: 1;
        margin-bottom: 12px;
    }

    .feature-title {
        color: #111827;
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 7px;
    }

    .feature-description {
        color: #6b7280;
        font-size: 12.5px;
        line-height: 1.55;
    }


    /* =====================================================
       CHAT AREA
       ===================================================== */

    [data-testid="stChatMessage"] {
        border-radius: 14px;
    }

    [data-testid="stChatInput"] {
        margin-top: 18px;
    }


    /* =====================================================
       HUMAN SUPPORT
       ===================================================== */

    .ticket-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 13px;
        padding: 15px;
        margin-bottom: 12px;

        box-shadow:
            0 3px 12px rgba(15, 23, 42, 0.035);
    }

    .ticket-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
    }

    .ticket-id {
        color: #111827;
        font-size: 13px;
        font-weight: 700;
    }

    .ticket-status {
        background: #fff7ed;
        color: #c2410c;
        padding: 3px 8px;
        border-radius: 999px;
        font-size: 10px;
        font-weight: 700;
        white-space: nowrap;
    }

    .ticket-date {
        color: #9ca3af;
        font-size: 10px;
        margin-top: 5px;
    }

    .ticket-summary {
        color: #4b5563;
        font-size: 12px;
        line-height: 1.55;
        margin-top: 10px;
    }


    /* =====================================================
       METRIC
       ===================================================== */

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 13px;
        padding: 12px 15px;
        margin-bottom: 15px;
    }


    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button {
        border-radius: 9px;
        min-height: 40px;
        font-weight: 600;
    }

    .stDownloadButton > button {
        border-radius: 9px;
        font-weight: 600;
    }


    /* =====================================================
       DIVIDERS
       ===================================================== */

    hr {
        border-color: #e5e7eb !important;
    }


    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {
        text-align: center;
        color: #9ca3af;
        font-size: 11px;
        line-height: 1.6;
        padding-top: 10px;
    }


    /* =====================================================
       RESPONSIVE
       ===================================================== */

    @media (max-width: 1100px) {

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .app-header {
            padding: 23px;
        }

        .app-header-title {
            font-size: 27px;
        }

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
    <div class="app-header">
        <div class="app-header-title">
            💬 Customer Support AI
        </div>

        <div class="app-header-subtitle">
            Get help with company information, products,
            orders, and support requests.
        </div>
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
        "To check an order, provide both your "
        "**Order ID** and the **phone number used "
        "for that order**."
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
# MAIN LAYOUT
# =========================================================

chat_col, support_col = st.columns(
    [2.35, 1],
    gap="large",
)


# =========================================================
# CHAT COLUMN
# =========================================================

with chat_col:

    st.markdown(
        '<div class="section-title">💬 Support Chat</div>',
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # WELCOME
    # -----------------------------------------------------

    if not st.session_state.messages:

        st.markdown(
            """
            <div class="welcome-card">

                <div class="welcome-title">
                    👋 Welcome!
                </div>

                <p class="welcome-text">
                    I'm your customer support assistant.
                    Ask me about company policies,
                    products, orders, or any support issue.
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

        # Three feature columns
        feature_1, feature_2, feature_3 = st.columns(
            3,
            gap="medium",
        )

        with feature_1:

            st.markdown(
                """
                <div class="feature-card">

                    <div class="feature-icon">
                        📚
                    </div>

                    <div class="feature-title">
                        Company Knowledge
                    </div>

                    <div class="feature-description">
                        Get answers from the company's
                        knowledge base.
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        with feature_2:

            st.markdown(
                """
                <div class="feature-card">

                    <div class="feature-icon">
                        📦
                    </div>

                    <div class="feature-title">
                        Order Tracking
                    </div>

                    <div class="feature-description">
                        Check your order status after
                        secure verification.
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        with feature_3:

            st.markdown(
                """
                <div class="feature-card">

                    <div class="feature-icon">
                        👨‍💼
                    </div>

                    <div class="feature-title">
                        Human Support
                    </div>

                    <div class="feature-description">
                        Issues that need human attention
                        can be escalated.
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")


    # -----------------------------------------------------
    # CHAT HISTORY
    # -----------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )


    # -----------------------------------------------------
    # CHAT INPUT
    # -----------------------------------------------------

    prompt = st.chat_input(
        "Type your message..."
    )

    if prompt:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            with st.spinner(
                "Thinking..."
            ):

                try:

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

                except Exception as exc:

                    # Log real error without showing technical
                    # details to the customer.
                    logger.exception(
                        "Customer support agent failed."
                    )

                    response = (
                        "I'm sorry, something went wrong "
                        "while processing your request. "
                        "Please try again."
                    )

            st.markdown(response)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response,
            }
        )

        st.rerun()


# =========================================================
# HUMAN SUPPORT COLUMN
# =========================================================

with support_col:

    st.markdown(
        '<div class="section-title">🧾 Human Support</div>',
        unsafe_allow_html=True,
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

    st.metric(
        "Pending requests",
        len(pending_tickets),
    )


    # -----------------------------------------------------
    # TICKETS
    # -----------------------------------------------------

    if pending_tickets:

        st.markdown("#### Open Requests")

        for ticket in reversed(
            pending_tickets
        ):

            ticket_id = html.escape(
                str(
                    ticket.get(
                        "ticket_id",
                        "Ticket",
                    )
                )
            )

            status = html.escape(
                str(
                    ticket.get(
                        "status",
                        "Pending",
                    )
                )
            )

            created = html.escape(
                str(
                    ticket.get(
                        "created_at_utc",
                        "",
                    )
                )
            )

            summary = html.escape(
                str(
                    ticket.get(
                        "summary",
                        "No summary available.",
                    )
                )
            )

            st.markdown(
                f"""
                <div class="ticket-card">

                    <div class="ticket-top">

                        <div class="ticket-id">
                            {ticket_id}
                        </div>

                        <div class="ticket-status">
                            {status}
                        </div>

                    </div>

                    <div class="ticket-date">
                        {created}
                    </div>

                    <div class="ticket-summary">
                        {summary}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


        csv_data = (
            pd.DataFrame(
                tickets
            )
            .to_csv(index=False)
            .encode("utf-8")
        )

        st.download_button(
            "⬇️ Download Ticket Queue",
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
        Secure order verification · Company knowledge ·
        Human escalation
    </div>
    """,
    unsafe_allow_html=True,
)
