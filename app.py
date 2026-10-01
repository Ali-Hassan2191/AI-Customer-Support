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

st.markdown(
    """
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    .stApp {
        background: #f7f8fc;
    }

    .main .block-container {
        max-width: 1450px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Remove unnecessary top spacing */
    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* ======================================================
       SIDEBAR
       ====================================================== */

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    [data-testid="stSidebar"] [data-testid="stTextInput"] {
        margin-bottom: 0.8rem;
    }

    [data-testid="stSidebar"] .stTextInput input {
        min-height: 42px;
        border-radius: 10px;
        border: 1px solid #d7dbe5;
        background: #ffffff;
    }

    [data-testid="stSidebar"] .stTextInput input:focus {
        border-color: #f59e0b;
        box-shadow: 0 0 0 1px #f59e0b;
    }

    .sidebar-brand {
        font-size: 1.18rem;
        font-weight: 750;
        color: #111827;
        margin-bottom: 0.25rem;
    }

    .sidebar-description {
        color: #6b7280;
        font-size: 0.82rem;
        line-height: 1.45;
        margin-bottom: 1.25rem;
    }

    .sidebar-section-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #111827;
        margin-top: 0.8rem;
        margin-bottom: 0.55rem;
    }

    /* ======================================================
       TOP HEADER
       ====================================================== */

    .top-title {
        font-size: 2rem;
        font-weight: 800;
        color: #111827;
        margin-bottom: 0.15rem;
    }

    .top-subtitle {
        font-size: 0.95rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }

    .title-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: #fff7ed;
        border: 1px solid #fed7aa;
        margin-right: 8px;
        vertical-align: middle;
    }

    /* ======================================================
       SECTION HEADERS
       ====================================================== */

    .section-heading {
        font-size: 1.15rem;
        font-weight: 750;
        color: #111827;
        margin-top: 0.15rem;
        margin-bottom: 0.75rem;
    }

    /* ======================================================
       WELCOME BOX
       ====================================================== */

    .welcome-title {
        font-size: 1.05rem;
        font-weight: 750;
        color: #111827;
        margin-bottom: 0.35rem;
    }

    .welcome-text {
        color: #6b7280;
        font-size: 0.92rem;
        line-height: 1.55;
        margin: 0;
    }

    /* ======================================================
       NATIVE STREAMLIT CONTAINERS
       ====================================================== */

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px;
    }

    /* ======================================================
       CHAT
       ====================================================== */

    [data-testid="stChatMessage"] {
        border-radius: 14px;
        margin-bottom: 0.6rem;
    }

    [data-testid="stChatInput"] {
        margin-top: 0.8rem;
    }

    [data-testid="stChatInput"] textarea {
        border-radius: 14px;
        border: 1px solid #d7dbe5;
    }

    [data-testid="stChatInput"] textarea:focus {
        border-color: #f59e0b;
        box-shadow: 0 0 0 1px #f59e0b;
    }

    /* ======================================================
       METRIC
       ====================================================== */

    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 0.85rem 1rem;
    }

    [data-testid="stMetricLabel"] {
        color: #6b7280;
    }

    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton > button {
        min-height: 42px;
        border-radius: 10px;
        font-weight: 650;
        border: 1px solid #d7dbe5;
    }

    .stButton > button:hover {
        border-color: #f59e0b;
        color: #b45309;
    }

    /* ======================================================
       DOWNLOAD BUTTON
       ====================================================== */

    .stDownloadButton > button {
        min-height: 42px;
        border-radius: 10px;
        font-weight: 650;
    }

    /* ======================================================
       SMALL SCREENS
       ====================================================== */

    @media (max-width: 900px) {

        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 1rem;
        }

        .top-title {
            font-size: 1.55rem;
        }

        .top-subtitle {
            font-size: 0.88rem;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
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
        '<div class="sidebar-brand">🟠 Customer Profile</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-description">'
        "Optional information helps our support team contact you "
        "if human assistance is needed."
        "</div>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # CUSTOMER NAME
    # --------------------------------------------------------

    customer_name = st.text_input(
        "Your name",
        key="customer_name",
        placeholder="Enter your name",
    )

    # --------------------------------------------------------
    # EMAIL
    # --------------------------------------------------------

    contact_email = st.text_input(
        "Email address",
        key="contact_email",
        placeholder="you@example.com",
    )

    st.divider()

    # --------------------------------------------------------
    # ORDER SUPPORT
    # --------------------------------------------------------

    st.markdown(
        '<div class="sidebar-section-title">📦 Order Support</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "For order status, provide both your **Order ID** "
        "and the **phone number used for that order**."
    )

    st.divider()

    # --------------------------------------------------------
    # CLEAR CHAT
    # --------------------------------------------------------

    if st.button(
        "🗑️ Clear conversation",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.caption("Customer Support AI")
    st.caption("Powered by CrewAI + Gemini")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="top-title">
        <span class="title-icon">🟡</span>
        Customer Support AI
    </div>

    <div class="top-subtitle">
        Get help with company information, products, orders,
        delivery status, and support requests.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MAIN COLUMNS
# ============================================================

chat_col, support_col = st.columns(
    [2.35, 1],
    gap="large",
)


# ============================================================
# CHAT AREA
# ============================================================

with chat_col:

    st.markdown(
        '<div class="section-heading">💬 Support Chat</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # WELCOME SCREEN
    # --------------------------------------------------------

    if not st.session_state.messages:

        with st.container(border=True):

            st.markdown(
                '<div class="welcome-title">👋 Welcome!</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<p class="welcome-text">'
                "I'm your customer support assistant. "
                "Ask me about company policies, products, "
                "orders, delivery status, or any support issue."
                "</p>",
                unsafe_allow_html=True,
            )

        st.write("")

        # ----------------------------------------------------
        # FEATURE CARDS
        # ----------------------------------------------------

        feature_1, feature_2, feature_3 = st.columns(
            3,
            gap="medium",
        )

        with feature_1:

            with st.container(border=True):

                st.markdown("### 📚")

                st.markdown("**Company Knowledge**")

                st.caption(
                    "Get answers from the company's "
                    "knowledge base."
                )

        with feature_2:

            with st.container(border=True):

                st.markdown("### 📦")

                st.markdown("**Order Tracking**")

                st.caption(
                    "Check verified order status using "
                    "your Order ID and phone number."
                )

        with feature_3:

            with st.container(border=True):

                st.markdown("### 🟠")

                st.markdown("**Human Support**")

                st.caption(
                    "Issues that need human help can "
                    "be escalated to support."
                )

    # --------------------------------------------------------
    # EXISTING MESSAGES
    # --------------------------------------------------------

    for message in st.session_state.messages:

        role = message.get("role", "assistant")
        content = message.get("content", "")

        if role == "user":
            avatar = "🟠"
        else:
            avatar = "🟡"

        with st.chat_message(
            role,
            avatar=avatar,
        ):
            st.markdown(content)

    # --------------------------------------------------------
    # CHAT INPUT
    # --------------------------------------------------------

    prompt = st.chat_input(
        "Ask something about your order or company support..."
    )

    # --------------------------------------------------------
    # HANDLE MESSAGE
    # --------------------------------------------------------

    if prompt:

        # Save current user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        # Display user message
        with st.chat_message(
            "user",
            avatar="🟠",
        ):
            st.markdown(prompt)

        # Generate AI response
        with st.chat_message(
            "assistant",
            avatar="🟡",
        ):

            with st.spinner("Thinking..."):

                try:

                    # Exclude current message from history
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

                    # IMPORTANT:
                    # Full error shown during development.
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


# ============================================================
# HUMAN SUPPORT
# ============================================================

with support_col:

    st.markdown(
        '<div class="section-heading">🧾 Human Support</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # LOAD TICKETS
    # --------------------------------------------------------

    try:

        tickets = read_pending_tickets()

    except Exception as exc:

        tickets = []

        st.error(
            f"Could not load support tickets: "
            f"{type(exc).__name__}: {exc}"
        )

    # --------------------------------------------------------
    # FILTER PENDING
    # --------------------------------------------------------

    pending_tickets = [
        ticket
        for ticket in tickets
        if str(
            ticket.get("status", "")
        ).strip().lower() == "pending"
    ]

    # --------------------------------------------------------
    # COUNT
    # --------------------------------------------------------

    st.metric(
        "Pending requests",
        len(pending_tickets),
    )

    st.write("")

    # --------------------------------------------------------
    # EMPTY STATE
    # --------------------------------------------------------

    if not pending_tickets:

        with st.container(border=True):

            st.markdown("### 🟢 All clear")

            st.write(
                "No pending human-support requests."
            )

            st.caption(
                "Escalated requests will appear here."
            )

    # --------------------------------------------------------
    # TICKETS
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

            with st.container(border=True):

                st.markdown(
                    f"**🎫 {ticket_id}**"
                )

                st.caption(
                    f"Pending • {created_at}"
                )

                st.write(summary)

                if (
                    customer
                    and customer != "Not provided"
                ):
                    st.caption(
                        f"Customer: {customer}"
                    )

                if (
                    email
                    and email != "Not provided"
                ):
                    st.caption(
                        f"Email: {email}"
                    )

    # --------------------------------------------------------
    # DOWNLOAD QUEUE
    # --------------------------------------------------------

    if tickets:

        csv_data = (
            pd.DataFrame(tickets)
            .to_csv(index=False)
            .encode("utf-8")
        )

        st.write("")

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

st.divider()

st.caption(
    "Customer Support AI • CrewAI single-agent system • "
    "Company knowledge search • Verified order lookup • "
    "Human escalation"
)
