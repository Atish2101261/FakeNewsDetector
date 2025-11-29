# Libraries
import streamlit as st
import pandas as pd
import pickle
import hashlib
import os
import base64
import newspaper
from newspaper import Article

# Password saving
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    if os.path.exists("users.csv") and os.path.getsize("users.csv") > 0:
        users = pd.read_csv("users.csv")
        if username in users["username"].values:
            stored_password = users[users["username"] == username]["password"].values[0]
            return hash_password(password) == stored_password
    return False

def register_user(username, password):
    if os.path.exists("users.csv") and os.path.getsize("users.csv") > 0:
        users = pd.read_csv("users.csv")
        if username in users["username"].values:
            return False
    else:
        users = pd.DataFrame(columns=["username", "password"])

    new_user = pd.DataFrame([[username, hash_password(password)]], columns=["username", "password"])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv("users.csv", index=False)
    return True

# Url Fetching
def fetch_article_text(url):
    try:
        config = newspaper.Config()
        config.browser_user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
        config.request_timeout = 10
        article = Article(url, config=config)
        article.download()
        article.parse()
        return article.text.strip()
    except Exception as e:
        return f"ERROR::{e}"

# Load Model
LRmodel = pickle.load(open("LRmodel.pkl", "rb"))
vectorization = pickle.load(open("vectorization.pkl", "rb"))

# Session State
if "page" not in st.session_state:
    st.session_state.page = "home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""

# Backgrond and Styles
def set_bg_from_local(image_file):
    if not os.path.exists(image_file):
        return
    with open(image_file, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}
        .main > div {{
            background-color: rgba(0, 0, 0, 0.55);
            padding: 2rem;
            border-radius: 15px;
            backdrop-filter: blur(5px);
        }}
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {{
            color: white !important;
        }}
        input[type="text"],
        input[type="password"],
        textarea {{
            color: black !important;
            background-color: rgba(255,255,255,0.9) !important;
            border: 1px solid #ccc !important;
        }}
        .stButton > button {{
            color: white !important;
            background-color: rgba(0, 0, 0, 0.6);
            border: 1px solid white;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg_from_local("breaknews.jpg")

# Pages
def home_page():
    st.title("JanchPadtaal App")
    st.markdown("Choose an option to continue:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Login"):
            st.session_state.page = "login"
            st.rerun()
        if st.button("📰 JanchPadtaal"):
            if st.session_state.logged_in:
                st.session_state.page = "JanchPadtaal"
                st.rerun()
            else:
                st.warning("Please login first.")
    with col2:
        if st.button("📝 Sign Up"):
            st.session_state.page = "signup"
            st.rerun()
        if st.button("📖 About"):
            st.session_state.page = "about"
            st.rerun()

def login_page():
    st.title("🔐 Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if verify_user(username, password):
            st.success(f"Welcome back, {username}!")
            st.session_state.logged_in = True
            st.session_state.user = username
            st.session_state.page = "JanchPadtaal"
            st.rerun()
        else:
            st.error("Invalid username or password.")
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "home"
        st.rerun()

def signup_page():
    st.title("📝 Create New Account")
    new_user = st.text_input("Create username")
    new_pass = st.text_input("Create password", type="password")
    if st.button("Sign Up"):
        if register_user(new_user, new_pass):
            st.success("Account created successfully! Please login.")
        else:
            st.error("Username already exists.")
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "home"
        st.rerun()

def JanchPadtaal_page():
    if not st.session_state.logged_in:
        st.warning("Please login to access the Fake News Detector.")
        if st.button("⬅️ Back to Home"):
            st.session_state.page = "home"
            st.rerun()
        return

    st.title("JanchPadtaal")
    st.subheader(f"Welcome, {st.session_state.user} 👋")

    input_text = st.text_area("📝 Paste your news article text here:")
    st.markdown("**OR**")
    input_url = st.text_input("🌐 Enter a news article URL:")

    if st.button("Predict"):
        if input_text.strip():
            vec = vectorization.transform([input_text])
            prediction = LRmodel.predict(vec)[0]
            if prediction == "REAL":
                st.success("✅ This news article is REAL.")
            else:
                st.error("🚨 This news article is FAKE.")
        elif input_url.strip():
            article_text = fetch_article_text(input_url)
            if article_text.startswith("ERROR::"):
                st.error("❌ Error fetching article: " + article_text.replace("ERROR::", ""))
            elif article_text == "":
                st.warning("⚠️ Couldn't extract text from the URL.")
            else:
                vec = vectorization.transform([article_text])
                prediction = LRmodel.predict(vec)[0]
                if prediction == "REAL":
                    st.success("✅ The news article in this URL is REAL.")
                else:
                    st.error("🚨 The news article in this URL is FAKE.")
        else:
            st.warning("Please enter article text or a valid URL.")

    if st.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.session_state.user = ""
        st.session_state.page = "home"
        st.rerun()

def about_page():
    st.title("📖 About JanchPadtaal App")
    st.markdown("""
    This application uses a **Machine Learning model (Logistic Regression with TF-IDF vectorization)** 
    to predict whether a news article is **FAKE** or **REAL**.

    **Features**:
    - Text and URL-based article input
    - Secure Login and Signup
    - Local background image
    - Built using Streamlit and Scikit-learn

    **Developers**: Ayush Kumar Tiwary  
    **Accuracy**: ~98.69%
    """)
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "home"
        st.rerun()

# Routings
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "login":
    login_page()
elif st.session_state.page == "signup":
    signup_page()
elif st.session_state.page == "JanchPadtaal":
    JanchPadtaal_page()
elif st.session_state.page == "about":
    about_page()
