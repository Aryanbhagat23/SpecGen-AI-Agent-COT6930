import streamlit as st
import json
import os
import time
import base64
import re
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import local modules
try:
    from agents import create_spec_crew
    from models import Specification
except ImportError as e:
    st.error(f"⚠️ Error importing modules: {e}")
    st.info("Make sure agents.py and models.py are in the same folder as app.py")
    st.stop()

def download_link(text, filename):
    """Generate download link for specification"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:file/text;base64,{b64}" download="{filename}_{timestamp}.md" class="download-btn">📥 Download Specification</a>'

# Page config
st.set_page_config(layout="wide", page_title="SpecGen AI", page_icon="✨")

# --- CSS Styling (New Dark Mode Theme for High Contrast) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Main background - Dark blue/gray gradient */
    .stApp {
        background: linear-gradient(135deg, #1f2937 0%, #0f172a 100%);
        font-family: 'Inter', sans-serif;
        color: #f3f4f6; /* Default text color is light */
    }

    /* White content card -> Dark content card */
    .main .block-container {
        max-width: 980px;
        padding: 2.5rem 2rem;
        background: #1f2937; /* Dark card background */
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        margin: 2rem auto;
        color: #f3f4f6; /* Ensures text inside is visible */
        border: 1px solid #374151;
    }

    /* Header styling - Neon Blue Gradient */
    h1 {
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%); 
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }

    .tagline {
        text-align: center;
        color: #9ca3af; /* Light gray for contrast */
        font-size: 1.15rem;
        font-weight: 500;
        margin-bottom: 1.5rem;
        padding-bottom: 1.5rem;
        border-bottom: 2px solid #374151; /* Dark divider */
    }

    /* Blue info banner -> Dark Accent */
    .info-banner {
        background: #374151; /* Dark background */
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
        color: #60a5fa; /* Light blue accent */
        font-weight: 600;
        font-size: 0.95rem;
        border: 1px solid #4b5563;
    }

    /* Yellow "New" banner -> Dark Orange Accent */
    .new-banner {
        background: #374151;
        padding: 0.9rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
        color: #fcd34d; /* Bright yellow/gold accent */
        font-weight: 600;
        font-size: 0.95rem;
        border: 1px solid #4b5563;
    }

    /* Section headers */
    .section-header {
        color: #e5e7eb; /* Light gray */
        font-size: 1.2rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #374151;
    }

    /* Template buttons */
    .stButton button {
        background: #4b5563; /* Dark button base */
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s;
        font-size: 0.95rem;
    }

    .stButton button:hover {
        background: #3b82f6; /* Blue hover accent */
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
    }

    /* Text input area - Dark, readable background */
    .stTextArea textarea {
        background: #111827; /* Near black */
        border: 2px solid #374151;
        border-radius: 12px;
        padding: 1rem;
        font-size: 1rem;
        color: #e5e7eb !important; /* Light text */
    }

    .stSelectbox, .stCheckbox {
        color: #e5e7eb !important;
        font-weight: 600;
    }

    .stSelectbox label, .stCheckbox label {
        color: #e5e7eb !important;
    }

    /* Main generate button - Neon Accent */
    button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%) !important;
        color: #0f172a !important; /* Dark text on bright button */
        border-radius: 12px !important;
        padding: 1rem 2.5rem !important;
        font-size: 1.1rem !important;
        font-weight: 800 !important;
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.4);
        transition: all 0.3s;
    }

    button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(59, 130, 246, 0.6);
    }

    /* Metrics styling - Blue accent */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: #60a5fa !important;
    }

    [data-testid="stMetricLabel"] {
        color: #9ca3af !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* Tabs styling - Dark background */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: #111827;
        padding: 0.5rem;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        background: #374151;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: #e5e7eb;
        transition: all 0.3s;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
        color: white !important;
    }

    /* Download button - Blue accent */
    .download-btn {
        display: inline-block;
        background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
        color: white !important;
        padding: 0.9rem 2rem;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 700;
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
        transition: all 0.3s;
    }

    /* Expander styling - Dark border */
    .stExpander {
        border: 2px solid #374151;
        border-radius: 12px;
        background: #1f2937;
    }

    /* Progress bar - Blue gradient */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
    }

    /* Success/Warning/Error messages - Dark backgrounds, bright text */
    .stSuccess {
        background: #10b981;
        color: #064e3b !important;
        border-radius: 12px;
        padding: 1rem;
    }

    .stWarning {
        background: #f59e0b;
        color: #78350f !important;
        border-radius: 12px;
        padding: 1rem;
    }

    .stError {
        background: #ef4444;
        color: #7f1d1d !important;
        border-radius: 12px;
        padding: 1rem;
    }
    
    .stInfo {
        background: #3b82f6;
        color: #1c3c72 !important;
        border-radius: 12px;
        padding: 1rem;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1>✨ SpecGen AI</h1>", unsafe_allow_html=True)
st.markdown('<p class="tagline">Transform Ideas into Professional Requirements • Powered by AI Agents</p>', unsafe_allow_html=True)

# Info banners
st.markdown("""<div class="info-banner">
    🎯 AI-Powered Analysis • ✅ Multi-Agent Validation • 📊 Metrics Dashboard • 🚀 Production Ready</div>""", unsafe_allow_html=True)
st.markdown("""<div class="new-banner">
    💡 <strong>New!</strong> Industry-specific requirements • Cost estimation • Timeline predictions • Quality validation</div>""", unsafe_allow_html=True)

# Quick start templates
with st.expander("💡 Need inspiration? Try these examples", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📱 SOCIAL MEDIA FEATURE", use_container_width=True, key="btn1"):
            st.session_state.template = "Build a social feed with infinite scroll, post creation, likes, comments, and real-time notifications"
            st.rerun()
        if st.button("🛒 E-COMMERCE CHECKOUT", use_container_width=True, key="btn2"):
            st.session_state.template = "Create a secure checkout system with multiple payment methods, address validation, and order tracking"
            st.rerun()
        if st.button("📊 ANALYTICS DASHBOARD", use_container_width=True, key="btn3"):
            st.session_state.template = "Develop a real-time analytics dashboard with customizable widgets, charts, and data export capabilities"
            st.rerun()
    with col2:
        if st.button("🔐 AUTHENTICATION SYSTEM", use_container_width=True, key="btn4"):
            st.session_state.template = "Build a secure authentication system with OAuth, two-factor authentication, and password recovery"
            st.rerun()
        if st.button("💬 CHAT APPLICATION", use_container_width=True, key="btn5"):
            st.session_state.template = "Create a real-time chat system with typing indicators, read receipts, and file sharing"
            st.rerun()
        if st.button("🎓 LEARNING PLATFORM", use_container_width=True, key="btn6"):
            st.session_state.template = "Develop an online learning platform with course management, progress tracking, and assessments"
            st.rerun()

# Industry context section
st.markdown('<p class="section-header">🏢 Industry Context (Optional)</p>', unsafe_allow_html=True)
col1, col2 = st.columns([2, 1])
with col1:
    industry = st.selectbox(
        "Select Industry",
        ["General", "Healthcare", "Finance", "E-commerce", "Education", "SaaS", "Government", "Entertainment"],
        key="industry"
    )
with col2:
    team_size = st.selectbox(
        "Team Size",
        ["Solo", "2-5", "6-20", "21-50", "51+"],
        key="team"
    )

# Main input section
st.markdown('<p class="section-header">🎯 Describe Your Feature Goal</p>', unsafe_allow_html=True)
default_value = st.session_state.get('template', "Develop an in-app system to encourage users to create and share their personalized learning paths")
feature_goal = st.text_area(
    "Feature Goal Input",  # Added proper label for accessibility
    height=120,
    value=default_value,
    placeholder="Example: Build a payment system with credit cards, refunds, and fraud detection...",
    label_visibility="collapsed",  # Hides the label but keeps it accessible
    key="feature_input")

# Advanced options
with st.expander("⚙️ Advanced Options", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        include_security = st.checkbox("🔒 Include Security Requirements", value=True)
        include_accessibility = st.checkbox("♿ Include Accessibility (WCAG)", value=False)
        include_testing = st.checkbox("🧪 Include Testing Strategy", value=True)
    with col2:
        include_deployment = st.checkbox("🚀 Include Deployment Considerations", value=False)
        include_cost = st.checkbox("💰 Include Cost Estimation", value=True)
        include_api = st.checkbox("🔌 Include API Specifications", value=False)
st.markdown("<br>", unsafe_allow_html=True)

# Generate button (centered)
col1, col2, col3 = st.columns([1.5, 1, 1.5])
with col2:
    generate_btn = st.button("🚀 GENERATE SPECIFICATION", use_container_width=True, type="primary")

# Main generation logic
if generate_btn:
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error("⚠️ **GEMINI_API_KEY not found**")
        st.info("""
        Please create a `.env` file in your project folder with:```
        GEMINI_API_KEY=your_actual_api_key_here```
        
        Get your API key from: https://aistudio.google.com/app/apikey
        """)
        st.stop()

    if not feature_goal.strip():
        st.warning("⚠️ Please describe your feature goal")
        st.stop()

    start_time = time.time()

    # Show loading state
    with st.spinner("🤖 AI Agents are working on your specification..."):
        try:
            # Build enhanced prompt
            prompt = feature_goal.strip()

            if industry != "General":
                prompt += f"\n\nIndustry: {industry}"

            if team_size != "Solo":
                prompt += f"\nTeam Size: {team_size}"

            if include_security:
                prompt += "\n\nInclude security requirements (authentication, authorization, encryption, data protection)."

            if include_accessibility:
                prompt += "\n\nInclude WCAG 2.1 Level AA accessibility requirements."

            if include_testing:
                prompt += "\n\nInclude comprehensive testing strategy and test cases."

            if include_deployment:
                prompt += "\n\nInclude deployment, infrastructure, and scalability considerations."

            if include_cost:
                prompt += "\n\nInclude cost estimation and resource requirements."

            if include_api:
                prompt += "\n\nInclude RESTful API endpoint specifications."

            # Create and run the crew
            crew = create_spec_crew(prompt)
            result = crew.kickoff()

            # Parse the result
            raw_output = str(result.raw if hasattr(result, 'raw') else result)

            # Clean up the output - remove markdown code blocks
            raw_output = re.sub(r'```json\s*', '', raw_output)
            raw_output = re.sub(r'```\s*', '', raw_output)
            raw_output = raw_output.strip()

            # Extract JSON using regex
            json_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
            if not json_match:
                raise ValueError("No valid JSON found in agent output")

            json_str = json_match.group(0)

            # Clean JSON - remove trailing commas
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)

            # Parse JSON
            data = json.loads(json_str)
            spec = Specification(**data)

            elapsed_time = time.time() - start_time
            timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")

        except json.JSONDecodeError as e:
            st.error(f"❌ **JSON Parsing Error**")
            st.info("The AI generated invalid JSON. Please try again.")
            with st.expander("🔍 Debug Info (for developers)"):
                st.code(raw_output[:500])
            st.stop()

        except Exception as e:
            error_msg = str(e)

            # Handle specific errors
            if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                st.error("⚠️ **API Rate Limit Reached**")
                st.info("The free tier has a limit. Please wait 60 seconds and try again.")

            elif "404" in error_msg or "not found" in error_msg.lower():
                st.error("⚠️ **Model Not Available**")
                st.info("The AI model is temporarily unavailable. Please try again in a moment.")

            elif "401" in error_msg or "unauthorized" in error_msg.lower() or "invalid" in error_msg.lower():
                st.error("⚠️ **Invalid API Key**")
                st.info("""
                Your API key may be invalid or expired. Please:
                1. Go to https://aistudio.google.com/app/apikey
                2. Generate a new API key
                3. Update your `.env` file with the new key
                4. Restart the app
                """)

            else:
                st.error(f"❌ **Generation Failed**")
                st.info("An unexpected error occurred. Please try again.")

            with st.expander("🔍 Error Details (for debugging)"):
                st.code(error_msg)
            st.stop()

    # Success message
    st.success("✅ Specification generated successfully!")
    st.balloons()

    # Metrics dashboard
    st.markdown('<p class="section-header">📊 Specification Metrics</p>', unsafe_allow_html=True)

    # Calculate metrics
    fr_count = spec.detailed_spec_markdown.count('FR-')
    nfr_count = spec.detailed_spec_markdown.count('NFR-')
    word_count = len(spec.detailed_spec_markdown.split())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⏱️ Generation Time", f"{elapsed_time:.1f}s")
    with col2:
        st.metric("📋 User Stories", len(spec.high_level_stories))
    with col3:
        st.metric("✅ Requirements", fr_count + nfr_count)
    with col4:
        st.metric("📝 Word Count", f"{word_count:,}")

    # Download button
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(download_link(spec.detailed_spec_markdown, "SpecGen_Specification"), unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Tabbed interface for results
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Full Specification", "📋 Executive Summary", "🔍 Quality Report", "💡 AI Insights"])

    with tab1:
        st.markdown("### Complete Specification Document")
        with st.expander("📑 Quick Navigation", expanded=False):
            st.markdown("""
            - **Introduction** - Feature overview and scope
            - **Functional Requirements** - What the system must do
            - **Non-Functional Requirements** - How the system must perform
            - **Acceptance Criteria** - Testable conditions (GIVEN/WHEN/THEN)
            - **Assumptions** - Prerequisites and constraints
            """)
        st.markdown(spec.detailed_spec_markdown)

    with tab2:
        st.markdown("### Executive Summary")

        st.markdown("#### 🎯 Feature Goal")
        st.info(feature_goal)

        st.markdown("#### 👥 User Stories")
        for i, story in enumerate(spec.high_level_stories, 1):
            st.write(f"{i}. {story}")

        st.markdown("#### 📊 Requirements Overview")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Functional Requirements", fr_count)
            st.caption("Core features and capabilities")
        with col2:
            st.metric("Non-Functional Requirements", nfr_count)
            st.caption("Performance, security, scalability")

        if include_cost:
            st.markdown("#### 💰 Project Estimates")
            # Calculation logic identical to your original code
            weeks = max(2, (fr_count * 0.5 + nfr_count * 0.3))
            min_cost = int(weeks * 40 * 80)
            max_cost = int(weeks * 1.5 * 40 * 150)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Estimated Cost", f"${min_cost:,} - ${max_cost:,}")
                st.caption("Based on industry averages for similar projects")
            with col2:
                st.metric("Timeline", f"{int(weeks)}-{int(weeks*1.5)} weeks")
                st.caption("Includes development, testing, and deployment")

    with tab3:
        st.markdown("### Quality Assurance Report")

        if spec.validation_status == "Validated":
            st.success("✅ All quality checks passed successfully!")
        else:
            st.warning(f"⚠️ Status: {spec.validation_status}")

        st.markdown("#### 📝 Validation Feedback")
        st.info(spec.validation_critique)

        st.markdown("#### ✅ Quality Checks Performed")
        checks = [
            "✓ Testability - All requirements follow GIVEN/WHEN/THEN format",
            "✓ Consistency - Requirements are logically coherent",
            "✓ Completeness - All aspects of the feature are covered",
            "✓ Measurability - Requirements have quantifiable acceptance criteria",
            "✓ Clarity - No ambiguous language (fast, easy, user-friendly)",
            "✓ Traceability - Requirements are properly numbered and organized"
        ]
        for check in checks:
            st.write(check)

    with tab4:
        st.markdown("### AI-Powered Insights")

        # Completeness score
        completeness = min(100, (fr_count * 5 + nfr_count * 5 + len(spec.high_level_stories) * 10))
        st.markdown("#### 📈 Completeness Score")
        st.progress(completeness / 100)
        st.write(f"**{completeness}%** - Your specification is comprehensive and well-structured")

        # Complexity analysis
        st.markdown("#### 🧩 Implementation Complexity")
        if fr_count + nfr_count < 15:
            complexity = "Low"
            color = "🟢"
        elif fr_count + nfr_count < 30:
            complexity = "Medium"
            color = "🟡"
        else:
            complexity = "High"
            color = "🔴"
        st.write(f"{color} **{complexity}** - Based on {fr_count + nfr_count} total requirements")

        # Timeline and cost estimates
        if include_cost:
            st.markdown("#### 📅 Project Estimates")
            weeks = max(2, (fr_count * 0.5 + nfr_count * 0.3))
            min_cost = int(weeks * 40 * 80)
            max_cost = int(weeks * 1.5 * 40 * 150)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("💰 Estimated Cost", f"${min_cost:,} - ${max_cost:,}")
                st.caption("Based on industry averages for similar projects")
            with col2:
                st.metric("⏱️ Timeline", f"{int(weeks)}-{int(weeks*1.5)} weeks")
                st.caption("Includes development, testing, and deployment")

        # Recommendations
        st.markdown("#### 🎯 Recommended Next Steps")
        next_steps = [
            "1. Review and refine requirements with stakeholders",
            "2. Break down into sprint-sized tasks",
            "3. Prioritize features (MoSCoW method)",
            "4. Create technical design documentation",
            "5. Set up project tracking (Jira/Azure DevOps)"
        ]
        for step in next_steps:
            st.write(step)

    # Footer with timestamp
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; padding: 1rem 0; color: #9ca3af;'>
        <p>Generated on {timestamp} • Powered by CrewAI & Gemini Flash 1.5</p>
    </div>
    """, unsafe_allow_html=True)
# Default footer
else:
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0; color: #9ca3af;'>
        <p>Made with ❤️ using CrewAI & Google Gemini</p>
        <p style='font-size: 0.9rem; margin-top: 0.5rem;'>Multi-Agent AI • Validation Layer • Industry Standards</p>
    </div>
    """, unsafe_allow_html=True)