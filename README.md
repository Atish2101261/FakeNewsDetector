# Fake News Detection

# Overview

The Fake News Detection System is a machine learning–based web application that predicts whether a given news article is real or fake. It uses TF-IDF vectorization and a Logistic Regression model to analyze news content and provide accurate predictions.

The system includes:

- A backend (fnd.py) for model training and evaluation
- A Streamlit-based frontend (ui.py) for user interaction
- User authentication (login/signup) for security
- URL-based text extraction for convenient analysis

# Features

- Machine learning–powered fake news classifier
- TF-IDF text representation and Logistic Regression model
- Interactive Streamlit UI
- Secure login and signup functionality
- Fake news detection via text input or news URL
- Trained model and vectorizer saved as pickle files
- Visual representation of prediction results
- Easy to deploy

# Technologies Used

- Language - Python 3.13
- Frontend - Streamlit
- Backend - ML Logistic Regression (Scikit-learn)
- Text Processing -	TF-IDF Vectorization
- Dataset Handling -	Pandas
- Data visualization - Matplotlib
- Model Saving -	Pickle
- Authentication -	Streamlit session state

# Dataset

The dataset consists of labeled news articles with text content and corresponding truth labels (Fake or True).
- Preprocessed to remove punctuation, stopwords, and special characters
- Transformed using TF-IDF vectorizer
- Split into training and testing sets (e.g., 80:20)

# Installation & Setup
1️⃣ Install Python - https://www.python.org/downloads/

Watch the video to install python with ease - https://www.youtube.com/watch?v=t2_Q2BRzeEE&list=PL0--sAWljl5LEzNyN5Z4zlorThiIUYEV_  (From 8:01)

Then, Check whether it is installed or not from command prompt by using the command - python --version

2️⃣ Install Libraries

Open Command prompt and run all the commands below one by one :-

pip install pandas

pip install numpy

pip install matplotlib

pip install sklearn

pip install streamlit

# How to run ?

Firstly, run the fnd.py file saperately and wait sometime 

After that open ui.py and open command prompt in terminal 

Run the Command- streamlit run ui.py

It will redirect in browser show the Streamlit based UI

# Usage Instructions

Sign Up / Log In to access the system

Navigate to the Fake News Detector page

Choose an input mode:

Paste news text directly

Or enter a URL of a news article

Click Predict

View the result — “✅ Real” or “❌ Fake” 

# Security Measures

- Passwords hashed before storage
- Session-based login/logout with st.session_state
- Input sanitization for text and URLs
- Restricted access to detection page unless logged in

# Contributors

Developer: Atish Patel

Project Type: Academic

Framework: Streamlit + Scikit-learn

# Note : Only The Hindu URL will work because maximum news websites block automated text extraction.
