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

    /* ================= GLOBAL ================= */

    .stApp {
        background: #f7f8fc;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* ================= HEADER ================= */

    .main-header {
        background: linear-gradient(135deg, #111827, #1f2937);
        padding: 28px 32px;
        border-radius: 18px;
        margin-bottom: 24px;
        color: white;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
    }

    .main-header h1 {
        margin: 0;
        font-size: 30px;
        font-weight: 700;
    }

    .main-header p {
        margin: 8px 0 0 0;
        color: #d1d5db;
        font-size: 15px;
        line-height: 1.5;
    }

    /* ================= WELCOME ================= */

    .welcome-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 18px;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.04);
    }

    .welcome-card h3 {
        margin: 0 0 8px 0;
        color: #111827;
    }

    .welcome-card p {
        color: #6b7280;
        margin: 0;
        line-height: 1.6;
    }

    /* ================= FEATURE CARDS ================= */

    .feature-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 18px;
        min-height: 145px;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.03);
    }

    .feature-icon {
        font-size: 24px;
        margin-bottom: 8px;
    }

    .feature-title {
        font-weight: 650;
        color: #111827;
        margin-bottom: 6px;
    }

    .feature-text {
        color: #6b7280;
        font-size: 13px;
        line-height: 1.5;
    }

    /* ================= SIDEBAR ================= */

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    /* ================= CHAT ================= */

    [data-testid="stChatMessage"] {
        border-radius: 14px;
    }

    /* ================= BUTTONS ================= */

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

    /* ================= FOOTER ================= */

    .footer {
        text-align: center;
        color: #9ca3af;
        font-size: 12px;
        padding-top: 18px;
        line-height: 1.6;
    }

    /* ================= RESPONSIVE ================= */

    @media (max-width: 900px) {

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .main-header {
            padding: 22px;
        }

        .main-header h1 {
            font-size: 25px;
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
# MAIN LAYOUT
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

        feature_col1, feature_col2, feature_col3 = st.columns(
            3,
            gap="medium",
        )

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

        role = message.get("role", "assistant")
        content = message.get("content", "")

        with st.chat_message(role):

            st.markdown(content)

    # -----------------------------------------------------
    # Chat input
    # -----------------------------------------------------

    prompt = st.chat_input(
        "Type your message..."
    )

    if prompt:

        # Save user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # -------------------------------------------------
        # Agent response
        # -------------------------------------------------

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

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

                    response = str(response).strip()

                    if not response:
                        response = (
                            "I'm sorry, I couldn't generate "
                            "a response. Please try again."
                        )

                except Exception as exc:

                    # Show actual error while testing
                    st.error(
                        f"Agent error: {type(exc).__name__}: {exc}"
                    )

                    st.exception(exc)

                    response = (
                        "I'm sorry, something went wrong "
                        "while processing your request. "
                        "Please try again."
                    )

            st.markdown(response)

        # Save assistant response
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

    st.markdown("### 🧾 Human Support")

    # -----------------------------------------------------
    # Read tickets
    # -----------------------------------------------------

    try:

        tickets = read_pending_tickets()

    except Exception as exc:

        tickets = []

        st.error(
            f"Could not load support tickets: "
            f"{type(exc).__name__}: {exc}"
        )

    # -----------------------------------------------------
    # Pending tickets only
    # -----------------------------------------------------

    pending_tickets = [
        ticket
        for ticket in tickets
        if str(
            ticket.get("status", "")
        ).strip().lower()
        == "pending"
    ]

    # -----------------------------------------------------
    # Counter
    # -----------------------------------------------------

    st.metric(
        "Pending requests",
        len(pending_tickets),
    )

    # =====================================================
    # EMPTY QUEUE
    # =====================================================

    if not pending_tickets:

        st.success(
            "✓ No pending support requests"
        )

        st.caption(
            "Requests escalated to human support "
            "will appear here."
        )

    # =====================================================
    # TICKETS
    # =====================================================

    else:

        st.markdown("#### Open Requests")

        for ticket in reversed(pending_tickets):

            ticket_id = str(
                ticket.get(
                    "ticket_id",
                    "Unknown",
                )
            )

            status = str(
                ticket.get(
                    "status",
                    "Pending",
                )
            )

            created = str(
                ticket.get(
                    "created_at_utc",
                    "",
                )
            )

            summary = str(
                ticket.get(
                    "summary",
                    "No summary available.",
                )
            )

            customer = str(
                ticket.get(
                    "customer_name",
                    "",
                )
            )

            email = str(
                ticket.get(
                    "contact_email",
                    "",
                )
            )

            # -------------------------------------------------
            # IMPORTANT:
            # Native Streamlit components are used here.
            # No custom HTML.
            # This prevents raw <div>, <span>, etc.
            # from appearing in the UI.
            # -------------------------------------------------

            with st.container(
                border=True
            ):

                # Ticket heading
                ticket_col1, ticket_col2 = st.columns(
                    [1.7, 1],
                    gap="small",
                )

                with ticket_col1:

                    st.markdown(
                        f"**🎫 {ticket_id}**"
                    )

                with ticket_col2:

                    st.markdown(
                        f"**🟠 {status}**"
                    )

                # Created time
                if created:

                    st.caption(
                        f"Created: {created}"
                    )

                # Summary
                st.write(
                    summary
                )

                # Customer information
                if (
                    customer
                    and customer.lower()
                    != "not provided"
                ):

                    st.caption(
                        f"👤 Customer: {customer}"
                    )

                # Email
                if (
                    email
                    and email.lower()
                    != "not provided"
                ):

                    st.caption(
                        f"✉️ Email: {email}"
                    )

    # =====================================================
    # DOWNLOAD TICKETS
    # =====================================================

    if tickets:

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
