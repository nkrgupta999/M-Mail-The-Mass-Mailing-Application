import streamlit as st

def show_log_details():
    # Read the log file and display its content
    try:
        with open("activity_log.txt", "r") as log_file:
            log_content = log_file.read()
            if log_content:
                st.text_area("Log Details", log_content, height=400)
            else:
                st.info("No log details available.")
    except FileNotFoundError:
        st.warning("Log file not found.")
