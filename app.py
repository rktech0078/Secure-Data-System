import streamlit as st
import hashlib
from cryptography.fernet import Fernet
import base64
import json
import os

# Page config
st.set_page_config(
    page_title="Secure Data System",
    page_icon="🛡️",
    layout="wide"
)

# Initialize session state variables
if 'stored_data' not in st.session_state:
    st.session_state.stored_data = {}

if 'failed_attempts' not in st.session_state:
    st.session_state.failed_attempts = 0

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = True

if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

if 'key' not in st.session_state:
    # Generate key for encryption
    st.session_state.key = Fernet.generate_key()
    st.session_state.cipher_suite = Fernet(st.session_state.key)

# Function to hash the passkey
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

# Function to encrypt data
def encrypt_data(text, passkey):
    combined_key = hashlib.sha256((passkey + st.session_state.key.decode()).encode()).digest()
    cipher = Fernet(base64.urlsafe_b64encode(combined_key[:32]))
    return cipher.encrypt(text.encode()).decode()

# Function to decrypt data
def decrypt_data(encrypted_text, passkey):
    try:
        combined_key = hashlib.sha256((passkey + st.session_state.key.decode()).encode()).digest()
        cipher = Fernet(base64.urlsafe_b64encode(combined_key[:32]))
        return cipher.decrypt(encrypted_text.encode()).decode()
    except Exception:
        return None

# Function to save data to a JSON file with indentation
def save_data_to_file():
    serializable_data = {}
    for user_id, data in st.session_state.stored_data.items():
        serializable_data[user_id] = {
            "encrypted_text": data["encrypted_text"],
            "passkey": data["passkey"]
        }
    
    with open("encrypted_data.json", "w") as f:
        json.dump(serializable_data, f, indent=4)

# Function to load data from a JSON file
def load_data_from_file():
    if os.path.exists("encrypted_data.json"):
        with open("encrypted_data.json", "r") as f:
            st.session_state.stored_data = json.load(f)

# Try to load data at startup
try:
    load_data_from_file()
except Exception:
    st.session_state.stored_data = {}

# Function to navigate to pages
def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

# Sidebar navigation - common to all pages
def sidebar_navigation():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2885/2885417.png", width=100)
        st.title("Navigation")
        
        # Add unique key to radio to fix error
        page = st.radio(
            "Select a page:",
            ["Home", "Store Data", "Retrieve Data"],
            key="navigation"
        )
        
        # Show stats
        st.markdown("---")
        st.subheader("System Stats")
        st.write(f"Data Entries: {len(st.session_state.stored_data)}")
        
        # Show failed attempts if any
        if st.session_state.failed_attempts > 0:
            st.warning(f"Failed attempts: {st.session_state.failed_attempts}/3")
        
        # Logout button
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()
        
        # Return selected page
        return page

