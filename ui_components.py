import streamlit as st

# --------------------------------------------------
# Reusable UI Components for SpecGen AI
# --------------------------------------------------
# This file keeps the UI clean and modular.

# -------------------------
# Styled Title
# -------------------------
def app_title():
    st.markdown(
        """
        <h1 style='text-align:center; color:#042f3b;'>✨ SpecGen AI — Gemini Edition</h1>
        <p style='text-align:center; color:#425466; font-size:1.1rem;'>Startup-ready specifications, roadmaps, risks & architecture powered by Gemini</p>
        """,
        unsafe_allow_html=True,
    )


# -------------------------
# Beautiful divider
# -------------------------
def divider(label: str = ""):
    st.markdown(
        f"""
        <div style='margin:25px 0; text-align:center;'>
            <span style='font-weight:600; color:#0f172a;'>{label}</span>
            <hr style='border:0; border-top:2px solid #e2e8f0; margin-top:8px;'>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------
# Info Card
# -------------------------
def info_card(title: str, body: str):
    st.markdown(
        f"""
        <div style='background:#ecfeff; border-left:5px solid #06b6d4; padding:1rem 1.2rem; border-radius:10px; margin:10px 0;'>
            <h4 style='margin:0; color:#036672;'>{title}</h4>
            <p style='margin:6px 0; color:#0c4a6e;'>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------
# Section Card Wrapper
# -------------------------
def section_card(title: str):
    st.markdown(
        f"""
        <div style='padding:1rem; background:white; border-radius:14px; box-shadow:0 6px 18px rgba(0,0,0,0.06); margin-bottom:1.2rem;'>
            <h3 style='margin-top:0; color:#0f172a;'>{title}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------
# Metric Row
# -------------------------
def metrics(requirements: int, stories: int, words: int):
    c1, c2, c3 = st.columns(3)
    c1.metric("Requirements", requirements)
    c2.metric("User Stories", stories)
    c3.metric("Words", words)


# -------------------------
# Styled Download Button
# -------------------------
def download_button(label: str, data: str, filename: str):
    st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime="text/plain",
        use_container_width=True,
    )


# -------------------------
# Footer
# -------------------------
def footer():
    st.markdown(
        """
        <div style='text-align:center; margin-top:2rem; color:#64748b;'>
            Made with ❤️ using Gemini & CrewAI — SpecGen for Startups
        </div>
        """,
        unsafe_allow_html=True,
    )