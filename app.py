import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Shopping List", page_icon="🛒", layout="centered")

# 2. THE ZERO-WIGGLE CSS
st.markdown("""
    <style>
    /* Kill all default padding/margins that cause the right-scroll */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main, .block-container {
        margin: 0 !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        overflow-x: hidden !important;
    }

    /* Target the content container specifically */
    .block-container {
        padding-top: 2rem !important;
        max-width: 100vw !important;
    }

    /* Force columns to stay in a tight row */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        width: 100% !important;
        gap: 0px !important; /* No gaps between columns */
    }

    /* Column 1 (Text) */
    [data-testid="column"]:nth-child(1) {
        flex: 10 !important; /* Take up 90% */
        min-width: 0 !important;
    }

    /* Column 2 (Button) */
    [data-testid="column"]:nth-child(2) {
        flex: 1 !important; /* Take up 10% */
        min-width: 45px !important;
        display: flex;
        justify-content: flex-end;
    }

    /* Button styling */
    .stButton button {
        border: none !important;
        background-color: transparent !important;
        font-size: 1.2rem !important;
        padding: 0 !important;
        width: 40px !important;
        height: 40px !important;
    }

    /* Fix text wrapping */
    .stMarkdown p {
        font-size: 1.1rem !important;
        line-height: 1.4 !important;
        word-wrap: break-word !important;
        margin: 0 !important;
    }

    /* Hide the Streamlit footer/hamburger menu for more space */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. App Title
st.title("🛒 Shopping List")

# 4. Connection & Data
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    df = conn.read(ttl=0)
except:
    st.stop()

# 5. Add Item Form
with st.form("add_item", clear_on_submit=True):
    new_item = st.text_input("Add to list...", placeholder="Milk, eggs...")
    if st.form_submit_button("Add Item", use_container_width=True):
        if new_item:
            new_row = pd.DataFrame([{"item": new_item}])
            updated_df = pd.concat([df, new_row], ignore_index=True) if not df.empty else new_row
            conn.update(data=updated_df)
            st.rerun()

st.write("---")

# 6. Display Items
if not df.empty:
    for index, row in df.iterrows():
        if pd.isna(row['item']) or not str(row['item']).strip():
            continue
            
        # We use a very tight column ratio
        c1, c2 = st.columns([0.9, 0.1])
        
        c1.write(f"🔹 {row['item']}")
        
        # When clicked, delete and refresh
        if c2.button("🗑️", key=f"del_{index}"):
            updated_df = df.drop(index)
            conn.update(data=updated_df)
            st.rerun()
else:
    st.info("List is empty!")