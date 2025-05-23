# blog_app.py

import streamlit as st
import os
from dotenv import load_dotenv
import groq
import re

# Load API key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY is missing in .env file")
    st.stop()

# Set up Groq client
client = groq.Groq(api_key=GROQ_API_KEY)

st.title("📝 AI Blog Generator")

# Initialize session state
if 'titles' not in st.session_state:
    st.session_state.titles = []
if 'selected_title' not in st.session_state:
    st.session_state.selected_title = None
if 'blog_content' not in st.session_state:
    st.session_state.blog_content = ""

# Step 1: Get keyword input
keyword = st.text_input("Enter a blog topic (keyword):")

# Step 2: Generate titles
if st.button("Generate Titles"):
    if not keyword.strip():
        st.warning("Please enter a topic.")
    else:
        with st.spinner("Thinking..."):
            prompt = f"""
Generate 4 blog title options about "{keyword}".
Return ONLY a numbered list:
1. Include keyword in first 3 words
2. Max 60 characters
3. Use power words like 'Essential', 'Definitive Guide', etc.
"""
            try:
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-8b-8192",
                    temperature=0.7,
                    max_tokens=300
                )

                content = response.choices[0].message.content.strip()
                lines = [line.strip() for line in content.split("\n") if re.match(r"\d+\.\s", line.strip())]
                titles = [re.sub(r"^\d+\.\s*", "", line) for line in lines]
                st.session_state.titles = titles
                st.session_state.selected_title = None
                st.session_state.blog_content = ""

            except Exception as e:
                st.error(f"Error: {e}")

# Step 3: Show radio buttons for selection
if st.session_state.titles:
    st.subheader("📚 Choose a Title")
    selected = st.radio("Pick one title:", st.session_state.titles)
    st.session_state.selected_title = selected

# Step 4: Generate full blog post
if st.session_state.selected_title and not st.session_state.blog_content:
    if st.button("Generate Blog Post"):
        with st.spinner("Writing full blog post..."):
            blog_prompt = f"""
Write a detailed blog post titled "{st.session_state.selected_title}".
Use markdown structure:
# Title
## Introduction
## Main Content (3-5 sections)
### Subsections
## Conclusion
Use practical examples and data where possible.
Length: approx 1500 words.
"""
            try:
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": blog_prompt}],
                    model="llama3-8b-8192",
                    temperature=0.8,
                    max_tokens=3000
                )

                blog = response.choices[0].message.content.strip()
                st.session_state.blog_content = blog

            except Exception as e:
                st.error(f"Error generating blog: {e}")

# Step 5: Show blog content
if st.session_state.blog_content:
    st.subheader("📝 Blog Content")
    st.markdown(st.session_state.blog_content)

    st.download_button(
        label="📥 Download Blog as Markdown",
        data=st.session_state.blog_content,
        file_name=f"{st.session_state.selected_title}.md"
    )

# Step 6: Reset
if st.button("🔄 Reset"):
    st.session_state.titles = []
    st.session_state.selected_title = None
    st.session_state.blog_content = ""
    st.rerun()
