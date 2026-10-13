"""
manufacturing_utils.py
------------------------------------------------------
Custom module for the Manufacturing Analytics project.

This file demonstrates several syllabus topics on its own:
    A. Python Core Concepts   -> functions, loops, conditionals, f-strings
    B. Data Structures        -> lists and dictionaries used everywhere
    C. Python Libraries       -> pandas, csv, os, random, datetime
    D. Custom Modules         -> this whole file IS the custom module
    E. Exception Handling     -> try/except blocks in every risky operation
    F. File Handling          -> reading/writing production_data.csv

app.py simply imports this module and calls these functions, which keeps
the Streamlit UI code separate from the "business logic" code.
------------------------------------------------------
"""

import csv
import os
import random
from datetime import datetime, timedelta

import pandas as pd

# ------------------------------------------------------------------
# A. CONSTANTS (Python Core Concepts)
# ------------------------------------------------------------------
CSV_FILE = "production_data.csv"

# The column order used everywhere in this project.
COLUMNS = [
    "Product_ID",
    "Product_Name",
    "Machine_ID",
    "Quantity_Produced",
    "Defective_Units",
    "Production_Cost",
    "Date",
]

# Sample lists used to generate realistic random data (Data Structures: lists)
PRODUCT_NAMES = [
    "Steel Rod", "Copper Wire", "Plastic Casing", "Rubber Gasket",
    "Aluminum Sheet", "Glass Panel", "Circuit Board", "Ball Bearing",
    "Metal Bracket", "Plastic Bottle", "Engine Bolt", "Wooden Pallet",
    "Ceramic Tile", "Steel Pipe", "Nylon Rope",
]

MACHINE_IDS = ["M101", "M102", "M103", "M104", "M105", "M106", "M107", "M108"]


# ------------------------------------------------------------------
# F. FILE HANDLING
# ------------------------------------------------------------------
def initialize_csv():
    """
    Make sure production_data.csv exists with the correct header.
    Uses exception handling in case the file cannot be created
    (e.g. permission problems).
    """
    try:
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(COLUMNS)
    except Exception as error:
        print(f"Error initializing CSV file: {error}")


def load_data():
    """
    Read the CSV file into a pandas DataFrame.
    Returns an empty DataFrame (with correct columns) if something goes wrong.
    """
    try:
        initialize_csv()
        data_frame = pd.read_csv(CSV_FILE)
        return data_frame
    except FileNotFoundError:
        print("CSV file not found. Returning an empty table instead.")
        return pd.DataFrame(columns=COLUMNS)
    except pd.errors.EmptyDataError:
        print("CSV file is empty. Returning an empty table instead.")
        return pd.DataFrame(columns=COLUMNS)
    except Exception as error:
        print(f"Unexpected error while loading data: {error}")
        return pd.DataFrame(columns=COLUMNS)


def save_data(data_frame):
    """
    Save a pandas DataFrame back to the CSV file.
    Returns True on success, False on failure.
    """
    try:
        data_frame.to_csv(CSV_FILE, index=False)
        return True
    except Exception as error:
        print(f"Error saving data to CSV: {error}")
        return False


# ------------------------------------------------------------------
# H. CRUD OPERATIONS  (Create, Read, Update, Delete)
# ------------------------------------------------------------------
def add_record(product_id, product_name, machine_id,
               quantity_produced, defective_units, production_cost, date):
    """
    CREATE: Add one new production record to the CSV file.
    A dictionary (Data Structure) is used to represent a single record.
    """
    try:
        # ---- Basic validation using exception handling ----
        quantity_produced = int(quantity_produced)
        defective_units = int(defective_units)
        production_cost = float(production_cost)

        if quantity_produced < 0 or defective_units < 0 or production_cost < 0:
            return False, "Numbers cannot be negative."

        if defective_units > quantity_produced:
            return False, "Defective units cannot exceed quantity produced."

        if product_id == "" or product_name == "" or machine_id == "":
            return False, "Product ID, Product Name and Machine ID cannot be empty."

        data_frame = load_data()

        # Prevent duplicate Product IDs
        if product_id in data_frame["Product_ID"].astype(str).values:
            return False, f"Product ID '{product_id}' already exists."

        new_record = {
            "Product_ID": product_id,
            "Product_Name": product_name,
            "Machine_ID": machine_id,
            "Quantity_Produced": quantity_produced,
            "Defective_Units": defective_units,
            "Production_Cost": production_cost,
            "Date": date,
        }

        # Add the new row using pandas concat
        new_row_df = pd.DataFrame([new_record])
        data_frame = pd.concat([data_frame, new_row_df], ignore_index=True)

        if save_data(data_frame):
            return True, "Record added successfully!"
        else:
            return False, "Could not save the record to file."

    except ValueError:
        return False, "Quantity, Defective Units and Cost must be valid numbers."
    except Exception as error:
        return False, f"Unexpected error: {error}"


def view_all_records():
    """READ: Return every record in the CSV file as a DataFrame."""
    return load_data()


def search_records(search_by, search_value):
    """
    READ (search): Find records matching a value in a chosen column.
    search_by must be one of the COLUMNS.
    """
    try:
        data_frame = load_data()
        if data_frame.empty:
            return data_frame

        # Search as text, case-insensitive, "contains" style search
        mask = data_frame[search_by].astype(str).str.contains(
            str(search_value), case=False, na=False
        )
        return data_frame[mask]
    except KeyError:
        print(f"Column '{search_by}' does not exist.")
        return pd.DataFrame(columns=COLUMNS)
    except Exception as error:
        print(f"Error while searching: {error}")
        return pd.DataFrame(columns=COLUMNS)


