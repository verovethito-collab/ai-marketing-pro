from fpdf import FPDF
import streamlit as st
import requests
import datetime
from supabase import create_client

with st.sidebar:
    st.title("🛠️ AI Marketing Hub")
    st.info("Generate high-converting marketing content in seconds.")

st.set_page_config(page_title="AI Marketing Pro", layout="centered")

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

API_KEY = st.secrets["GROQ_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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

st.markdown("---")
user_email = st.text_input("Enter your email (required)")

def get_or_create_user(email):
    response = supabase.table("users").select("*").eq("email", email).execute()

    if response.data:
        return response.data[0]
    else:
        new_user = {
            "email": email,
            "usage_count": 0
        }
        insert = supabase.table("users").insert(new_user).execute()
        return insert.data[0]

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
                        "content": "You are an elite Digital Marketing Strategist. Your copy is high-converting, engaging, and persuasive."
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
    base = f"""
Business Details:
{business}
"""

    if content_type == "Instagram":
        prompt = base + """
Generate 3 high-converting Instagram captions:
- Use emojis
- Add strong call-to-action
- Make it engaging and trendy
- Keep Indian audience in mind
"""

    elif content_type == "WhatsApp":
        prompt = base + """
Write a short WhatsApp promotional message:
- Friendly and personal tone
- Create urgency
- Add CTA
"""

    elif content_type == "Email":
        prompt = base + """
Write a professional marketing email:
- Include subject line
- Clear value proposition
- Persuasive CTA
"""

    elif content_type == "Ad Copy":
        prompt = base + """
Write a high-converting advertisement:
- Strong hook
- Problem + solution
- Emotional trigger
- Clear CTA
"""

    if tone == "Local Hinglish":
        prompt += "\nUse Hinglish (mix Hindi + English) naturally."

    return prompt

if st.button("Generate ✨"):
    if not business_name or not target_audience:
        st.error("Please fill all required fields!")
    elif not user_email:
        st.error("Email is required!")
    else:
        user = get_or_create_user(user_email)

        usage = user["usage_count"]
        last_used = user["last_used"]

        now = datetime.datetime.utcnow()
        last_time = datetime.datetime.fromisoformat(last_used.replace("Z", ""))

        time_diff = (now - last_time).total_seconds()

        if usage >= 3 and time_diff < 5 * 60 * 60:
            remaining = int((5 * 60 * 60 - time_diff) / 60)
            st.warning(f"🚀 Limit reached! Come back in {remaining} minutes.")
            st.stop()

        if time_diff >= 5 * 60 * 60:
            usage = 0

        with st.spinner("Generating content..."):
            prompt = build_prompt(business_description, content_type, tone)
            output = generate_content(prompt)

            supabase.table("users").update({
                "usage_count": usage + 1,
                "last_used": now.isoformat()
            }).eq("email", user_email).execute()

            st.markdown("---")
            st.subheader("📢 Generated Content")
            st.write(output)

            st.subheader("🔥 Promotional Offer Ideas")

            offer_prompt = f"""
Business Details:
{business_description}

Generate 3 creative limited-time offers for this business.
Make them catchy and realistic for Indian customers.
"""

            offers = generate_content(offer_prompt)
            st.write(offers)

            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)

                clean_text = (output + "\n\nOFFERS:\n" + offers).encode('latin-1', 'ignore').decode('latin-1')
                pdf.multi_cell(0, 10, txt=clean_text)

                pdf_output = pdf.output(dest='S').encode('latin-1')

                st.download_button(
                    label="Download as PDF 📄",
                    data=pdf_output,
                    file_name="marketing_content.pdf",
                    mime="application/pdf"
                )
            except:
                st.warning("PDF generation failed, but content is available above!")

st.markdown("---")
st.info("You can generate up to 3 times every 5 hours.")
