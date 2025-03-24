import streamlit as st
import requests
import json
from datetime import datetime

# Configure the base URL for the Flask backend
BACKEND_URL = "http://localhost:5000"

def init_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None

def login_user(email, password):
    """Login user through the Flask backend."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.authenticated = True
            st.session_state.user_info = data['user']
            return True
        return False
    except Exception as e:
        st.error(f"Error during login: {str(e)}")
        return False

def register_user(email, password, name):
    """Register a new user through the Flask backend."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json={"email": email, "password": password, "name": name}
        )
        if response.status_code == 201:
            data = response.json()
            st.session_state.authenticated = True
            st.session_state.user_info = data['user']
            return True
        return False
    except Exception as e:
        st.error(f"Error during registration: {str(e)}")
        return False

def logout_user():
    """Logout the current user."""
    try:
        response = requests.post(f"{BACKEND_URL}/auth/logout")
        if response.status_code == 200:
            st.session_state.authenticated = False
            st.session_state.user_info = None
            return True
        return False
    except Exception as e:
        st.error(f"Error during logout: {str(e)}")
        return False

def upload_manuscript(file):
    """Upload a manuscript file."""
    try:
        files = {"file": file}
        response = requests.post(f"{BACKEND_URL}/manuscript/upload", files=files)
        return response.status_code == 200, response.json()
    except Exception as e:
        st.error(f"Error uploading manuscript: {str(e)}")
        return False, None

def get_manuscripts():
    """Get all manuscripts for the current user."""
    try:
        response = requests.get(f"{BACKEND_URL}/manuscript/manuscripts")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching manuscripts: {str(e)}")
        return []

def save_notes(file_name, notes):
    """Save notes for a manuscript."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/manuscript/save-notes",
            json={"file_name": file_name, "notes": notes}
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error saving notes: {str(e)}")
        return False

def get_manuscript_notes(file_name):
    """Get notes for a specific manuscript."""
    try:
        response = requests.get(f"{BACKEND_URL}/manuscript/notes/{file_name}")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching notes: {str(e)}")
        return []

def main():
    st.set_page_config(page_title="Manuscript Manager", layout="wide")
    init_session_state()

    # Sidebar for authentication
    with st.sidebar:
        if not st.session_state.authenticated:
            st.title("Login / Register")
            tab1, tab2 = st.tabs(["Login", "Register"])
            
            with tab1:
                with st.form("login_form"):
                    email = st.text_input("Email")
                    password = st.text_input("Password", type="password")
                    submit = st.form_submit_button("Login")
                    if submit:
                        if login_user(email, password):
                            st.success("Logged in successfully!")
                            st.rerun()
            
            with tab2:
                with st.form("register_form"):
                    name = st.text_input("Name")
                    email = st.text_input("Email")
                    password = st.text_input("Password", type="password")
                    submit = st.form_submit_button("Register")
                    if submit:
                        if register_user(email, password, name):
                            st.success("Registered successfully!")
                            st.rerun()
        else:
            st.title(f"Welcome, {st.session_state.user_info['name']}!")
            if st.button("Logout"):
                if logout_user():
                    st.success("Logged out successfully!")
                    st.rerun()

    # Main content
    if st.session_state.authenticated:
        st.title("Manuscript Manager")
        
        # File upload section
        st.header("Upload Manuscript")
        uploaded_file = st.file_uploader("Choose a file", type=['txt', 'pdf', 'doc', 'docx'])
        if uploaded_file:
            if st.button("Upload"):
                success, response = upload_manuscript(uploaded_file)
                if success:
                    st.success("File uploaded successfully!")
                else:
                    st.error("Error uploading file")

        # Manuscripts list
        st.header("Your Manuscripts")
        manuscripts = get_manuscripts()
        if manuscripts:
            selected_manuscript = st.selectbox(
                "Select a manuscript",
                options=[m['file_name'] for m in manuscripts]
            )
            
            if selected_manuscript:
                # Notes section
                st.subheader("Manuscript Notes")
                notes = get_manuscript_notes(selected_manuscript)
                
                # Display existing notes
                if notes:
                    for note in notes:
                        with st.expander(f"Note from {note['timestamp']}"):
                            st.write(note['assistant_response'])
                
                # Add new note
                new_note = st.text_area("Add a new note")
                if st.button("Save Note"):
                    if save_notes(selected_manuscript, new_note):
                        st.success("Note saved successfully!")
                        st.rerun()
        else:
            st.info("No manuscripts found. Upload one to get started!")

if __name__ == "__main__":
    main() 