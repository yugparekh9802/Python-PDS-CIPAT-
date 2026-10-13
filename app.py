

import streamlit as st
import pandas as pd
from datetime import date


import manufacturing_utils as mu




st.set_page_config(
    page_title="Manufacturing Analytics",
    page_icon="🏭",
    layout="wide",
)


mu.initialize_csv()



# SIDEBAR NAVIGATION (Python Core Concepts: variables + conditionals)

st.sidebar.title("🏭 Manufacturing Analytics")
menu_choice = st.sidebar.radio(
    "Navigate to:",
    (
        "Dashboard",
        "Add Record",
        "View Records",
        "Search Records",
        "Update Record",
        "Delete Record",
        "Generate Sample Data",
    ),
)

st.sidebar.markdown("---")




#  DASHBOARD

if menu_choice == "Dashboard":
    st.title("📊 Manufacturing Dashboard")
    st.write("A quick overview of all production activity recorded so far.")

    summary = mu.get_dashboard_summary()

    # Show key numbers in metric cards
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Production", f"{summary['total_production']:,} units")
    col2.metric("Good Units", f"{summary['good_units']:,} units")
    col3.metric("Total Defective Units", f"{summary['total_defects']:,} units")

    col4, col5 = st.columns(2)
    col4.metric("Defect Percentage", f"{summary['defect_percentage']}%")
    col5.metric("Total Production Cost", f"₹ {summary['total_cost']:,.2f}")

    st.markdown("---")
    st.subheader("🏗️ Machine-wise Production")

    machine_data = summary["machine_wise_production"]
    if machine_data is not None and not machine_data.empty:
        chart_data = machine_data.set_index("Machine_ID")
        st.bar_chart(chart_data)
        st.dataframe(machine_data, use_container_width=True)
    else:
        st.info("No data available yet. Add records or generate sample data first.")



#  ADD RECORD  (CRUD - Create)

elif menu_choice == "Add Record":
    st.title("➕ Add New Production Record")

    with st.form("add_record_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            product_id = st.text_input("Product ID (e.g. P2001)")
            product_name = st.text_input("Product Name")
            machine_id = st.text_input("Machine ID (e.g. M101)")
            record_date = st.date_input("Date", value=date.today())

        with col2:
            quantity_produced = st.text_input("Quantity Produced", value="0")
            defective_units = st.text_input("Defective Units", value="0")
            production_cost = st.text_input("Production Cost", value="0.0")

        submitted = st.form_submit_button("Add Record")

    if submitted:
        # E. EXCEPTION HANDLING happens inside mu.add_record()
        success, message = mu.add_record(
            product_id=product_id.strip(),
            product_name=product_name.strip(),
            machine_id=machine_id.strip(),
            quantity_produced=quantity_produced,
            defective_units=defective_units,
            production_cost=production_cost,
            date=str(record_date),
        )
        if success:
            st.success(message)
        else:
            st.error(message)



#  VIEW RECORDS  (CRUD - Read)

elif menu_choice == "View Records":
    st.title("📋 All Production Records")

    data_frame = mu.view_all_records()

    if data_frame.empty:
        st.info("No records found. Try adding a record or generating sample data.")
    else:
        st.write(f"Showing **{len(data_frame)}** record(s).")
        st.dataframe(data_frame, use_container_width=True)

        # Simple file download button (uses the CSV file we already have)
        csv_bytes = data_frame.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download as CSV",
            data=csv_bytes,
            file_name="production_data_export.csv",
            mime="text/csv",
        )



#  SEARCH RECORDS  (CRUD - Read / search)

elif menu_choice == "Search Records":
    st.title("🔍 Search Production Records")

    search_column = st.selectbox("Search by column:", mu.COLUMNS)
    search_value = st.text_input("Search value")

    if st.button("Search"):
        try:
            if search_value.strip() == "":
                st.warning("Please enter a value to search for.")
            else:
                results = mu.search_records(search_column, search_value.strip())
                if results.empty:
                    st.info("No matching records found.")
                else:
                    st.success(f"Found {len(results)} matching record(s).")
                    st.dataframe(results, use_container_width=True)
        except Exception as error:
            st.error(f"Something went wrong while searching: {error}")



# UPDATE RECORD  (CRUD - Update)

elif menu_choice == "Update Record":
    st.title("✏️ Update a Production Record")

    product_id_to_update = st.text_input("Enter the Product ID to update")

    if product_id_to_update:
        existing = mu.search_records("Product_ID", product_id_to_update)

        if existing.empty:
            st.warning("No record found with that Product ID.")
        else:
            st.write("Current record:")
            st.dataframe(existing, use_container_width=True)

            current = existing.iloc[0]

            with st.form("update_record_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_product_name = st.text_input(
                        "Product Name", value=str(current["Product_Name"])
                    )
                    new_machine_id = st.text_input(
                        "Machine ID", value=str(current["Machine_ID"])
                    )
                    new_date = st.text_input("Date", value=str(current["Date"]))

                with col2:
                    new_quantity = st.text_input(
                        "Quantity Produced", value=str(current["Quantity_Produced"])
                    )
                    new_defects = st.text_input(
                        "Defective Units", value=str(current["Defective_Units"])
                    )
                    new_cost = st.text_input(
                        "Production Cost", value=str(current["Production_Cost"])
                    )

                update_submitted = st.form_submit_button("Update Record")

            if update_submitted:
                updated_fields = {
                    "Product_Name": new_product_name,
                    "Machine_ID": new_machine_id,
                    "Date": new_date,
                    "Quantity_Produced": new_quantity,
                    "Defective_Units": new_defects,
                    "Production_Cost": new_cost,
                }
                success, message = mu.update_record(product_id_to_update, updated_fields)
                if success:
                    st.success(message)
                else:
                    st.error(message)



#  DELETE RECORD  (CRUD - Delete)

elif menu_choice == "Delete Record":
    st.title("🗑️ Delete a Production Record")

    product_id_to_delete = st.text_input("Enter the Product ID to delete")

    if product_id_to_delete:
        existing = mu.search_records("Product_ID", product_id_to_delete)
        if existing.empty:
            st.warning("No record found with that Product ID.")
        else:
            st.dataframe(existing, use_container_width=True)
            confirm = st.checkbox("Yes, I confirm I want to delete this record.")
            if st.button("Delete Record"):
                if not confirm:
                    st.warning("Please check the confirmation box before deleting.")
                else:
                    success, message = mu.delete_record(product_id_to_delete)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)



#  GENERATE SAMPLE DATA

elif menu_choice == "Generate Sample Data":
    st.title("🎲 Generate Random Sample Data")
    st.write(
        "This will generate **100 realistic random production records** "
        "and overwrite the current `production_data.csv` file."
    )

    num_records = st.number_input(
        "Number of records to generate", min_value=1, max_value=1000, value=100
    )

    if st.button("Generate Sample Data"):
        success, message = mu.generate_sample_data(int(num_records))
        if success:
            st.success(message)
            st.dataframe(mu.view_all_records(), use_container_width=True)
        else:
            st.error(message)




