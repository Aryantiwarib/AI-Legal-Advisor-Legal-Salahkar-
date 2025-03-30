import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase
from datetime import datetime

# Initialize Firebase Admin SDK
app_name = "my_chat"
if app_name not in firebase_admin._apps:
    cred = credentials.Certificate("C:/Users/Aryan/Downloads/advocatesinfo-b5650-firebase-adminsdk-ga6bm-fd0e9ebd73.json")
    firebase_admin.initialize_app(cred, name=app_name)
db = firestore.client(firebase_admin.get_app(app_name))


st.set_page_config(
    page_icon=r"C:\Users\Aryan\OneDrive\Desktop\Ai Tools(Projects)\CLIMAVOX__4_-removebg-preview.png", 
)


# Firebase Configuration
firebase_config = {
    "apiKey": "AIzaSyCagJjYVOyVCqvmXyUy-ri8GFkanxhx6EI",
    "authDomain": "advocatesinfo-b5650.firebaseapp.com",
    "projectId": "advocatesinfo-b5650",
    "storageBucket": "advocatesinfo-b5650.appspot.com",
    "messagingSenderId": "1034270615048",
    "appId": "1:1034270615048:web:efd45920dd7f1bec4d93bd",
    "measurementId": "G-Z5079VL3L4",
    "databaseURL": "https://advocatesinfo-b5650.firebaseio.com"
}

# Initialize Firebase with Pyrebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# Authentication Functions
def login_user(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        # Update user status to online
        db.collection('users').document(user['localId']).set({
            'email': email,
            'status': 'online',
            'last_login': datetime.now()
        }, merge=True)
        return user
    except Exception as e:
        st.error(f"Error: {str("Enter correct email or password(Password should be at least six character)!")}")
        return None

def signup_user(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        auth.send_email_verification(user['idToken'])  # Send verification email
        # Add user to Firestore with initial status
        db.collection('users').document(user['localId']).set({
            'email': email,
            'status': 'offline',
            'last_login': None
        })
        return user
    except Exception as e:
        st.error(f"Error: {str("Enter correct email or password(Password should be at least six character)!")}")
        return None

def update_user_status(user_id, status):
    db.collection('users').document(user_id).update({
        'status': status,
        'last_login': datetime.now()
    })

# Streamlit UI
st.title("Personal Chat Website")

if 'user' not in st.session_state:
    st.session_state.user = None

menu = ["Login", "SignUp"]
if st.session_state.user is None:
    choice = st.sidebar.selectbox("Menu", menu)
else:
    st.sidebar.write(f"Logged in as: {st.session_state.user['email']}")
    if st.sidebar.button("Logout"):
        update_user_status(st.session_state.user['localId'], 'offline')
        st.session_state.user = None
        st.success("Logged out successfully!")
        st.experimental_rerun()

if st.session_state.user is None:
    if choice == "SignUp":
        st.subheader("Create an Account")
        email = st.text_input("Email")
        password = st.text_input("Password", type='password')
        if st.button("Sign Up"):
            user = signup_user(email, password)
            if user:
                st.success("Account created successfully! Please check your email to verify your account.")
                st.info("Go to the login menu to log in after verification.")
    elif choice == "Login":
        st.subheader("Login to your Account")
        email = st.text_input("Email")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            user = login_user(email, password)
            if user:
                account_info = auth.get_account_info(user['idToken'])
                if account_info['users'][0]['emailVerified']:
                    st.session_state.user = user
                    st.success("Logged in successfully!")
                    st.experimental_rerun()
                else:
                    st.error("Email not verified. Please verify your email before logging in.")
else:
    # Chat Section
    st.subheader("Chat Section")

    users_ref = db.collection('users')
    user_id = st.session_state.user['localId']

    # Fetch all users except the current user
    users = users_ref.stream()
    user_list = [doc.to_dict()['email'] for doc in users if doc.id != user_id]
    chat_with = st.selectbox("Select User to Chat With", user_list)

    recipient_user_id = None  # Initialize recipient_user_id

    if chat_with:
        if "message_input" not in st.session_state:
            st.session_state.message_input = ""

        message = st.text_area("Enter your message:", value=st.session_state.message_input, key="message_input")

        if st.button("Send"):
            if message :
                try:
                    # Get the recipient's user ID
                    recipient_ref = users_ref.where("email", "==", chat_with).limit(1).stream()
                    for doc in recipient_ref:
                        recipient_user_id = doc.id
                    
                    if recipient_user_id:
                        chat_data = {
                            'from_email': st.session_state.user['email'],
                            'to_email': chat_with,
                            'message': message,
                            'timestamp': datetime.now()
                        }
                        # Save the message under both users' chat collections
                        db.collection(f'chats/{user_id}/{recipient_user_id}').add(chat_data)
                        db.collection(f'chats/{recipient_user_id}/{user_id}').add(chat_data)
                        st.success("Message sent!")
                        # Clear the input field indirectly by rerunning the app
                        st.session_state.message_input = ""  # Reset the message input state
                        st.experimental_rerun()  # Rerun to reset the widget state
                    else:
                        st.error("Failed to find the recipient user.")
                except Exception as e:
                    st.success(f"Personal chat with advocates")
            else:
                st.warning("Message cannot be empty.")

        # Display chat history
        if recipient_user_id:
            chats_ref = db.collection(f'chats/{user_id}/{recipient_user_id}').order_by('timestamp')
            chats = chats_ref.stream()

            st.write("Chat History:")
            for chat in chats:
                chat_data = chat.to_dict()
                sender_email = chat_data['from_email']
                if sender_email == st.session_state.user['email']:
                    # Your message on the left in a green box
                    st.markdown(f"""
                        <div style='text-align: left; background-color:  rgb(90 154 106); padding: 10px; border-radius: 10px; margin-bottom: 25px; width: 60%;'>
                            <strong>Your Message:</strong><br>{chat_data['message']}
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    # Recipient's message on the right in a black box
                    st.markdown(f"""
                        <div style='text-align: right; background-color: #343a40; color: white; padding: 10px; border-radius: 10px; margin-bottom: 5px; margin-top:24px; width: 60%; float: right;'>
                            <strong>{sender_email.split('@')[0]}:</strong><br>{chat_data['message']}
                        </div>
                    """, unsafe_allow_html=True)

            # Clear float
            st.markdown("<div style='clear: both;'></div>", unsafe_allow_html=True)
