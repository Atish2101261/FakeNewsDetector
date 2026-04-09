# Libraries
import streamlit as st
import pandas as pd
import pickle
import hashlib
import os
import base64
import newspaper
from newspaper import Article
import nltk
try:
    nltk.download('punkt')
    nltk.download('punkt_tab')
except:
    pass

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

# Load Models
LRmodel = pickle.load(open("LRmodel.pkl", "rb"))
vectorization = pickle.load(open("vectorization.pkl", "rb"))

# Load Subject Models (New)
SubjectModel = pickle.load(open("SubjectModel.pkl", "rb"))
SubjectVectorizer = pickle.load(open("SubjectVectorizer.pkl", "rb"))

# Session State
if "page" not in st.session_state:
    st.session_state.page = "home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""

# Backgrond and Styles
def inject_premium_css():
    image_file = "premium_news_bg.png"
    if os.path.exists(image_file):
        with open(image_file, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
            bg_css = f'background-image: url("data:image/png;base64,{encoded}");'
    else:
        bg_css = 'background: linear-gradient(135deg, #020617, #0f172a, #1eccd1);'

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Playfair+Display:wght@700;900&display=swap');

        :root {{
            --primary: #6366f1;
            --secondary: #a855f7;
            --accent: #f43f5e;
            --sidebar-bg: rgba(2, 6, 23, 0.98);
            --glass-bg: rgba(15, 23, 42, 0.88);
            --glass-border: rgba(255, 255, 255, 0.15);
            --neon-glow: 0 0 20px rgba(99, 102, 241, 0.5);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }}

        .stApp {{
            {bg_css}
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            font-family: 'Outfit', sans-serif;
            color: var(--text-main);
        }}

        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background: var(--sidebar-bg) !important;
            border-right: 1px solid var(--glass-border);
            backdrop-filter: blur(25px);
        }}

        [data-testid="stSidebar"] .stMarkdown h1 {{
            font-family: 'Playfair Display', serif !important;
            font-size: 1.5rem !important;
            background: linear-gradient(to right, #ffffff, #6366f1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            white-space: nowrap;
            margin-bottom: 2rem !important;
        }}

        /* Navigation Radio styling */
        .stRadio label {{
            color: var(--text-main) !important;
            font-weight: 500 !important;
            font-size: 1rem !important;
            padding: 0.5rem 0 !important;
        }}

        /* Header & Padding Fixes */
        header {{
            visibility: hidden;
            height: 0px !important;
        }}

        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0) !important;
        }}

        /* Main Container */
        .main .block-container {{
            background: var(--glass-bg);
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            padding: 2.5rem !important;
            margin-top: 0rem !important;
            margin-bottom: 1rem;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
            max-width: 1000px !important;
        }}

        /* Typography */
        h1, h2, h3, h4 {{
            font-family: 'Playfair Display', serif !important;
            letter-spacing: -0.5px;
            color: var(--text-main) !important;
            text-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }}

        .premium-header {{
            background: linear-gradient(135deg, #ffffff, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem !important;
            font-weight: 900 !important;
            margin-bottom: 0.5rem !important;
            text-shadow: none !important;
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.5));
        }}

        .verdict-banner {{
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            font-weight: 600;
            margin: 1.5rem 0;
            font-size: 1.2rem;
            border: 1px solid rgba(255,255,255,0.1);
        }}

        p, label, .stMarkdown, .stInfo, .stCaption {{
            color: var(--text-main) !important;
            font-weight: 400;
        }}
        .stButton > button {{
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid var(--glass-border) !important;
            color: white !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .stButton > button:hover {{
            background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
            border-color: transparent !important;
            transform: scale(1.02);
            box-shadow: var(--neon-glow);
        }}

        /* Animated Progress Bars */
        .stProgress > div > div > div > div {{
            background-image: linear-gradient(to right, var(--primary), var(--secondary)) !important;
        }}

        /* Result Cards */
        .insight-card {{
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 1.5rem;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            height: 100%;
            min-height: 160px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .insight-card:hover {{
            transform: translateY(-5px);
            border-color: var(--primary);
            background: rgba(15, 23, 42, 0.8);
            box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
        }}

        .insight-card h2, .insight-card h3 {{
            color: white !important;
            text-shadow: 0 2px 5px rgba(0,0,0,0.5);
            margin-top: 0 !important;
        }}

        .insight-card p {{
            color: #cbd5e1 !important;
            font-size: 1.1rem;
            line-height: 1.6;
        }}

        /* Scanning Animation */
        @keyframes scan {{
            0% {{ background-position: 0% 0%; }}
            100% {{ background-position: 0% 100%; }}
        }}
        .scanning-effect {{
            background: linear-gradient(transparent, rgba(99, 102, 241, 0.1), transparent);
            background-size: 100% 200%;
            animation: scan 2s linear infinite;
        }}

        /* Footer */
        .footer-text {{
            text-align: center;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            opacity: 0.4;
            margin-top: 4rem;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

inject_premium_css()

# Pages
def home_page():
    st.markdown("<h1 class='premium-header'>Welcome to FakeNewsDetector</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.2rem; opacity: 0.8;'>Easy-to-use AI tool to verify news articles and identify misinformation.</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🚀 How to Get Started")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class='insight-card'>
            <h4>🔐 1. Access System</h4>
            <p style='font-size: 0.9rem; margin: 0;'>Securely login to your account to unlock our advanced analysis engines.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class='insight-card'>
            <h4>📝 2. Input Content</h4>
            <p style='font-size: 0.9rem; margin: 0;'>Paste any news article text or link directly into our smart analysis field.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class='insight-card' style='border-color: var(--primary);'>
            <h4>📊 3. View Results</h4>
            <p style='font-size: 0.9rem; margin: 0;'>Get a clear verdict on the truth, topic, and confidence score in seconds.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        if st.button("Log In to Start Analysis"):
            st.session_state.page = "login"
            st.rerun()
    else:
        if st.button("Go to Analysis Dashboard"):
            st.session_state.page = "FakeNewsDetector"
            st.rerun()

    st.markdown("<p class='footer-text'>Verification Protocol // Version 4.0</p>", unsafe_allow_html=True)

def login_page():
    st.markdown("## 🔐 Login")
    with st.container():
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        st.markdown("<div style='margin-top: 1rem;'>", unsafe_allow_html=True)
        if st.button("Access Dashboard"):
            if verify_user(username, password):
                st.success(f"Welcome back, {username}!")
                st.session_state.logged_in = True
                st.session_state.user = username
                st.session_state.page = "FakeNewsDetector"
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    if st.button("⬅️ Back to Home", key="back_login"):
        st.session_state.page = "home"
        st.rerun()

def signup_page():
    st.markdown("## 📝 Create Account")
    with st.container():
        new_user = st.text_input("Username", placeholder="Choose a username")
        new_pass = st.text_input("Password", type="password", placeholder="Choose a strong password")
        
        st.markdown("<div style='margin-top: 1rem;'>", unsafe_allow_html=True)
        if st.button("Register"):
            if register_user(new_user, new_pass):
                st.success("Registration successful! You can now log in.")
            else:
                st.error("Username already taken.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    if st.button("⬅️ Back to Home", key="back_signup"):
        st.session_state.page = "home"
        st.rerun()

def FakeNewsDetector_page():
    if not st.session_state.logged_in:
        st.warning("Please login to access the analysis tools.")
        return

    st.markdown("<h2 class='premium-header'>News Analysis Tool</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='opacity: 0.8;'>Welcome back, <b>{st.session_state.user}</b>! What would you like to verify today?</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📄 Verify Text", "🌐 Verify URL"])

    with tab1:
        # Example Buttons
        st.markdown("**Try an example:**")
        ex1, ex2 = st.columns(2)
        with ex1:
            if st.button("📝 Try Real News Example"):
                st.session_state.input_val = "NASA's Perseverance rover has successfully collected its first rock sample from the surface of Mars, marking a major milestone in the search for ancient life on the Red Planet."
        with ex2:
            if st.button("🚨 Try Fake News Example"):
                st.session_state.input_val = "SHOCKING: Scientists discover that Mars is actually a hollow shell used by ancient civilizations to hide from the sun. NASA has been covering this up for decades!"

        input_text = st.text_area("Paste news article text:", height=180, 
                                 value=st.session_state.get("input_val", ""),
                                 placeholder="Paste the news text you want to check...")
        
        if st.button("Start Analysis", key="analyze_text_btn"):
            if input_text.strip():
                with st.spinner("Our AI is analyzing the news patterns..."):
                    # Truth Prediction with Proba
                    vec_truth = vectorization.transform([input_text])
                    prob_truth = LRmodel.predict_proba(vec_truth)[0]
                    prediction_truth = "REAL" if prob_truth[1] > prob_truth[0] else "FAKE"
                    conf_truth = max(prob_truth) * 100
                    
                    # Topic Prediction with Proba
                    vec_topic = SubjectVectorizer.transform([input_text])
                    prob_topic = SubjectModel.predict_proba(vec_topic)[0]
                    prediction_topic = SubjectModel.classes_[prob_topic.argmax()]
                    conf_topic = max(prob_topic) * 100
                    
                    # Verdict Banner
                    if prediction_truth == "REAL":
                        st.balloons()
                        v_color = "rgba(16, 185, 129, 0.2)"
                        v_border = "#10b981"
                        v_text = "Highly Credible: This article appears to be Real News."
                    else:
                        v_color = "rgba(239, 68, 68, 0.2)"
                        v_border = "#ef4444"
                        v_text = "Warning: This article shows patterns of Misinformation."

                    st.markdown(f"<div class='verdict-banner' style='background: {v_color}; border-color: {v_border};'>{v_text}</div>", unsafe_allow_html=True)

                    st.markdown("### Analysis Details")
                    c1, c2 = st.columns(2)
                    
                    with c1:
                        st.markdown(f"""
                        <div class='insight-card'>
                            <p style='margin:0; font-size: 0.8rem; opacity: 0.6;'>TOPIC FOUND</p>
                            <h3 style='margin: 0.5rem 0; color: white !important;'>{prediction_topic.upper()}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        st.progress(conf_topic / 100)
                        st.caption(f"Topic Confidence: {conf_topic:.1f}%")
                        
                    with c2:
                        color = "#10b981" if prediction_truth == "REAL" else "#ef4444"
                        st.markdown(f"""
                        <div class='insight-card' style='border-color: {color};'>
                            <p style='margin:0; font-size: 0.8rem; opacity: 0.6;'>TRUTH RATING</p>
                            <h3 style='margin: 0.5rem 0; color: {color} !important;'>{prediction_truth}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        st.progress(conf_truth / 100)
                        st.caption(f"Reliability Score: {conf_truth:.1f}%")
            else:
                st.warning("Please enter some text to analyze.")

    with tab2:
        input_url = st.text_input("Data Source URL:", placeholder="https://news-archive.com/source-entry")
        if st.button("FETCH & SCAN", key="analyze_url_btn"):
            if input_url.strip():
                with st.spinner("ESTABLISHING DATA CONNECTION..."):
                    article_text = fetch_article_text(input_url)
                    if article_text.startswith("ERROR::"):
                        st.error(f"SYSTEM ERROR: {article_text.replace('ERROR::', '')}")
                    elif article_text == "":
                        st.warning("DATA GAP: NO READABLE CONTENT RETRIEVED.")
                    else:
                        # Truth Prediction with Proba
                        vec_truth = vectorization.transform([article_text])
                        prob_truth = LRmodel.predict_proba(vec_truth)[0]
                        prediction_truth = "REAL" if prob_truth[1] > prob_truth[0] else "FAKE"
                        conf_truth = max(prob_truth) * 100
                        
                        # Topic Prediction with Proba
                        vec_topic = SubjectVectorizer.transform([article_text])
                        prob_topic = SubjectModel.predict_proba(vec_topic)[0]
                        prediction_topic = SubjectModel.classes_[prob_topic.argmax()]
                        conf_topic = max(prob_topic) * 100
                        
                        # Display Results
                        st.markdown("### REMOTE ANALYSIS INSIGHTS")
                        c1, c2 = st.columns(2)
                        
                        with c1:
                            st.markdown(f"""
                            <div class='insight-card'>
                                <p style='margin:0; font-size: 0.8rem; opacity: 0.6; text-transform: uppercase;'>TOPIC CLASSIFIED</p>
                                <h3 style='margin: 0.5rem 0; color: white !important;'>{prediction_topic.upper()}</h3>
                            </div>
                            """, unsafe_allow_html=True)
                            st.progress(conf_topic / 100)
                            st.caption(f"Topic Confidence: {conf_topic:.1f}%")
                            
                        with c2:
                            color = "#10b981" if prediction_truth == "REAL" else "#ef4444"
                            icon = "VALID" if prediction_truth == "REAL" else "ANOMALY"
                            
                            if prediction_truth == "REAL": st.balloons()
                            
                            st.markdown(f"""
                            <div class='insight-card' style='border-color: {color};'>
                                <p style='margin:0; font-size: 0.8rem; opacity: 0.6; text-transform: uppercase;'>VERIFICATION STATUS</p>
                                <h3 style='margin: 0.5rem 0; color: {color} !important;'>{icon} DETECTED</h3>
                            </div>
                            """, unsafe_allow_html=True)
                            st.progress(conf_truth / 100)
                            st.caption(f"Truth Confidence: {conf_truth:.1f}%")
            else:
                st.warning("PROMPT: VALID URL SOURCE REQUIRED.")

def about_page():
    st.markdown("<h2 class='premium-header'>SYSTEM LOGS & ARCHITECTURE</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='insight-card'>
        <h3>Neural Architecture</h3>
        <p>The system utilizes a multi-layer analysis approach, combining linguistic feature extraction with statistical classification models.</p>
        
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 2rem;'>
            <div>
                <p style='opacity: 0.6; font-size: 0.7rem;'>TRUTH SENSITIVITY</p>
                <h2 style='color: var(--primary) !important;'>98.69%</h2>
            </div>
            <div>
                <p style='opacity: 0.6; font-size: 0.7rem;'>TOPIC PRECISION</p>
                <h2 style='color: var(--secondary) !important;'>81.40%</h2>
            </div>
        </div>
    </div>
    <br>
    """, unsafe_allow_html=True)
    
    cols = st.columns(2)
    with cols[0]:
        st.markdown("### Technology Stack")
        st.code("""
Python 3.14
Streamlit Pro
Scikit-learn
TF-IDF Vectorization
        """)
    with cols[1]:
        st.markdown("### Core Modules")
        st.info("Logistic Regression Engine")
        st.info("Neural Topic Identifier")
        st.info("URL Data Extractor")

# Sidebar Navigation
with st.sidebar:
    st.markdown("# Fake News Detector")
    st.markdown("---")
    
    # Page Mapping for Synchronization
    if st.session_state.logged_in:
        nav_options = ["Home", "Analyze News", "About System", "Logout"]
        page_to_idx = {"home": 0, "FakeNewsDetector": 1, "about": 2}
    else:
        nav_options = ["Home", "Login", "Sign Up", "About System"]
        page_to_idx = {"home": 0, "login": 1, "signup": 2, "about": 3}
    
    # Get current index based on session state
    current_idx = page_to_idx.get(st.session_state.page, 0)
    
    choice = st.radio("MAIN MENU", nav_options, index=current_idx)
    
    # Handle Navigation from Sidebar
    if choice == "Home": st.session_state.page = "home"
    elif choice == "Login": st.session_state.page = "login"
    elif choice == "Sign Up": st.session_state.page = "signup"
    elif choice == "Analyze News": st.session_state.page = "FakeNewsDetector"
    elif "About" in choice: st.session_state.page = "about"
    elif choice == "Logout":
        st.session_state.logged_in = False
        st.session_state.user = ""
        st.session_state.page = "home"
        st.rerun()

# Routing Logic
if st.session_state.page == "home": home_page()
elif st.session_state.page == "login": login_page()
elif st.session_state.page == "signup": signup_page()
elif st.session_state.page == "FakeNewsDetector": FakeNewsDetector_page()
elif st.session_state.page == "about": about_page()
