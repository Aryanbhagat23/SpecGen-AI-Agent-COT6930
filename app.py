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


# --- Helper Function for Download Link ---
def get_markdown_download_link(markdown_text, filename):
    if "```mermaid" in markdown_text:
        header = "# NOTE: This Specification includes a Mermaid Diagram.\n# You can view the flowchart code in the 'Feature Flow Diagram' section using a tool like Mermaid.live. \n\n"
        markdown_text = header + markdown_text
    b64 = base64.b64encode(markdown_text.encode()).decode()
    href = f'<a href="data:file/text;base64,{b64}" download="{filename}" class="download-button">⬇️ Download Specification (.md)</a>'
    return href


# --- Streamlit UI Configuration ---
st.set_page_config(layout="wide", page_title="SpecGen AI Agent")

# --- NEW: Modern SaaS Theme CSS ---
st.markdown("""
<style>
    /* ANIMATED BACKGROUND */
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        # animation: gradient 15s ease infinite; /* Optional: uncomment for movement */
        background: #f4f7f6; /* Fallback/Static clean background if preferred */
        background: linear-gradient(135deg, #f6f8fd 0%, #f1f4f9 100%);
        color: #1a202c;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* MAIN CONTAINER CARD EFFECT */
    .block-container {
        max-width: 950px;
        padding-top: 3rem;
        padding-bottom: 5rem;
    }
    div[data-testid="stVerticalBlock"] > div.stMarkdown {
        /* This targets specific markdown blocks if needed */
    }
    
    /* HEADERS */
    h1 {
        color: #2d3748;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin-bottom: 0.5rem;
    }
    h3 {
        color: #718096;
        font-weight: 400;
        font-size: 1.25rem;
        margin-top: 0;
    }
    
    /* INPUT AREA Styling */
    .stTextArea label {
        color: #4a5568;
        font-weight: 600;
        font-size: 1rem;
    }
    .stTextArea textarea {
        background-color: #ffffff;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.05);
        color: #2d3748;
        font-size: 16px;
        transition: all 0.2s;
    }
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102,126,234, 0.2);
    }

    /* GENERATE BUTTON - The Hero Action */
    div.stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* Indigo Gradient */
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 50px; /* Pill shape */
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 0 10px 20px -10px rgba(102,126,234, 0.5);
        transition: all 0.3s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 14px 28px -10px rgba(102,126,234, 0.6);
        color: #ffffff;
    }
    
    /* STATUS BOXES */
    .stAlert {
        border-radius: 12px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    
    /* RESULT CARDS */
    [data-testid="stMarkdownContainer"] {
        # background-color: #ffffff;
        # padding: 25px;
        # border-radius: 16px;
        # box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        # border: 1px solid #edf2f7;
    }
    
    /* DOWNLOAD BUTTON */
    .download-button {
        display: inline-block;
        background-color: #2d3748;
        color: #ffffff !important;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.2s;
    }
    .download-button:hover {
        background-color: #4a5568;
        transform: translateY(-1px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }
    
    /* Remove standard Streamlit footer and hamburger menu for clean look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)


# --- HERO SECTION ---
# Centered, clean title area
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.markdown("<h1 style='text-align: center;'>🚀 SpecGen Agent</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Turn Vague Ideas Into Rigorous, Validated Software Specifications In Seconds.</h3>", unsafe_allow_html=True)
    st.markdown("---")


# --- MAIN INPUT SECTION ---
# Using a container to create a visual "card" effect for the input
with st.container():
    col_spacer_l, col_main, col_spacer_r = st.columns([1, 8, 1])
    with col_main:
        feature_goal = st.text_area(
            "What feature do you want to build?",
            height=120,
            placeholder="E.g., Build a real-time notification system for user engagement...",
            help="Enter a high-level goal. The agents will handle the details."
        )
        
        # Spacing
        st.write("") 
        
        if st.button("✨ Generate & Validate Specification"):
            if not os.getenv("GEMINI_API_KEY"):
                st.error("🚨 GEMINI_API_KEY not found in .env file.")
                st.stop()
            if not feature_goal:
                st.warning("Please enter a feature goal first.")
                st.stop()

            # --- Execution Flow ---
            start_time = time.time()
            status_area = st.empty()
            
            # Minimalist, clean status updates
            with status_area.status("🤖 AI Agents at work...", expanded=True) as status:
                st.write("🧠 **Goal Agent** is decomposing your idea...")
                # (Real app would have granular updates here if possible)
                time.sleep(0.8) # UI Interaction pause
                st.write("✍️ **Feature Agent** is drafting technical requirements & flowcharts...")
                time.sleep(0.8)
                st.write("🕵️ **Validation Agent** is auditing for testability and consistency...")
                
                try:
                    # Run the actual crew
                    spec_crew = create_spec_crew(feature_goal)
                    result_output = spec_crew.kickoff()

                    # Parse output
                    raw_output = str(result_output.raw) if hasattr(result_output, 'raw') else str(result_output)
                    json_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
                    
                    if json_match:
                        clean_json = json_match.group(0).strip().replace('```json', '').replace('```', '')
                        final_spec = Specification(**json.loads(clean_json))
                        status.update(label="✅ Specification Ready!", state="complete", expanded=False)
                    else:
                        status.update(label="❌ Parsing Error", state="error", expanded=True)
                        st.error("Could not parse agent output. See raw data below.")
                        st.code(raw_output)
                        st.stop()

                    # --- RESULTS DISPLAY ---
                    st.markdown("---")
                    
                    # Use tabs for a cleaner, less scrolling-heavy layout
                    tab1, tab2 = st.tabs(["📄 Final Specification", "🕵️ Validation Audit Trail"])
                    
                    with tab1:
                        st.success(f"Generation Complete in {round(time.time() - start_time, 2)}s")
                        # Download Button prominently displayed
                        st.markdown(get_markdown_download_link(final_spec.detailed_spec_markdown, "SpecGen_Output.md"), unsafe_allow_html=True)
                        
                        # Render the spec in a clean white card
                        st.markdown(
                            f"""<div style="background-color: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); color: #2d3748;">
                            {final_spec.detailed_spec_markdown}
                            </div>""", 
                            unsafe_allow_html=True
                        )

                    with tab2:
                        st.info("### Validation Critique Log")
                        st.markdown(f"**Status:** `{final_spec.validation_status}`")
                        st.write(final_spec.validation_critique)
                        st.divider()
                        st.markdown("### Original Decomposed Needs")
                        for story in final_spec.high_level_stories:
                            st.markdown(f"- {story}")

                except Exception as e:
                    status.update(label="❌ System Error", state="error", expanded=True)
                    st.error(f"An error occurred: {e}")

# --- Simple Footer ---
st.markdown("<div style='text-align: center; color: #a0aec0; padding-top: 50px;'>SpecGen Dynamics • COT6930 Final Project</div>", unsafe_allow_html=True)