import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime

# -------------------------
# Utility Functions
# -------------------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password, hashed):
    return hash_password(password) == hashed

# -------------------------
# Page Config
# -------------------------
st.set_page_config(page_title="My Hood News", layout="wide")
st.title("📰 My Hood News")

# -------------------------
# Initialize Session State
# -------------------------
if "users" not in st.session_state:
    st.session_state["users"] = pd.DataFrame(columns=["Full Name", "Email", "Password", "Location"])
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
if "posts" not in st.session_state:
    st.session_state["posts"] = []

# -------------------------
# Authentication Functions
# -------------------------
def signup():
    st.subheader("Create Account")
    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    location = st.text_input("Location")

    if st.button("Sign Up"):
        if email in list(st.session_state["users"]["Email"]):
            st.error("Email already exists. Please login.")
        else:
            new_user = pd.DataFrame([[full_name, email, hash_password(password), location]], columns=st.session_state["users"].columns)
            st.session_state["users"] = pd.concat([st.session_state["users"], new_user], ignore_index=True)
            st.success("Account created! Please login.")
            st.experimental_rerun()

def login():
    st.subheader("Login to Your Account")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_row = st.session_state["users"][st.session_state["users"]["Email"] == email]
        if not user_row.empty and check_password(password, user_row["Password"].values[0]):
            st.session_state["current_user"] = user_row.iloc[0].to_dict()
            st.success(f"Welcome {st.session_state['current_user']['Full Name']}!")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials.")

# -------------------------
# Post Functionality
# -------------------------
def add_sample_posts():
    st.session_state["posts"] = [
        {
            "Author": "PoliceDept",
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Content": "A major road accident took place early this morning in Powai near Murarji Nagar. According to eyewitnesses, a speeding truck lost control and rammed into several vehicles, causing a massive pile-up on the highway. Fire brigade and local police immediately reached the spot to control the situation and provide medical assistance.",
            "Image": "accident in powai.png",
        },
        {
            "Author": "TrafficDept",
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Content": "Heavy traffic congestion reported in Jari Mari near Sakinaka. Vehicles are moving slowly due to ongoing drainage work and narrow lanes. Commuters are advised to avoid this route and take alternatives.",
            "Image": "jarimari traffic.png",
        },
        {
            "Author": "FireDept",
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Content": "A fire broke out in a residential building at Safed Pool, Kurla. Smoke was seen billowing from the 7th floor. Fire tenders rushed to the spot and the fire was brought under control after an hour-long operation. No casualties have been reported so far.",
            "Image": "powai fire broke out.png",
        },
        {
            "Author": "BMC",
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Content": "Water supply maintenance scheduled today in Jari Mari. Residents are advised to store water in advance as there may be interruptions during the day. The BMC assures that normal supply will resume by evening.",
            "Image": None,
        },
    ]

def home_feed():
    st.header("🏠 Home Feed")
    if not st.session_state["posts"]:
        add_sample_posts()
    for post in st.session_state["posts"]:
        st.subheader(f"{post['Author']} ({post['Time']})")
        st.write(post["Content"])
        if post["Image"]:
            try:
                st.image(post["Image"], width=400)
            except:
                st.warning("(Image not available)")
        st.markdown("---")

# -------------------------
# Main App Flow
# -------------------------
def main():
    menu = ["Login", "Sign Up", "Home Feed"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        if st.session_state["current_user"]:
            st.success(f"Already logged in as {st.session_state['current_user']['Full Name']}")
            home_feed()
        else:
            login()

    elif choice == "Sign Up":
        signup()

    elif choice == "Home Feed":
        if st.session_state["current_user"]:
            home_feed()
        else:
            st.warning("Please login first.")

if __name__ == "__main__":
    main()
