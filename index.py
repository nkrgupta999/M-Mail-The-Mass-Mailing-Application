import streamlit as st
import pymysql
from dashboard import dashboard

# Connect to MySQL Database
def create_connection():
    return pymysql.connect(
        host='localhost',
        user='<Enter Your MySQL Username>',
        password='<Enter Your Password Here>',
        database='login_system'
    )

def create_users_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50),
            username VARCHAR(50) UNIQUE,
            password VARCHAR(100)
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# Signup functionality
def signup_user(username, name, password):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, name, password) VALUES (%s, %s, %s)", (username, name, password))
        conn.commit()
        st.success("You have successfully signed up!")
    except pymysql.err.IntegrityError:
        st.error("Username already exists.")
    finally:
        cursor.close()
        conn.close()

# Login functionality
def login_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# Main app function
def main():
    # Initialize session state for page navigation
    create_connection()
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        # If the user is not logged in, show login/signup page
        st.title("Welcome to the Mass Mailing App \n Login/Signup")

        menu = ["Login", "Signup"]
        choice = st.selectbox("Menu", menu)

        # Signup Functionality
        if choice == "Signup":
            st.subheader("Create a new account")
            name = st.text_input("Enter your Name")
            username = st.text_input("Enter your Username")
            password = st.text_input("Enter Your Password", type='password')
            confirm_password = st.text_input("Enter your Confirm Password", type='password')
            
            if st.button("Signup"):
                if password == confirm_password:
                    signup_user(username, name, password)
                else:
                    st.error("Passwords do not match")

        # Login Funcitionality
        elif choice == "Login":
            st.subheader("Login to your account")
            username = st.text_input("Username")
            password = st.text_input("Password", type='password')
            
            if st.button("Login"):
                user = login_user(username, password)
                
                # After successful login, update session state and trigger rerun
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.name = user[2]  # Store user's name in session state
                    st.experimental_set_query_params(logged_in="true")  # Set query params to indicate logged in
                else:
                    st.error("Invalid username or password")
    else:
        # If the user is logged in, show the dashboard page
        st.sidebar.title(f"Welcome {st.session_state.name}!")  # Display user's name in the sidebar
        dashboard()  # Show the dashboard after login

# Run the app
if __name__ == '__main__':
    create_users_table()
    main()