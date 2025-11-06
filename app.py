import streamlit as st
from dotenv import load_dotenv
import os
from models.text_generator import generate_presentation_content
from utils.slide_generator import create_presentation

# Load environment variables
load_dotenv()

st.set_page_config(page_title="🧠 AI Presentation Maker", layout="wide")

st.title("🧠 AI Presentation Maker — Text + Slide Layout Automation")
st.markdown("Generate a complete, editable PowerPoint presentation from just a single topic using **Groq + LLaMA** and **python-pptx**.")

# Sidebar
st.sidebar.header("⚙️ Settings")
num_slides = st.sidebar.slider("Number of slides", 3, 15, 6)
use_groq = st.sidebar.checkbox("Use Groq acceleration", value=True)
show_preview = st.sidebar.checkbox("Show slide preview", value=True)

# Input
topic = st.text_input("🎯 Enter your presentation topic:", placeholder="e.g., The Future of Artificial Intelligence in Healthcare")

if st.button("🚀 Generate Presentation"):
    if not topic.strip():
        st.warning("Please enter a topic before generating the presentation.")
    else:
        with st.spinner("🧠 Generating presentation content..."):
            slides = generate_presentation_content(topic, num_slides=num_slides, use_groq=use_groq)

        st.success("✅ Content generated successfully!")

        # Optional preview section
        if show_preview and slides:
            st.subheader("🖼️ Slide Preview")
            for i, slide in enumerate(slides):
                st.markdown(f"### 🪄 Slide {i+1}: {slide['title']}")
                for point in slide["points"]:
                    st.markdown(f"- {point}")
                st.markdown("---")

        # Generate and download PPTX
        with st.spinner("🎨 Creating PowerPoint file..."):
            output_path = create_presentation(topic, slides)

        st.success("🎉 Presentation created!")
        st.markdown(f"📥 [Download Presentation]({output_path})")

st.markdown("---")
st.caption("Built with ❤️ using Groq, LLaMA, python-pptx, and Streamlit.")
