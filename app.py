import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
import os

# ---------- Helpers ----------
def make_hash(password: str) -> str:
    return hashlib.sha256(str(password).encode()).hexdigest()

def check_password(password: str, hashed: str) -> bool:
    return make_hash(password) == hashed

USERS_CSV = "users.csv"
POSTS_CSV = "posts.csv"

def load_users():
    if os.path.exists(USERS_CSV):
        return pd.read_csv(USERS_CSV)
    return pd.DataFrame(columns=["Full Name","Email","Phone","Password","Public Name","Country","State","District","Pin Code","Area"])

def save_users(df):
    df.to_csv(USERS_CSV, index=False)

def load_posts():
    if os.path.exists(POSTS_CSV):
        return pd.read_csv(POSTS_CSV)
    return pd.DataFrame(columns=["Author","Content","Image","Pin","Area","Timestamp"])

def save_posts(df):
    df.to_csv(POSTS_CSV, index=False)

# ---------- Sample posts builder ----------
def make_sample_posts(pin, area):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sample = [
        {
            "Author": "PoliceDept",
            "Content": """A major road accident took place early this morning in Powai near Murarji Nagar. 
According to eyewitnesses, a speeding truck lost control and rammed into several vehicles, causing a massive pile-up on the highway. 
Fire brigade and local police immediately reached the spot to control the situation and provide medical assistance. Several people sustained injuries 
and traffic movement was severely disrupted for hours. Authorities have urged residents to avoid this route until clearance work is completed.""",
            "Image": "images/accident.png",
            "Pin": pin,
            "Area": area,
            "Timestamp": now
        },
        {
            "Author": "TrafficDept",
            "Content": """Heavy traffic congestion has been reported near Sakinaka in the Jari Mari area due to ongoing repair works and continuous rainfall. 
The narrow lanes, combined with double-parked vehicles, made movement extremely difficult for commuters during peak hours. Public transport, 
including buses and rickshaws, was affected, leading to delays in office travel. Authorities have deployed traffic police to manage the situation, 
but commuters are advised to take alternative routes until the situation improves.""",
            "Image": "images/traffic.png",
            "Pin": pin,
            "Area": area,
            "Timestamp": now
        },
        {
            "Author": "BMC",
            "Content": """A fire broke out this afternoon in a residential tower located in Filter Pada, Powai. Thick black smoke was seen billowing from the upper floors, 
causing panic among residents. Fire tenders rushed to the spot and immediately began evacuation efforts. Fortunately, no casualties have been reported so far, 
though several people were treated for smoke inhalation. The cause of the fire is still under investigation, but initial reports suggest an electrical short circuit.""",
            "Image": "images/fire.png",
            "Pin": pin,
            "Area": area,
            "Timestamp": now
        },
        {
            "Author": "CommunityGroup",
            "Content": """In a positive development, residents of Jari Mari organized a community cleanliness and safety drive in collaboration with local NGOs and civic bodies. 
The initiative saw over 200 volunteers coming together to clean streets, remove garbage, and set up awareness camps on sanitation and waste management. Local leaders 
highlighted the importance of maintaining hygiene and safety in densely populated areas. The event concluded with a pledge by residents to continue such efforts regularly.""",
            "Image": "",
            "Pin": pin,
            "Area": area,
            "Timestamp": now
        }
    ]
    return pd.DataFrame(sample)

# ---------- Page setup ----------
st.set_page_config(page_title="Hyperlocal News App", layout="wide")
st.title("📰 Hyperlocal News & Safety App")

# ---------- Session state ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user_email" not in st.session_state:
    st.session_state.current_user_email = None

# Load data
users = load_users()
posts = load_posts()

