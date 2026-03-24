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
    pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=output)
        
        # Create the download button
        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button(
            label="Download as PDF 📄",
            data=pdf_output,
            file_name="marketing_copy.pdf",
            mime="application/pdf"
        )
    st.markdown("[☕ Buy me a coffee](https://www.buymeacoffee.com/)")
API_KEY = st.secrets["GROQ_API_KEY"]
def generate_content(business, choice):
    prompts = {
        "Instagram": f"Generate 3 punchy Instagram captions with emojis for: {business}",
        "WhatsApp": f"Write a short, friendly WhatsApp promotional message for: {business}",
        "Email": f"Write a professional, high-converting cold email for: {business}",
        "Ad Copy": f"Write a catchy, persuasive advertisement copy for: {business}"
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

business_description = st.text_area("Describe your business:")
content_type = st.selectbox("Type:", ["Instagram", "WhatsApp", "Email", "Ad Copy"])

if st.button("Generate ✨"):
    if not business_description:
        st.error("Enter a description!")
    else:
        with st.spinner("Writing..."):
            output = generate_content(business_description, content_type)
            st.markdown("---")
            st.write(output)
