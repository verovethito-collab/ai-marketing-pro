from fpdf import FPDF
import streamlit as st
import requests
import datetime
from supabase import create_client

# Sidebar
with st.sidebar:
    st.title("🛠️ AI Marketing Hub")
    st.info("Generate high-converting marketing content in seconds.")

st.set_page_config(page_title="AI Marketing Pro", layout="centered")

# API + DB
API_KEY = st.secrets["GROQ_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- AUTH SYSTEM ----------------

auth_mode = st.sidebar.selectbox("Choose Mode", ["Login", "Sign Up"])

email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")

user = None

if auth_mode == "Sign Up":
    if st.sidebar.button("Create Account"):
        res = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        if res.user:
            st.sidebar.success("Account created! Please login.")
        else:
            st.sidebar.error("Signup failed")

elif auth_mode == "Login":
    if st.sidebar.button("Login"):
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if res.user:
            st.session_state["user"] = res.user
            st.sidebar.success("Logged in!")
        else:
            st.sidebar.error("Login failed")

# Keep session
if "user" in st.session_state:
    user = st.session_state["user"]

# Logout
if user:
    if st.sidebar.button("Logout"):
        st.session_state.pop("user")
        st.rerun()

# ---------------- UI ----------------

st.title("🚀 AI Marketing for Local Businesses")
st.caption("Get Instagram posts, WhatsApp promos & offers in seconds")
st.markdown("---")

st.subheader("💡 Example Output")
st.code("""
🔥 Get Fit This Summer at Iron Pulse Gym!

No more excuses 💪 Join now and transform your body with expert trainers.

Limited offer: 20% OFF for first 50 members!

📩 DM us today!
""")

if st.button("Try Demo"):
    st.session_state.business_name = "Iron Pulse Gym"
    st.session_state.target_audience = "Young professionals"

# Require login
if not user:
    st.warning("Please login to use the app")
    st.stop()

# Inputs
st.subheader("📌 Enter Business Details")

business_name = st.text_input("Business Name", value=st.session_state.get("business_name", ""))
business_type = st.selectbox(
    "Business Type",
    ["Gym", "Cafe", "Salon", "Clothing Store", "Restaurant", "Other"]
)
target_audience = st.text_input("Target Audience", value=st.session_state.get("target_audience", ""))
tone = st.selectbox(
    "Tone",
    ["Funny", "Professional", "Luxury", "Local Hinglish"]
)

content_type = st.selectbox(
    "Content Type",
    ["Instagram", "WhatsApp", "Email", "Ad Copy"]
)

business_description = f"""
Business Name: {business_name}
Business Type: {business_type}
Target Audience: {target_audience}
Tone: {tone}
"""

# ---------------- DB ----------------

def get_or_create_user(email):
    response = supabase.table("users").select("*").eq("email", email).execute()

    if response.data:
        return response.data[0]
    else:
        new_user = {
            "email": email,
            "usage_count": 0,
            "last_used": datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
        }
        insert = supabase.table("users").insert(new_user).execute()
        return insert.data[0]

# ---------------- AI ----------------

def generate_content(prompt):
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an elite Digital Marketing Strategist."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            },
            timeout=15
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

def build_prompt(business, content_type, tone):
    base = f"Business Details:\n{business}\n"

    if content_type == "Instagram":
        prompt = base + "Generate 3 engaging Instagram captions with emojis and CTA."
    elif content_type == "WhatsApp":
        prompt = base + "Write a short WhatsApp promo message with urgency."
    elif content_type == "Email":
        prompt = base + "Write a marketing email with subject and CTA."
    else:
        prompt = base + "Write a high-converting ad copy."

    if tone == "Local Hinglish":
        prompt += "\nUse Hinglish."

    return prompt

# ---------------- GENERATE ----------------

if st.button("Generate ✨"):
    if not business_name or not target_audience:
        st.error("Fill all fields")
    else:
        user_email = user.email
        user_data = get_or_create_user(user_email)

        usage = user_data["usage_count"]
        last_used = user_data.get("last_used")

        now = datetime.datetime.utcnow()

        if last_used:
            last_time = datetime.datetime.fromisoformat(last_used.replace("Z", ""))
        else:
            last_time = now

        time_diff = (now - last_time).total_seconds()

        if usage >= 3 and time_diff < 5 * 60 * 60:
            remaining = int((5 * 60 * 60 - time_diff) / 60)
            st.warning(f"Limit reached. Come back in {remaining} minutes.")
            st.stop()

        if time_diff >= 5 * 60 * 60:
            usage = 0

        with st.spinner("Generating..."):
            prompt = build_prompt(business_description, content_type, tone)
            output = generate_content(prompt)

            supabase.table("users").update({
                "usage_count": usage + 1,
                "last_used": now.replace(tzinfo=datetime.timezone.utc).isoformat()
            }).eq("email", user_email).execute()

            st.subheader("📢 Content")
            st.write(output)

            # PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            clean_text = output.encode('latin-1', 'ignore').decode('latin-1')
            pdf.multi_cell(0, 10, txt=clean_text)

            pdf_output = pdf.output(dest='S').encode('latin-1')

            st.download_button(
                "Download PDF",
                data=pdf_output,
                file_name="content.pdf",
                mime="application/pdf"
            )

st.markdown("---")
st.info("Free plan: 3 uses every 5 hours")