# ---------- Auth UI ----------
if not st.session_state.logged_in:
    choice = st.sidebar.selectbox("Menu", ["Login", "Sign Up"])
    if choice == "Sign Up":
        st.subheader("Create New Account")
        full_name = st.text_input("Full Name", key="su_fullname")
        phone = st.text_input("Phone Number", key="su_phone")
        email = st.text_input("Email", key="su_email")
        password = st.text_input("Password", type="password", key="su_password")
        if st.button("Sign Up"):
            if email in users["Email"].values:
                st.error("Email already registered! Please login.")
            elif not email or not password or not full_name:
                st.error("Please fill Full Name, Email and Password.")
            else:
                new_user = {
                    "Full Name": full_name,
                    "Email": email,
                    "Phone": phone,
                    "Password": make_hash(password),
                    "Public Name": "",
                    "Country": "",
                    "State": "",
                    "District": "",
                    "Pin Code": "",
                    "Area": ""
                }
                users = pd.concat([users, pd.DataFrame([new_user])], ignore_index=True)
                save_users(users)
                st.success("Account created! Proceed to profile setup.")
                # set session to logged in new user and rerun
                st.session_state.logged_in = True
                st.session_state.current_user_email = email
                st.rerun()

    else:  # Login
        st.subheader("Login to Your Account")
        email = st.text_input("Email", key="li_email")
        password = st.text_input("Password", type="password", key="li_password")
        if st.button("Login"):
            if email in users["Email"].values:
                user_row = users.loc[users["Email"] == email].iloc[0]
                if check_password(password, user_row["Password"]):
                    st.session_state.logged_in = True
                    st.session_state.current_user_email = email
                    st.success(f"Welcome {user_row['Full Name']}!")
                    st.rerun()
                else:
                    st.error("Invalid password!")
            else:
                st.error("User not found! Please sign up.")

# ---------- After login flow ----------
if st.session_state.logged_in and st.session_state.current_user_email:
    # reload to ensure latest data on disk is read
    users = load_users()
    posts = load_posts()
    user = users.loc[users["Email"] == st.session_state.current_user_email].iloc[0]

    # If public profile not set, force profile setup
    if pd.isna(user["Public Name"]) or user["Public Name"] == "":
        st.warning("Complete your public profile setup first.")
        public_name = st.text_input("Public Display Name", key="pf_public_name")
        country = st.selectbox("Country", ["India"], key="pf_country")
        state = st.selectbox("State", ["Maharashtra"], key="pf_state")
        district = st.selectbox("District", ["Mumbai Suburban"], key="pf_district")
        pin = st.selectbox("Pin Code", ["400072", "400087"], key="pf_pin")
        if pin == "400072":
            area = st.selectbox("Area", ["Jari Mari", "Safed Pool"], key="pf_area")
        else:
            area = st.selectbox("Area", ["Powai", "Filter Pada", "Murarji Nagar"], key="pf_area")

        if st.button("Save Profile"):
            users.loc[users["Email"] == st.session_state.current_user_email, ["Public Name","Country","State","District","Pin Code","Area"]] = \
                [public_name, country, state, district, pin, area]
            save_users(users)

            # add sample posts for this pin+area if none exist
            existing = posts[(posts["Pin"] == pin) & (posts["Area"] == area)]
            if existing.empty:
                sample_df = make_sample_posts(pin, area)
                posts = pd.concat([posts, sample_df], ignore_index=True)
                save_posts(posts)

            st.success("Profile setup completed. Redirecting to Home Feed...")
            st.rerun()

    else:
        st.markdown("### 🏠 Home Feed")
        user_pin = user["Pin Code"]
        user_area = user["Area"]
        # show posts filtered by pin and area
        filtered = posts[(posts["Pin"] == user_pin) & (posts["Area"] == user_area)]
        if filtered.empty:
            st.info("No posts in your area yet.")
        else:
            for i, row in filtered.iterrows():
                st.markdown(f"**{row['Author']}** ({row['Timestamp']})")
                st.write(row["Content"])
                img = str(row["Image"]) if pd.notna(row["Image"]) else ""
                if img and img.strip() != "":
                    try:
                        st.image(img, width=400)
                    except Exception as e:
                        st.write("(Image not available)")
                st.markdown("---")

        # Add New Post
        st.subheader("✍️ Add New Post")
        content = st.text_area("Post Content", key="new_content")
        image_url = st.text_input("Image URL or relative path (optional)", key="new_image")
        tags = st.text_input("Tags (optional)", key="new_tags")
        if st.button("Post"):
            new_post = {
                "Author": users.loc[users["Email"] == st.session_state.current_user_email, "Public Name"].values[0],
                "Content": content,
                "Image": image_url,
                "Pin": user_pin,
                "Area": user_area,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            posts = pd.concat([posts, pd.DataFrame([new_post])], ignore_index=True)
            save_posts(posts)
            st.success("Post added successfully!")
            st.rerun()

        # Logout
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.current_user_email = None
            st.rerun()
