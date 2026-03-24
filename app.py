from fpdf import FPDF
import streamlit as st
import requests
with st.sidebar:
    st.title("🛠️ AI Marketing Hub")
    st.info("This tool uses Llama 3.3 to generate high-converting copy in seconds.")
    st.markdown("---")
    st.subheader("Need a custom AI tool?")
    st.markdown("[📧 Contact the Developer](mailto:yourname@example.com)")
    st.markdown("---")
    st.write("🙏 If this helped you, consider supporting:")
    st.markdown("[☕ Buy me a coffee](https://www.buymeacoffee.com/)")
API_KEY = st.secrets["GROQ_API_KEY"]
def generate_content(business, choice):
    prompts = {
    "Instagram": f"""
You are an expert social media marketer.

Business Details:
{business}

Task:
Generate 3 high-converting Instagram captions.
- Use emojis
- Add strong call-to-action
- Make it engaging
- Keep Indian audience in mind
""",

    "WhatsApp": f"""
Write a WhatsApp promotional message for:
{business}

- Keep it friendly and short
- Add urgency
- Make it feel personal
""",

    "Email": f"""
Write a professional cold email for:
{business}

- Strong subject line
- Clear value proposition
- Persuasive CTA
""",

    "Ad Copy": f"""
Write a high-converting ad copy for:
{business}

- Attention-grabbing hook
- Problem + solution
- Strong CTA
"""
}
    }
    
    prompt = prompts.get(choice)
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are an elite Digital Marketing Strategist. Your copy is high-converting and punchy."
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

st.set_page_config(page_title="AI Marketing Pro")
st.title("🚀 AI Marketing Content Generator")

business_name = st.text_input("Business Name")
business_type = st.selectbox("Business Type", ["Gym", "Cafe", "Salon", "Clothing Store", "Other"])
target_audience = st.text_input("Target Audience")
tone = st.selectbox("Tone", ["Funny", "Professional", "Luxury", "Local Hinglish"])

business_description = f"""
Name: {business_name}
Type: {business_type}
Audience: {target_audience}
"""
content_type = st.selectbox("Type:", ["Instagram", "WhatsApp", "Email", "Ad Copy"])

if st.button("Generate ✨"):
    if not business_description:
        st.error("Enter a description!")
    else:
        with st.spinner("Writing..."):
            output = generate_content(business_description, content_type)
            st.markdown("---")
            st.write(output)
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                # Clean text to avoid encoding errors in PDF
                clean_text = output.encode('latin-1', 'ignore').decode('latin-1')
                pdf.multi_cell(0, 10, txt=clean_text)
                
                pdf_output = pdf.output(dest='S').encode('latin-1')
                
                st.download_button(
                    label="Download as PDF 📄",
                    data=pdf_output,
                    file_name="marketing_copy.pdf",
                    mime="application/pdf"
                )
            except Exception as pdf_err:
                st.warning("PDF could not be generated, but you can still copy the text above!")
## Final Reminder
