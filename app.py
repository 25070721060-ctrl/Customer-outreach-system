"""
app.py
------
Run with:  streamlit run app.py

A simple dashboard with two tabs:
1. Find Leads   - search Google and/or Hunter.io, collect results into a table
2. Send Emails  - review the collected leads, write a template, send emails

Leads are kept in Streamlit's session state and can be exported/imported as CSV.
"""

import os
import io
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from lead_finder import search_google_leads, find_emails_for_domain
from email_sender import send_bulk_emails

load_dotenv()

st.set_page_config(page_title="Lead Gen Dashboard", layout="wide")

if "leads" not in st.session_state:
    st.session_state.leads = pd.DataFrame(
        columns=["first_name", "last_name", "position", "email", "domain", "source"]
    )

st.title("📊 Lead Gen & Outreach Dashboard")

tab_find, tab_send, tab_data = st.tabs(["🔎 Find Leads", "✉️ Send Emails", "🗂️ Lead Data"])

# ---------------------------------------------------------------------------
# TAB 1: Find Leads
# ---------------------------------------------------------------------------
with tab_find:
    st.subheader("Find leads via Google")
    col1, col2 = st.columns(2)
    with col1:
        google_query = st.text_input(
            "Google search query",
            placeholder='e.g. "digital marketing agency" contact site:.com',
        )
        if st.button("Search Google"):
            api_key = os.getenv("GOOGLE_API_KEY")
            cse_id = os.getenv("GOOGLE_CSE_ID")
            if not api_key or not cse_id:
                st.error("Set GOOGLE_API_KEY and GOOGLE_CSE_ID in your .env file first.")
            else:
                with st.spinner("Searching..."):
                    results = search_google_leads(google_query, api_key, cse_id)
                st.write(f"Found {len(results)} results:")
                st.dataframe(pd.DataFrame(results), use_container_width=True)
                st.caption("These are companies/pages, not verified emails yet. Use the Hunter.io search below with a domain to get actual email addresses.")

    st.divider()
    st.subheader("Find verified emails at a company domain (Hunter.io)")
    with col2:
        domain = st.text_input("Company domain", placeholder="e.g. example.com")
        limit = st.slider("Max results", 1, 50, 10)
        if st.button("Search Hunter.io"):
            api_key = os.getenv("HUNTER_API_KEY")
            if not api_key:
                st.error("Set HUNTER_API_KEY in your .env file first.")
            elif not domain:
                st.error("Enter a domain first.")
            else:
                with st.spinner("Searching..."):
                    new_leads = find_emails_for_domain(domain, api_key, limit)
                if new_leads:
                    new_df = pd.DataFrame(new_leads)
                    new_df["source"] = "hunter.io"
                    st.session_state.leads = pd.concat(
                        [st.session_state.leads, new_df], ignore_index=True
                    ).drop_duplicates(subset="email")
                    st.success(f"Added {len(new_leads)} leads. See the 'Lead Data' tab.")
                else:
                    st.warning("No emails found for that domain.")

# ---------------------------------------------------------------------------
# TAB 2: Send Emails
# ---------------------------------------------------------------------------
with tab_send:
    st.subheader("Compose outreach email")
    st.caption("Use {first_name}, {last_name}, {position}, {email}, {domain} as placeholders - they'll be filled in per lead.")

    subject_template = st.text_input("Subject", value="Quick question, {first_name}")
    body_template = st.text_area(
        "Body",
        height=220,
        value=(
            "Hi {first_name},\n\n"
            "[Product details will go here once you have them - "
            "what it does, why it's relevant to their role/company, "
            "and a clear next step like a call link or reply prompt.]\n\n"
            "Best,\n[Your Name]\n\n"
            "---\n"
            "If you'd rather not hear from us again, just reply and let me know."
        ),
    )

    st.divider()
    st.subheader("Select leads to email")
    if st.session_state.leads.empty:
        st.info("No leads yet - go find some in the 'Find Leads' tab, or upload a CSV in 'Lead Data'.")
    else:
        editable = st.session_state.leads.copy()
        editable.insert(0, "send", True)
        edited = st.data_editor(editable, use_container_width=True, key="send_editor")
        selected = edited[edited["send"]].drop(columns=["send"])

        st.write(f"{len(selected)} lead(s) selected")

        confirm = st.checkbox("I've filled in real product details above and confirm I want to send these emails")
        if st.button("Send Emails", disabled=not confirm):
            smtp_config = {
                "host": os.getenv("SMTP_HOST"),
                "port": int(os.getenv("SMTP_PORT", 587)),
                "username": os.getenv("SMTP_USERNAME"),
                "password": os.getenv("SMTP_PASSWORD"),
                "sender_name": os.getenv("SENDER_NAME", ""),
            }
            if not smtp_config["username"] or not smtp_config["password"]:
                st.error("Set SMTP_USERNAME and SMTP_PASSWORD in your .env file first.")
            else:
                with st.spinner("Sending..."):
                    results = send_bulk_emails(
                        selected.to_dict("records"),
                        subject_template,
                        body_template,
                        smtp_config,
                    )
                results_df = pd.DataFrame(results)
                st.dataframe(results_df, use_container_width=True)
                sent_count = results_df["success"].sum()
                st.success(f"Sent {sent_count}/{len(results_df)} emails.")

# ---------------------------------------------------------------------------
# TAB 3: Lead Data (view / import / export)
# ---------------------------------------------------------------------------
with tab_data:
    st.subheader("All collected leads")
    st.dataframe(st.session_state.leads, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        csv_bytes = st.session_state.leads.to_csv(index=False).encode("utf-8")
        st.download_button("Download leads as CSV", csv_bytes, "leads.csv", "text/csv")

    with col_b:
        uploaded = st.file_uploader("Import leads from CSV", type="csv")
        if uploaded is not None:
            imported = pd.read_csv(uploaded)
            st.session_state.leads = pd.concat(
                [st.session_state.leads, imported], ignore_index=True
            ).drop_duplicates(subset="email")
            st.success(f"Imported {len(imported)} rows.")
