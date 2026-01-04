import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Lukas & Emelie Shopping", page_icon="🛒", layout="centered")

# 2. CSS Injection for Mobile Optimization
# This keeps the text and delete button on the same line and prevents clipping
st.markdown("""
    <style>
    /* Force columns to stay side-by-side on mobile */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        flex-wrap: nowrap !important;
    }
    
    /* Ensure the text column takes up most space */
    [data-testid="column"]:nth-child(1) {
        flex: 1 1 auto !important;
        min-width: 0 !important;
    }

    /* Fix the width of the delete button column so it doesn't cut off */
    [data-testid="column"]:nth-child(2) {
        width: 65px !important; 
        flex: 0 0 65px !important;
        min-width: 65px !important;
        text-align: right;
    }
    
    /* Make the button look better on mobile */
    .stButton button {
        padding: 0px 5px !important;
        height: 38px !important;
        width: 100% !important;
        border-radius: 8px;
    }

    /* Clean up spacing */
    .stMarkdown p {
        margin-bottom: 0px;
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛒 Shopping List")

# 3. Establish Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 4. Read Data
try:
    # ttl=0 ensures we don't cache data so both users see updates immediately
    df = conn.read(ttl=0)
except Exception as e:
    st.error("Connection Error: Make sure the Google Sheet is shared with the service account email.")
    st.stop()

# 5. Add Item Form
with st.form("add_item_form", clear_on_submit=True):
    new_item = st.text_input("What do we need?", placeholder="e.g. Milk, Eggs...")
    submit = st.form_submit_button("Add to List", use_container_width=True)
    
    if submit and new_item:
        # Create new row
        new_row = pd.DataFrame([{"item": new_item}])
        
        # Merge with existing data
        if df.empty:
            updated_df = new_row
        else:
            updated_df = pd.concat([df, new_row], ignore_index=True)
        
        # Update Google Sheets
        conn.update(data=updated_df)
        st.success(f"Added {new_item}!")
        st.rerun()

st.write("---")

# 6. Display Items
st.subheader("Current Items")

if not df.empty:
    for index, row in df.iterrows():
        # Skip empty rows in the sheet
        if pd.isna(row['item']) or row['item'].strip() == "":
            continue
            
        # Create columns for the item and the delete button
        col1, col2 = st.columns([0.85, 0.15], vertical_alignment="center", gap="small")
        
        # Column 1: Item Text
        col1.write(f"🔹 {row['item']}")
        
        # Column 2: Delete Button
        if col2.button("🗑️", key=f"btn_{index}"):
            updated_df = df.drop(index)
            conn.update(data=updated_df)
            st.rerun()
else:
    st.info("The list is empty!")

# 7. Footer (Optional)
st.caption("Shared list for Lukas & Emelie")