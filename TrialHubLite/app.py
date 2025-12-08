import streamlit as st
import sqlite3
import pandas as pd

# Page Config
st.set_page_config(
    page_title="TrialHub Lite",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 TrialHub Lite")

# Database Connection
@st.cache_resource
def get_connection():
    return sqlite3.connect("trialhub.db", check_same_thread=False)

conn = get_connection()

# Fetch Data
def load_data():
    query = "SELECT * FROM trials"
    df = pd.read_sql(query, conn)
    return df

try:
    df = load_data()
    
    # Metrics
    st.metric("Total Trials", len(df))
    
    # Search/Filter
    search_term = st.text_input("Search (Subject, Phone, Note, etc.)", "")
    
    if search_term:
        # Simple case-insensitive search across all columns
        mask = df.apply(lambda x: x.astype(str).str.contains(search_term, case=False).any(), axis=1)
        df_display = df[mask]
    else:
        df_display = df

    # Display Data
    st.dataframe(
        df_display,
        use_container_width=True,
        column_config={
            "meet_link": st.column_config.LinkColumn("Meet Link"),
            "phone": st.column_config.TextColumn("Phone"),
            "status": st.column_config.TextColumn("Status"),
        },
        hide_index=True
    )

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Please ensure 'trialhub.db' exists and is populated.")

