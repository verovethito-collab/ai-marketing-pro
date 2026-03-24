from fpdf import FPDF
import streamlit as st
import requests
import time

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
user_email = st.text_input("Enter your email (optional)")

if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0

if "last_reset" not in st.session_state:
    st.session_state.last_reset = time.time()

current_time = time.time()
elapsed_time = current_time - st.session_state.last_reset

if elapsed_time > 5 * 60 * 60:
    st.session_state.usage_count = 0
    st.session_state.last_reset = current_time

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

if st.session_state.usage_count >= 3:
    remaining = int((5 * 60 * 60 - elapsed_time) / 60)
    st.warning(f"🚀 Limit reached! Come back in {remaining} minutes to generate more content.")
    st.stop()

if st.button("Generate ✨"):
    if not business_name or not target_audience:
        st.error("Please fill all required fields!")
    else:
        if user_email:
            with open("leads.txt", "a") as f:
                f.write(user_email + "\n")

        with st.spinner("Generating content..."):
            prompt = build_prompt(business_description, content_type, tone)
            output = generate_content(prompt)

            st.session_state.usage_count += 1

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