# Login Page
def login_page():
    st.title("🔒 Secure Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("##### Please enter your credentials")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True):
            if username and password:
                st.session_state.authenticated = True
                st.session_state.failed_attempts = 0
                st.session_state.current_page = "home"
                st.rerun()
            else:
                st.error("Invalid username or password.")

# Home Page
def home_page():
    selected_page = sidebar_navigation()
    
    # Handle navigation from sidebar
    if selected_page != "Home":
        st.session_state.current_page = selected_page.lower().replace(" ", "_")
        st.rerun()
    
    # Main content
    st.title("🛡️ Secure Data Encryption System")
    
    st.markdown("""
    ## Welcome to Your Secure Data Vault
    
    This application helps you safely store and retrieve sensitive information 
    using strong encryption. Your data is protected with a personal passkey 
    that only you know.
    
    ### Key Features:
    - 🔐 **Strong Encryption**: All data is securely encrypted
    - 🔑 **Passkey Protection**: Your unique passkey ensures only you can access your data
    - 🛑 **Security Measures**: Three failed attempts will lock the system
    - 💾 **Data Persistence**: Your encrypted data is saved between sessions
    """)
    
    # Quick action buttons
    # st.markdown("### Quick Actions")
    # col1, col2 = st.columns(2)
    
    # with col1:
    #     if st.button("Store New Data", use_container_width=True):
    #         st.session_state.current_page = "store_data"
    #         st.rerun()
    
    # with col2:
    #     if st.button("Retrieve Data", use_container_width=True):
    #         st.session_state.current_page = "retrieve_data"
    #         st.rerun()

# Insert Data Page
def store_data_page():
    selected_page = sidebar_navigation()
    
    # Handle navigation from sidebar
    if selected_page != "Store Data":
        st.session_state.current_page = selected_page.lower().replace(" ", "_")
        st.rerun()
    
    # Main content
    st.title("📝 Store New Data")
    st.markdown("Enter your data and a passkey to securely store it.")
    
    # Form layout
    user_id = st.text_input("User ID (will be used to retrieve your data)")
    text_data = st.text_area("Enter the data you want to encrypt", height=150)
    
    col1, col2 = st.columns(2)
    with col1:
        passkey = st.text_input("Create a passkey", type="password")
    with col2:
        confirm_passkey = st.text_input("Confirm passkey", type="password")
    
    st.info("Make sure to remember your passkey. It cannot be recovered if lost!")
    
    # Store button
    if st.button("Store Data Securely", use_container_width=True):
        if not user_id or not text_data or not passkey:
            st.error("All fields are required.")
        elif passkey != confirm_passkey:
            st.error("Passkeys do not match.")
        else:
            hashed_passkey = hash_passkey(passkey)
            encrypted_text = encrypt_data(text_data, passkey)
            
            st.session_state.stored_data[user_id] = {
                "encrypted_text": encrypted_text,
                "passkey": hashed_passkey
            }
            
            save_data_to_file()
            st.success("Data stored successfully!")
            st.balloons()

# Retrieve Data Page
def retrieve_data_page():
    selected_page = sidebar_navigation()
    
    # Handle navigation from sidebar
    if selected_page != "Retrieve Data":
        st.session_state.current_page = selected_page.lower().replace(" ", "_")
        st.rerun()
    
    # Main content
    st.title("🔍 Retrieve Data")
    st.markdown("Enter your User ID and passkey to retrieve your data.")
    
    # Form layout
    col1, col2 = st.columns(2)
    with col1:
        user_id = st.text_input("User ID")
    with col2:
        passkey = st.text_input("Enter your passkey", type="password")
    
    # Retrieve button
    if st.button("Retrieve Data", use_container_width=True):
        if not user_id or not passkey:
            st.error("Both User ID and passkey are required.")
        elif user_id not in st.session_state.stored_data:
            st.error("User ID not found.")
            st.session_state.failed_attempts += 1
        else:
            stored_passkey = st.session_state.stored_data[user_id]["passkey"]
            
            if hash_passkey(passkey) == stored_passkey:
                encrypted_text = st.session_state.stored_data[user_id]["encrypted_text"]
                decrypted_text = decrypt_data(encrypted_text, passkey)
                
                if decrypted_text:
                    st.success("Data retrieved successfully!")
                    
                    # Display the decrypted data
                    with st.expander("Your Decrypted Data", expanded=True):
                        st.code(decrypted_text)
                    
                    st.session_state.failed_attempts = 0
                else:
                    st.error("Failed to decrypt data. Passkey might be incorrect.")
                    st.session_state.failed_attempts += 1
            else:
                st.error("Incorrect passkey.")
                st.session_state.failed_attempts += 1
        
        if st.session_state.failed_attempts >= 3:
            st.error(f"You've exceeded the maximum number of attempts ({st.session_state.failed_attempts}).")
            st.warning("Please login again for security reasons.")
            st.session_state.authenticated = False
            st.rerun()

# Main app logic
if not st.session_state.authenticated:
    login_page()
else:
    if st.session_state.current_page == "home":
        home_page()
    elif st.session_state.current_page == "store_data":
        store_data_page()
    elif st.session_state.current_page == "retrieve_data":
        retrieve_data_page()