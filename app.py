import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Page setup
st.set_page_config(page_title="Lukas & Emelie Shopping", page_icon="🛒")
st.title("🛒 Shopping List")

# Create connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Read the data
try:
    df = conn.read(ttl=0)
except Exception as e:
    st.error("Could not read sheet. Make sure you shared it with the service account and cell A1 contains 'item'.")
    st.stop()

# Form to add new items
with st.form("add_item_form", clear_on_submit=True):
    new_item = st.text_input("Add something to the list...")
    submit = st.form_submit_button("Add Item", use_container_width=True)
    
    if submit and new_item:
        # Create a new row
        new_row = pd.DataFrame([{"item": new_item}])
        
        # Add to the current dataframe
        if df.empty:
            updated_df = new_row
        else:
            updated_df = pd.concat([df, new_row], ignore_index=True)
        
        # Save back to Google Sheets
        conn.update(data=updated_df)
        st.success(f"Added {new_item}!")
        st.rerun()

# Display the items
st.subheader("Current Items")
if not df.empty:
    for index, row in df.iterrows():
        # Handle cases where row might be empty
        if pd.isna(row['item']) or row['item'] == "":
            continue
            
        col1, col2 = st.columns([0.8, 0.2])
        col1.write(f"🔹 **{row['item']}**")
        
        if col2.button("🗑️", key=f"btn_{index}"):
            updated_df = df.drop(index)
            conn.update(data=updated_df)
            st.rerun()
else:
    st.info("The list is empty. Time to relax!")