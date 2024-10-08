import streamlit as st
import requests
import pandas as pd

API_URL = 'http://localhost:8000/transactions/'

def upload_file():
    """Upload the transaction CSV file to Django."""
    st.title("Transaction Processor")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        if st.button('Upload'):
            # Send the file to the Django API
            response = requests.post(f"{API_URL}upload/", files={'file': uploaded_file})
            if response.status_code == 200:
                st.success("File uploaded successfully!")
                st.write(response.json())  # Show bad transactions if any
            else:
                st.error("File upload failed")


def show_reports():
    """Show various reports generated by Django."""
    st.title("Reports")

    if st.button('Show Chart of Accounts'):
        chart = requests.get(f"{API_URL}chart/")
        st.write(pd.DataFrame(chart.json()))

    if st.button('Show Collections'):
        collections = requests.get(f"{API_URL}collections/")
        st.write(pd.DataFrame(collections.json()))

    if st.button('Show Bad Transactions'):
        bad_transactions = requests.get(f"{API_URL}bad_transactions/")
        st.write(pd.DataFrame(bad_transactions.json()))


def reset_system():
    """Reset the system and clear all cached data."""
    if st.button('Reset System'):
        response = requests.get(f"{API_URL}reset/")
        if response.status_code == 200:
            st.success("System reset successfully!")
        else:
            st.error("System reset failed")


upload_file()
show_reports()
reset_system()