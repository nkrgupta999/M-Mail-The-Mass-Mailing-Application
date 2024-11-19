import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import base64
import logging
import schedule
import time
import threading
from click import option
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Google import Create_Service
from Outlookemail import sendOutlook
from gmail_template import gmail_template
from outlook_template import outlook_template
from dbfunction import save_email_to_db
from dbfunction import fetch_emails_from_db
from dbfunction import delete_email_from_db
from dbfunction import update_email_in_db
from dbfunction import clear_email_db
from showlog import show_log_details


#Configuration of logging
logging.basicConfig(
    filename='activity_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constants for Gmail API
CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']

# Create the Gmail service
service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

# Initialize an empty list to hold statistics data
stats_data = []

# Function to determine delivery area based on email sending status
def determine_delivery_area(status):
    return "Inbox" if status else "Failed"

def send_email_gmail(receiver_email, subject, message_body):
    emailMsg = message_body  # Use the input message body
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = receiver_email
    mimeMessage['subject'] = subject
    mimeMessage.attach(MIMEText(emailMsg, 'plain'))
    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()

    try:
        # Sending the email
        message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
        logging.info(f"Gmail: Email sent successfully to {receiver_email}")  # Log email sent action
        return True
    except Exception as e:
        logging.error(f"Gmail: Failed to send email to {receiver_email}: {e}")  # Log error
        st.error(f"An error occurred while sending email to {receiver_email}: {e}")
        return False

def view_statistics():
    # Convert stats_data into a DataFrame for display
    if stats_data:
        # Convert the list of stats into a DataFrame
        stats_df = pd.DataFrame(stats_data)
        
        # Display the dataframe
        st.dataframe(stats_df)

        # 1. Pie Chart for Delivery Status (Delivered vs Failed)
        st.subheader("Delivery Status Distribution")
        delivery_status_count = stats_df["Delivery Status"].value_counts()
        
        # Plot Pie chart
        fig_pie = plt.figure(figsize=(6, 6))
        plt.pie(delivery_status_count, labels=delivery_status_count.index, autopct='%1.1f%%', startangle=90, colors=["#76b041", "#d9534f"])
        plt.title("Delivery Status: Delivered vs Failed")
        st.pyplot(fig_pie)
        
        # 2. Bar Chart for Email Count by Mailing Service (Gmail vs Outlook)
        st.subheader("Email Count by Mailing Service")
        mailing_service_count = stats_df["Mailing Service"].value_counts()

        # Plot Bar chart using Plotly
        fig_bar = px.bar(mailing_service_count, x=mailing_service_count.index, y=mailing_service_count.values, 
                         labels={'x': 'Mailing Service', 'y': 'Count'},
                         title="Number of Emails Sent by Mailing Service")
        st.plotly_chart(fig_bar)

    else:
        st.warning("No statistics available.")

#log Viewer
def view_logs():
    st.subheader("Activity Log")
    try:
        with open("activity_log.txt", "r") as file:
            logs = file.readlines()
            st.text_area("Activity Log Details", value="".join(logs), height=300)
    except FileNotFoundError:
        st.warning("No logs available.")

# Function to schedule email sending
def schedule_email(receiver_email, subject, message_body, send_time, mailing_service):
    def job():
        if mailing_service == "Gmail":
            status = send_email_gmail(receiver_email, subject, message_body)
            delivery_area = determine_delivery_area(status)
            stats_data.append({
                "Email ID": receiver_email,
                "Mailing Service": "Gmail",
                "Delivery Status": "Delivered" if status else "Failed",
                "Delivery Area": delivery_area
            })
            st.success(f"Scheduled email sent to {receiver_email} via Gmail.")
        elif mailing_service == "Outlook":
            sendOutlook(receiver_email, subject, message_body)
            delivery_area = "Inbox"  # Assuming delivery to Inbox for simplicity
            stats_data.append({
                "Email ID": receiver_email,
                "Mailing Service": "Outlook",
                "Delivery Status": "Delivered",
                "Delivery Area": delivery_area
            })
            st.success(f"Scheduled email sent to {receiver_email} via Outlook.")
        logging.info(f"Scheduled email sent to {receiver_email} at {send_time}")

    schedule.every().day.at(send_time).do(job)  # Schedule the job for the specified time
    st.info(f"Email scheduled to be sent at {send_time} to {receiver_email}.")

# Function to run scheduled jobs in the background
def run_scheduled_jobs():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the scheduler in a separate thread
threading.Thread(target=run_scheduled_jobs, daemon=True).start()

#Flow of entire dashboard Interface
def dashboard():
    global stats_data  # Access the global statistics data

    # Sidebar for logout button
    st.sidebar.title("Menu / Navigation")

    # Add the Logout button at the bottom of the sidebar
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.experimental_set_query_params(logged_in="false")
        logging.info("User logged out.")  # Log logout action

    st.title("Mass Mailing Application Dashboard")
    if st.sidebar.button("Log Details"):
        show_log_details()  # Call the function to show log details

    st.header("Choose Your Mailing Service")

    # Option to choose between Gmail and Outlook
    option = st.radio("Select your mailing service", ('Gmail', 'Outlook'))

    if option == 'Gmail':
        st.subheader("You selected Gmail")
        st.info("Proceed with Gmail API integration for mass mailing.")

    elif option == 'Outlook':
        st.subheader("You selected Outlook")
        st.info("Proceed with Outlook API integration for mass mailing.")

    # Add both buttons to use templates, regardless of the mailing service chosen
    if st.sidebar.button("Use Gmail Template"):
        gmail_template()  # Call the Gmail template function
        logging.info("Gmail template used.")  # Log template selection

    if st.sidebar.button("Use Outlook Template"):
        outlook_template()  # Call the Outlook template function
        logging.info("Outlook template used.")  # Log template selection

    # Email sending form
    st.header("Compose Email")

    # Input area for receiver email address (single email or multiple from CSV)
    receiver_email = st.text_input("Receiver Email (single email or multiple from CSV)")

    # Option to upload a .csv file with email addresses
    csv_file = st.file_uploader("Or upload a .csv file with receiver emails and Contact numbers", type=['csv'])

    # Display the contents of the uploaded .csv file (if any)
    if csv_file is not None:
        emails_df = pd.read_csv(csv_file)
        st.write("Emails found in the CSV file:")
        st.dataframe(emails_df)

        # Save emails to the database and display with checkboxes
        for email in emails_df['email']:
            save_email_to_db(email)  # Function to save email to the database
        st.success("Emails have been saved to the database.")

    # Inputs for email content
    subject = st.text_input("Email Subject")
    message_body = st.text_area("E-mail Message Body", height=200)

    # Button to send the email immediately
    if st.button("Send Email"):
        if option == 'Gmail':
            if csv_file is not None and 'email' in emails_df.columns:
                emails_list = emails_df['email'].tolist()  # Assuming 'email' is the column name in the CSV
                for email in emails_list:
                    status = send_email_gmail(email, subject, message_body)  # Function to send email via Gmail
                    delivery_area = determine_delivery_area(status)  # Function to determine delivery area
                    stats_data.append({
                        "Email ID": email,
                        "Mailing Service": "Gmail",
                        "Delivery Status": "Delivered" if status else "Failed",
                        "Delivery Area": delivery_area
                    })
                st.success(f"Sending emails to {len(emails_list)} recipients via Gmail.")
                clear_email_db()  # Clear the simulated database
            elif receiver_email:
                status = send_email_gmail(receiver_email, subject, message_body)
                delivery_area = determine_delivery_area(status)
                stats_data.append({
                    "Email ID": receiver_email,
                    "Mailing Service": "Gmail",
                    "Delivery Status": "Delivered" if status else "Failed",
                    "Delivery Area": delivery_area
                })
                st.success(f"Sending email to {receiver_email} via Gmail.")
                clear_email_db()  # Clear the simulated database
            else:
                st.error("Please provide a receiver email or upload a .csv file.")

        elif option == 'Outlook':
            if csv_file is not None and 'email' in emails_df.columns:
                emails_list = emails_df['email'].tolist()  # Assuming 'email' is the column name in the CSV
                for email in emails_list:
                    sendOutlook(email, subject, message_body)  # Function to send email via Outlook
                    delivery_area = "Inbox"  # Assuming delivery to Inbox for simplicity
                    stats_data.append({
                        "Email ID": email,
                        "Mailing Service": "Outlook",
                        "Delivery Status": "Delivered",
                        "Delivery Area": delivery_area
                    })
                st.success(f"Sending emails to {len(emails_list)} recipients via Outlook.")
                clear_email_db()  # Clear the simulated database

            elif receiver_email:
                sendOutlook(receiver_email, subject, message_body)
                delivery_area = "Inbox"
                stats_data.append({
                    "Email ID": receiver_email,
                    "Mailing Service": "Outlook",
                    "Delivery Status": "Delivered",
                    "Delivery Area": delivery_area
                })
                st.success(f"Sending email to {receiver_email} via Outlook.")
                clear_email_db()  # Clear the simulated database

    # Add Email Scheduling Section
    st.header("Schedule an Email")

    # Inputs for scheduling email
    schedule_receiver_email = st.text_input("Receiver Email for Scheduling")
    schedule_subject = st.text_input("Scheduled Email Subject")
    schedule_message_body = st.text_area("Scheduled Email Message Body", height=200)
    schedule_time = st.text_input("Schedule Time (HH:MM in 24-hour format)")

    # Button to schedule the email
    if st.button("Schedule Email"):
        if option == "Gmail":
            schedule_email(schedule_receiver_email, schedule_subject, schedule_message_body, schedule_time, "Gmail")
        elif option == "Outlook":
            schedule_email(schedule_receiver_email, schedule_subject, schedule_message_body, schedule_time, "Outlook")

    # Button to view statistics
    if st.sidebar.button("View Statistics"):
        st.session_state.stats_data = stats_data  # Save stats data in session state
        view_statistics()  # Function to view statistics
        logging.info("User viewed statistics.")  # Log statistics view


# Run the app
if __name__ == "__main__":
    dashboard()