def update_record(product_id, updated_fields):
    """
    UPDATE: Find a record by Product_ID and update the given fields.
    updated_fields is a dictionary, e.g. {"Quantity_Produced": 500}
    """
    try:
        data_frame = load_data()
        product_id_column = data_frame["Product_ID"].astype(str)

        if product_id not in product_id_column.values:
            return False, f"Product ID '{product_id}' not found."

        row_index = data_frame[product_id_column == product_id].index[0]

        for field_name, field_value in updated_fields.items():
            if field_name in ["Quantity_Produced", "Defective_Units"]:
                field_value = int(field_value)
            elif field_name == "Production_Cost":
                field_value = float(field_value)
            data_frame.at[row_index, field_name] = field_value

        if save_data(data_frame):
            return True, "Record updated successfully!"
        else:
            return False, "Could not save changes to file."

    except ValueError:
        return False, "Please enter valid numbers for numeric fields."
    except Exception as error:
        return False, f"Unexpected error: {error}"


def delete_record(product_id):
    """DELETE: Remove a record by Product_ID."""
    try:
        data_frame = load_data()
        product_id_column = data_frame["Product_ID"].astype(str)

        if product_id not in product_id_column.values:
            return False, f"Product ID '{product_id}' not found."

        data_frame = data_frame[product_id_column != product_id]

        if save_data(data_frame):
            return True, "Record deleted successfully!"
        else:
            return False, "Could not save changes to file."
    except Exception as error:
        return False, f"Unexpected error: {error}"


# ------------------------------------------------------------------
# C. PYTHON LIBRARIES + B. DATA STRUCTURES: Sample data generation
# ------------------------------------------------------------------
def generate_sample_data(number_of_records=100):
    """
    Generate a list of dictionaries containing realistic random
    manufacturing records, then save them to the CSV file.
    This OVERWRITES the existing file with fresh sample data.
    """
    try:
        records_list = []          # list of dictionaries (Data Structure)
        today = datetime.now()

        for i in range(1, number_of_records + 1):
            product_id = f"P{1000 + i}"
            product_name = random.choice(PRODUCT_NAMES)
            machine_id = random.choice(MACHINE_IDS)

            quantity_produced = random.randint(100, 1000)
            # Defective units are usually a small percentage of quantity produced
            defect_rate = random.uniform(0.0, 0.10)
            defective_units = int(quantity_produced * defect_rate)

            production_cost = round(random.uniform(500.0, 5000.0), 2)

            random_days_ago = random.randint(0, 89)
            record_date = (today - timedelta(days=random_days_ago)).strftime("%Y-%m-%d")

            record = {
                "Product_ID": product_id,
                "Product_Name": product_name,
                "Machine_ID": machine_id,
                "Quantity_Produced": quantity_produced,
                "Defective_Units": defective_units,
                "Production_Cost": production_cost,
                "Date": record_date,
            }
            records_list.append(record)

        data_frame = pd.DataFrame(records_list, columns=COLUMNS)

        if save_data(data_frame):
            return True, f"{number_of_records} sample records generated successfully!"
        else:
            return False, "Could not save generated sample data."

    except Exception as error:
        return False, f"Error generating sample data: {error}"


# ------------------------------------------------------------------
# DASHBOARD CALCULATIONS
# ------------------------------------------------------------------
def get_dashboard_summary():
    """
    Calculate simple dashboard statistics and return them as a dictionary.
    """
    try:
        data_frame = load_data()

        if data_frame.empty:
            return {
                "total_production": 0,
                "total_defects": 0,
                "good_units": 0,
                "defect_percentage": 0.0,
                "total_cost": 0.0,
                "machine_wise_production": pd.DataFrame(),
            }

        # Make sure numeric columns are actually numeric
        data_frame["Quantity_Produced"] = pd.to_numeric(
            data_frame["Quantity_Produced"], errors="coerce"
        ).fillna(0)
        data_frame["Defective_Units"] = pd.to_numeric(
            data_frame["Defective_Units"], errors="coerce"
        ).fillna(0)
        data_frame["Production_Cost"] = pd.to_numeric(
            data_frame["Production_Cost"], errors="coerce"
        ).fillna(0)

        total_production = int(data_frame["Quantity_Produced"].sum())
        total_defects = int(data_frame["Defective_Units"].sum())
        good_units = total_production - total_defects
        total_cost = float(data_frame["Production_Cost"].sum())

        if total_production > 0:
            defect_percentage = round((total_defects / total_production) * 100, 2)
        else:
            defect_percentage = 0.0

        machine_wise_production = (
            data_frame.groupby("Machine_ID")["Quantity_Produced"]
            .sum()
            .reset_index()
            .sort_values(by="Quantity_Produced", ascending=False)
        )

        summary = {
            "total_production": total_production,
            "total_defects": total_defects,
            "good_units": good_units,
            "defect_percentage": defect_percentage,
            "total_cost": total_cost,
            "machine_wise_production": machine_wise_production,
        }
        return summary

    except Exception as error:
        print(f"Error calculating dashboard summary: {error}")
        return {
            "total_production": 0,
            "total_defects": 0,
            "good_units": 0,
            "defect_percentage": 0.0,
            "total_cost": 0.0,
            "machine_wise_production": pd.DataFrame(),
        }
