import logging

# Configure logging
logging.basicConfig(
    filename="activity_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Simulated database for emails (replace this with your actual database)
email_db = []  # This will serve as our email storage

# Simulated database functions with logging
def save_email_to_db(email):
    # Simulate saving email to a database
    email_db.append(email)
    logging.info(f"Email saved to database: {email}")

def fetch_emails_from_db():
    # Simulate fetching emails from a database
    logging.info("Fetched emails from the database.")
    return [{'id': idx, 'email': email} for idx, email in enumerate(email_db)]

def delete_email_from_db(email_id):
    # Simulate deleting an email from the database
    if 0 <= email_id < len(email_db):
        deleted_email = email_db[email_id]
        del email_db[email_id]
        logging.info(f"Email with ID {email_id} and address {deleted_email} deleted from database.")
    else:
        logging.warning(f"Attempted to delete email with invalid ID: {email_id}")

def update_email_in_db(email_id, new_email):
    # Simulate updating an email in the database
    if 0 <= email_id < len(email_db):
        old_email = email_db[email_id]
        email_db[email_id] = new_email
        logging.info(f"Email with ID {email_id} updated from {old_email} to {new_email} in the database.")
    else:
        logging.warning(f"Attempted to update email with invalid ID: {email_id}")

def clear_email_db():
    # Clear the email database after sending emails
    email_db.clear()
    logging.info("Cleared all emails from the database.")
