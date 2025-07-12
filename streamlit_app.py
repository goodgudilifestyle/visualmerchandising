
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Store Sales Value Calculator", layout="wide")

st.title("🧮 30-Day Store Sales Value Calculator")

# Initialize session state for selected products
if "final_table" not in st.session_state:
    st.session_state.final_table = pd.DataFrame()
if "product_list" not in st.session_state:
    st.session_state.product_list = []

# File uploader
uploaded_file = st.file_uploader("📤 Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Read file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Ensure correct column names (strip and standardize)
    df.columns = df.columns.str.strip()

    # Calculate per-store sales value
    store_cols = ["BGD", "CS", "MLW", "HSR", "JYN", "JPN", "KHL"]
    for store in store_cols:
        df[f"{store} Sale Value"] = df[f"{store} 30D Sold Qty"] * df["Selling P"]

    # Store-wide sales table
    display_cols = ["Product Name", "SKU"] + [f"{store} Sale Value" for store in store_cols]
    sales_table = df[display_cols]

    st.markdown("### 📊 Full Store-Wise 30-Day Sales Value Table")
    st.dataframe(sales_table, use_container_width=True)

    # Product selection interface
    st.markdown("---")
    selected_product = st.selectbox("🔎 Select a Product to Add to Final Table", df["Product Name"].unique())

    if st.button("➕ Add to Final Table"):
        if selected_product not in st.session_state.product_list:
            selected_row = sales_table[df["Product Name"] == selected_product]
            st.session_state.final_table = pd.concat([st.session_state.final_table, selected_row], ignore_index=True)
            st.session_state.product_list.append(selected_product)

    # Display final table with totals
    if not st.session_state.final_table.empty:
        st.markdown("### ✅ Final Display Table")
        final_table_with_total = st.session_state.final_table.copy()
        total_row = final_table_with_total.iloc[:, 2:].sum(numeric_only=True)
        total_row["Product Name"] = "TOTAL"
        total_row["SKU"] = ""
        final_table_with_total = pd.concat([final_table_with_total, pd.DataFrame([total_row])], ignore_index=True)
        st.dataframe(final_table_with_total, use_container_width=True)

        # Download button
        to_download = final_table_with_total
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            to_download.to_excel(writer, index=False, sheet_name="Selected Products")
        st.download_button("📥 Download Final Table as Excel", data=buffer.getvalue(), file_name="final_sales_table.xlsx", mime="application/vnd.ms-excel")
