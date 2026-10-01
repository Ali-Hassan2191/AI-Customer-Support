"""Streamlit frontend for the CrewAI customer support assistant."""

import pandas as pd
import streamlit as st

from agent import answer_customer
from escalation import read_pending_tickets


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Customer Support AI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.html(
    """
    <style>

    /* -------------------------------------------------------
       GLOBAL
    ------------------------------------------------------- */

    .stApp {
        background: #f5f7fb;
    }

    .main .block-container {
        max-width: 1500px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Prevent horizontal overflow */
    .stApp,
    .main,
    [data-testid="stAppViewContainer"] {
        overflow-x: hidden;
    }


    /* -------------------------------------------------------
       SIDEBAR
    ------------------------------------------------------- */

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    .sidebar-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
        color: #111827;
    }

    .sidebar-description {
        font-size: 0.82rem;
        color: #6b7280;
        line-height: 1.5;
        margin-bottom: 1.25rem;
    }


    /* -------------------------------------------------------
       HEADER
    ------------------------------------------------------- */

    .app-header {
        background: linear-gradient(135deg, #172033 0%, #26344d 100%);
        border-radius: 18px;
        padding: 1.35rem 1.5rem;
        margin-bottom: 1.5rem;
        color: white;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 8px 25px rgba(15, 23, 42, 0.10);
    }

    .app-header-title {
        font-size: 1.85rem;
        font-weight: 750;
        line-height: 1.2;
        margin: 0;
    }

    .app-header-subtitle {
        font-size: 0.92rem;
        color: #d1d5db;
        margin-top: 0.45rem;
        line-height: 1.5;
    }


    /* -------------------------------------------------------
       SECTION TITLES
    ------------------------------------------------------- */

    .section-title {
        font-size: 1.25rem;
        font-weight: 750;
        color: #111827;
        margin-bottom: 0.75rem;
    }


    /* -------------------------------------------------------
       WELCOME CARD
    ------------------------------------------------------- */

    .welcome-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.04);
    }

    .welcome-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.4rem;
    }

    .welcome-text {
        color: #4b5563;
        line-height: 1.6;
        margin: 0;
    }


    /* -------------------------------------------------------
       INFO CARD
    ------------------------------------------------------- */

    .info-card {
        background: #eff6ff;
        border: 1px solid #dbeafe;
        border-radius: 12px;
        padding: 0.9rem 1rem;
        color: #1e3a8a;
        font-size: 0.9rem;
        line-height: 1.55;
        margin-top: 0.75rem;
        margin-bottom: 1rem;
    }


    /* -------------------------------------------------------
       FEATURE CARDS
    ------------------------------------------------------- */

    .feature-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 1rem;
        min-height: 120px;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.035);
    }

    .feature-icon {
        font-size: 1.35rem;
        margin-bottom: 0.35rem;
    }

    .feature-title {
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.25rem;
    }

    .feature-text {
        color: #6b7280;
        font-size: 0.83rem;
        line-height: 1.45;
    }


    /* -------------------------------------------------------
       SUPPORT QUEUE
    ------------------------------------------------------- */

    .queue-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.04);
        margin-bottom: 0.8rem;
    }

    .queue-ticket {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 0.85rem;
        margin-top: 0.75rem;
        background: #fafafa;
    }

    .ticket-id {
        font-weight: 700;
        color: #111827;
    }

    .ticket-summary {
        color: #4b5563;
        font-size: 0.88rem;
        line-height: 1.5;
        margin-top: 0.45rem;
    }


    /* -------------------------------------------------------
       CHAT
    ------------------------------------------------------- */

    [data-testid="stChatMessage"] {
        border-radius: 14px;
        margin-bottom: 0.65rem;
    }

    [data-testid="stChatInput"] {
        margin-top: 0.75rem;
    }


    /* -------------------------------------------------------
       BUTTONS
    ------------------------------------------------------- */

    .stButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 600;
    }


    /* -------------------------------------------------------
       INPUTS
    ------------------------------------------------------- */

    [data-testid="stTextInput"] input {
        border-radius: 10px;
    }


    /* -------------------------------------------------------
       METRIC
    ------------------------------------------------------- */

    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 0.9rem 1rem;
    }


    /* -------------------------------------------------------
       FOOTER
    ------------------------------------------------------- */

    .footer-note {
        color: #9ca3af;
        font-size: 0.78rem;
        text-align: center;
        margin-top: 1.5rem;
        line-height: 1.5;
    }


    /* -------------------------------------------------------
       SMALL SCREENS
    ------------------------------------------------------- */

    @media (max-width: 900px) {

        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .app-header-title {
            font-size: 1.45rem;
        }

        .app-header {
            padding: 1.1rem;
        }

    }

    </style>
    """
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">👤 Customer Profile</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-description">'
        "Optional information helps our support team follow up when needed."
        "</div>",
        unsafe_allow_html=True,
    )

    customer_name = st.text_input(
        "Your name",
        key="customer_name",
        placeholder="Enter your name",
    )

    contact_email = st.text_input(
        "Email address",
        key="contact_email",
        placeholder="you@example.com",
    )

    st.divider()

    st.markdown(
        "### 📦 Order Support"
    )

    st.info(
        "To check an order, provide both your **Order ID** "
        "and the **phone number used for that order**."
    )

    st.divider()

    if st.button(
        "🗑️ Clear conversation",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.caption(
        "Customer Support AI\n\n"
        "Powered by CrewAI + Gemini"
    )


# ============================================================
# HEADER
# ============================================================

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


# ============================================================
# MAIN LAYOUT
# ============================================================

chat_col, support_col = st.columns(
    [2.4, 1],
    gap="large",
)


# ============================================================
# CHAT COLUMN
# ============================================================

with chat_col:

    st.markdown(
        '<div class="section-title">💬 Support Chat</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Welcome screen
    # --------------------------------------------------------

    if not st.session_state.messages:

        st.markdown(
            """
            <div class="welcome-card">

                <div class="welcome-title">
                    👋 Welcome!
                </div>

                <p class="welcome-text">
                    I'm your customer support assistant.
                    Ask me about company policies, products,
                    orders, delivery status, or any support issue.
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

        feature_cols = st.columns(
            3,
            gap="medium",
        )

        with feature_cols[0]:
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

        with feature_cols[1]:
            st.markdown(
                """
                <div class="feature-card">

                    <div class="feature-icon">📦</div>

                    <div class="feature-title">
                        Order Tracking
                    </div>

                    <div class="feature-text">
                        Check verified order status using
                        your Order ID and phone number.
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        with feature_cols[2]:
            st.markdown(
                """
                <div class="feature-card">

                    <div class="feature-icon">👨‍💼</div>

                    <div class="feature-title">
                        Human Support
                    </div>

                    <div class="feature-text">
                        Requests that need human help can
                        be escalated to support.
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    # --------------------------------------------------------
    # Existing chat messages
    # --------------------------------------------------------

    for message in st.session_state.messages:

        role = message.get("role", "assistant")
        content = message.get("content", "")

        with st.chat_message(
            role,
            avatar="👤" if role == "user" else "🤖",
        ):
            st.markdown(content)


    # --------------------------------------------------------
    # Chat input
    # --------------------------------------------------------

    prompt = st.chat_input(
        "Type your message here..."
    )


    # --------------------------------------------------------
    # Process new message
    # --------------------------------------------------------

    if prompt:

        # Save user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        # Display user message immediately
        with st.chat_message(
            "user",
            avatar="👤",
        ):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message(
            "assistant",
            avatar="🤖",
        ):

            with st.spinner(
                "Checking company information..."
            ):

                try:

                    # IMPORTANT:
                    # Do not include the current message in history.
                    previous_history = (
                        st.session_state.messages[:-1]
                    )

                    response = answer_customer(
                        prompt,
                        previous_history,
                        customer_name=customer_name,
                        contact_email=contact_email,
                    )

                except Exception as exc:

                    # Show full error during development
                    st.exception(exc)

                    response = (
                        "Sorry, I couldn't process your request "
                        "right now. Please try again."
                    )

                st.markdown(response)

        # Save assistant response
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response,
            }
        )

        # No st.rerun() here.
        # Streamlit already reruns after chat_input submission.


# ============================================================
# HUMAN SUPPORT COLUMN
# ============================================================

with support_col:

    st.markdown(
        '<div class="section-title">🧾 Human Support</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Load tickets
    # --------------------------------------------------------

    try:
        tickets = read_pending_tickets()

    except Exception as exc:

        tickets = []

        st.error(
            f"Could not load support tickets: {type(exc).__name__}"
        )


    pending_tickets = [
        ticket
        for ticket in tickets
        if str(ticket.get("status", "")).lower() == "pending"
    ]


    # --------------------------------------------------------
    # Pending count
    # --------------------------------------------------------

    st.metric(
        "Pending requests",
        len(pending_tickets),
    )


    # --------------------------------------------------------
    # Empty state
    # --------------------------------------------------------

    if not pending_tickets:

        st.success(
            "✓ No pending support requests"
        )

        st.caption(
            "Requests escalated to human support will "
            "appear here."
        )


    # --------------------------------------------------------
    # Tickets
    # --------------------------------------------------------

    else:

        for ticket in reversed(pending_tickets):

            ticket_id = ticket.get(
                "ticket_id",
                "Unknown ticket",
            )

            created_at = ticket.get(
                "created_at_utc",
                "",
            )

            summary = ticket.get(
                "summary",
                "No summary provided.",
            )

            customer = ticket.get(
                "customer_name",
                "",
            )

            email = ticket.get(
                "contact_email",
                "",
            )

            st.markdown(
                f"""
                <div class="queue-ticket">

                    <div class="ticket-id">
                        🎫 {ticket_id}
                    </div>

                    <div style="color:#6b7280;font-size:0.75rem;margin-top:0.2rem;">
                        Pending • {created_at}
                    </div>

                    <div class="ticket-summary">
                        {summary}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            if customer and customer != "Not provided":
                st.caption(
                    f"Customer: {customer}"
                )

            if email and email != "Not provided":
                st.caption(
                    f"Email: {email}"
                )


    # --------------------------------------------------------
    # Download tickets
    # --------------------------------------------------------

    if tickets:

        csv_data = pd.DataFrame(
            tickets
        ).to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="⬇️ Download ticket queue",
            data=csv_data,
            file_name="pending_tickets.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer-note">
        Customer Support AI • CrewAI single-agent system •
        Company knowledge search • Verified order lookup • Human escalation
    </div>
    """,
    unsafe_allow_html=True,
)
