import streamlit as st
import json
import os
import time
import base64
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Import necessary classes and local modules ---
try:
    from crewai import CrewOutput 
    from agents import create_spec_crew 
    from models import Specification
except ImportError as e:
    st.error(f"Module Import Error: {e}. Please ensure you ran 'pip install crewai litellm' and check file names.")
    st.stop()


# --- Helper Function for Download Link (PDF Alternative) ---
def get_markdown_download_link(markdown_text, filename):
    """Generates a link to download the Markdown content as a file."""
    # Prepend a note that the code is Mermaid syntax if found
    if "```mermaid" in markdown_text:
        header = "# NOTE: This Specification includes a Mermaid Diagram.\n# You can view the flowchart code in the 'Feature Flow Diagram' section using a tool like Mermaid.live. \n\n"
        markdown_text = header + markdown_text
        
    # Encode the string data
    b64 = base64.b64encode(markdown_text.encode()).decode()
    
    # Create the HTML download link with stylish button class
    href = f'<a href="data:file/text;base64,{b64}" download="{filename}" class="download-button">⬇️ Download Specification (.md)</a>'
    return href


# --- Streamlit UI Configuration ---
st.set_page_config(layout="wide", page_title="SpecGen AI Agent")

# Apply custom, modern, and appealing CSS styling
st.markdown("""
<style>
    /* Base Background and Text Colors */
    .stApp {
        /* Vibrant gradient background using deep colors */
        background: linear-gradient(135deg, #0e021a 0%, #1a0537 50%, #0d1a2d 100%);
        color: #f0f6fc;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    h1 { 
        color: #ffb86c; /* Soft orange/yellow accent for main header */
        border-bottom: 2px solid #5a4b73;
        padding-bottom: 10px;
    }
    h3 { 
        color: #bd93f9; /* Pastel purple accent */
    }

    /* Input Field Styling */
    .stTextInput label, .stTextArea label {
        color: #f8f8f2;
    }
    .stTextInput input, .stTextArea textarea {
        background-color: #282a36; /* Dark background */
        color: #f8f8f2;
        border: 1px solid #44475a;
        border-radius: 12px; /* Increased rounding */
        padding: 12px;
        box-shadow: 0 0 15px rgba(189, 147, 249, 0.2); /* Subtle purple glow */
    }

    /* Primary Button Styling (Generate) - HIGH CONTRAST POP */
    div.stButton > button {
        background: linear-gradient(45deg, #ff79c6, #bd93f9); /* Pink to Purple Gradient */
        color: #282a36; /* Dark text for high contrast */
        border-radius: 12px;
        border: none;
        font-weight: bold;
        padding: 12px 25px;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(255, 121, 198, 0.4); /* Stronger glow/shadow */
    }
    div.stButton > button:hover {
        background: linear-gradient(45deg, #bd93f9, #ff79c6);
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(255, 121, 198, 0.6);
    }
    
    /* Download Button Styling (Custom class) */
    .download-button {
        background-color: #44475a; /* Neutral dark background */
        color: #f8f8f2 !important;
        border-radius: 8px;
        border: 1px solid #6272a4;
        padding: 10px 15px;
        text-decoration: none;
        font-weight: bold;
        transition: background-color 0.3s;
        display: inline-block;
        margin-top: 10px;
    }
    .download-button:hover {
        background-color: #6272a4;
        color: #ffb86c !important; /* Orange hover text */
    }

    /* Markdown Output Container (The Spec Document) */
    [data-testid="stMarkdownContainer"] {
        background-color: #282a36; /* Match input field background */
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #44475a;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.6);
        color: #f8f8f2;
    }
    
    /* Info Box (Critique Log) */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid #ff79c6 !important; /* Pink accent bar */
        background-color: #3b3d4f !important; /* Slightly lighter shade for distinction */
    }
</style>
""", unsafe_allow_html=True)


# --- UI Header ---
st.header("💡 SpecGen Agent: Idea to Specification")
st.markdown("### A Multi-Agent System for High-Quality, Validated Software Requirements")


# --- Input Section ---
feature_goal = st.text_area(
    "Enter a high-level feature goal:",
    value="Develop an in-app system to encourage users to create and share their personalized learning paths to boost community engagement and platform stickiness.",
    height=100
)

# --- Execution Button ---
if st.button("Generate & Validate Specification", key="run_button"):
    if not os.getenv("GEMINI_API_KEY"):
        st.error("🚨 GEMINI_API_KEY not found. Please set your API key in the .env file.")
        st.stop()
    
    if not feature_goal:
        st.warning("Please enter a feature goal to begin.")
        st.stop()

    # --- Execution Block ---
    start_time = time.time()
    
    status_placeholder = st.empty()
    status_placeholder.info("🚀 Running 3-Agent Collaboration... (Decomposition -> Generation -> QA Audit)")
    
    try:
        # 1. Create and run the crew
        spec_crew = create_spec_crew(feature_goal)
        result_output = spec_crew.kickoff()

        # --- Parsing Logic ---
        if hasattr(result_output, 'raw'):
            result_json_string = str(result_output.raw)
        else:
            result_json_string = str(result_output)

        # Clean JSON parsing: find the JSON block and load it
        json_match = re.search(r'\{.*\}', result_json_string, re.DOTALL)
        if json_match:
            clean_json_string = json_match.group(0).strip()
            # Clean up potential markdown formatting around the JSON
            clean_json_string = clean_json_string.replace('```json', '').replace('```', '').strip()
            result_data = json.loads(clean_json_string)
            final_spec = Specification(**result_data)
        else:
            st.error("⚠️ Failed to parse final output. LLM did not return clean JSON.")
            st.code(result_json_string, language='text') 
            st.stop()
            
        # --- Display Results ---
        end_time = time.time()
        elapsed_time = round(end_time - start_time, 2)
        
        # Update final status message
        if "Validated" in final_spec.validation_status:
            status_placeholder.success(f"✅ FINAL STATUS: **{final_spec.validation_status}** (Completed in {elapsed_time} seconds)")
        else:
            status_placeholder.error(f"❌ FINAL STATUS: **{final_spec.validation_status}** (Completed in {elapsed_time} seconds)")
        
        st.subheader("Final Output & Breakdown")

        # --- Layout for Presentation ---
        col_critique, col_spec = st.columns([1, 2])
        
        with col_critique:
            st.markdown("#### 🕵️ Audit Trail & Decomposition")
            st.markdown(f"**Original Goal:** *{final_spec.feature_goal}*")
            st.markdown("---")
            
            # Show the Validation Agent's Reasoning Log
            st.markdown("##### 📝 Validation Critique Log")
            st.info(final_spec.validation_critique)
            
            st.markdown("##### Atomic User Needs (Analyzer Output)")
            # Display the list of needs derived by the Goal Agent
            st.markdown("\n".join([f"* {need}" for need in final_spec.high_level_stories]))
        
        with col_spec:
            st.markdown("#### 📄 Audited Specification Document")
            
            # Download Link for the Specification
            download_link = get_markdown_download_link(
                final_spec.detailed_spec_markdown, 
                "SpecGen_Specification.md"
            )
            st.markdown(download_link, unsafe_allow_html=True)
            
            # Display the final specification document in Markdown format
            st.markdown(final_spec.detailed_spec_markdown)
            
    except Exception as e:
        status_placeholder.error(f"An unexpected error occurred: {e}")
        st.info("Check your terminal for detailed agent logs and ensure all dependencies are correct.")


# --- Footer ---
st.markdown("---")
st.caption("Powered by Gemini and CrewAI. Designed for COT6930 Final Project.")