import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Lukas & Emelie Shopping", page_icon="🛒", layout="centered")

# 2. CSS Injection for a "Locked" Mobile UI
st.markdown("""
    <style>
    /* 1. Prevent horizontal scrolling on the whole app */
    html, body, .stApp {
        overflow-x: hidden !important;
        width: 100% !important;
    }

    /* 2. Force columns to stay side-by-side and fit the screen */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        flex-wrap: nowrap !important;
        width: 100% !important;
    }
    
    /* 3. Text Column: Force it to wrap if the text is long */
    [data-testid="column"]:nth-child(1) {
        flex: 1 1 auto !important;
        min-width: 0 !important;
        word-break: break-word !important; /* This prevents horizontal push */
        overflow-wrap: break-word !important;
    }

    /* 4. Button Column: Fixed width, no shifting */
    [data-testid="column"]:nth-child(2) {
        width: 50px !important; 
        flex: 0 0 50px !important;
        min-width: 50px !important;
        text-align: right;
    }
    
    /* 5. Button styling */
    .stButton button {
        padding: 0px !important;
        height: 35px !important;
        width: 40px !important;
        border-radius: 8px;
        margin-left: auto;
    }

    /* 6. Clean up text spacing */
    .stMarkdown p {
        margin-bottom: 0px;
        font-size: 1.1rem;
        line-height: 1.2;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛒 Shopping List")

# 3. Establish Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 4. Read Data
try:
    df = conn.read(ttl=0)
except Exception as e:
    st.error("Connection Error: Check Google Sheet sharing settings.")
    st.stop()

# 5. Add Item Form
with st.form("add_item_form", clear_on_submit=True):
    new_item = st.text_input("What do we need?", placeholder="e.g. Milk...")
    submit = st.form_submit_button("Add Item", use_container_width=True)
    
    if submit and new_item:
        new_row = pd.DataFrame([{"item": new_item}])
        updated_df = pd.concat([df, new_row], ignore_index=True) if not df.empty else new_row
        conn.update(data=updated_df)
        st.success(f"Added {new_item}!")
        st.rerun()

st.write("---")

# 6. Display Items
st.subheader("Current Items")

if not df.empty:
    for index, row in df.iterrows():
        if pd.isna(row['item']) or row['item'].strip() == "":
            continue
            
        # Using columns with a small gap
        col1, col2 = st.columns([0.85, 0.15], vertical_alignment="center")
        
        col1.write(f"🔹 {row['item']}")
        
        if col2.button("🗑️", key=f"btn_{index}"):
            updated_df = df.drop(index)
            conn.update(data=updated_df)
            st.rerun()
else:
    st.info("The list is empty!")

st.caption("Shared list for Lukas & Emelie")