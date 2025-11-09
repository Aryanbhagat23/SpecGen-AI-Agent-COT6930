import os
import json
import re
from dotenv import load_dotenv

# --- Import LiteLLM and Pydantic for robust execution ---
# We MUST use LiteLLM now since it's clearly hijacking all model calls.
try:
    from litellm import completion
    from pydantic import BaseModel, Field
except ImportError:
    raise ImportError("LiteLLM is required for this environment. Please run 'pip install litellm pydantic'.")

# --- Fallback for Google Genai (Not used for API call, but sometimes CrewAI looks for it) ---
try:
    from google import genai
    from google.genai.errors import APIError
except ImportError:
    pass 

# Load environment variables
load_dotenv()

# --- Configuration Constants ---
# LiteLLM requires the provider to be prefixed in the model name.
# This format explicitly tells LiteLLM to use the Gemini provider with the 2.5-flash model.
GEMINI_MODEL_ID = "gemini/gemini-2.5-flash" 
# LiteLLM uses GEMINI_API_KEY environment variable automatically.

# --- Pydantic Output Model (Must match models.py) ---
class Specification(BaseModel):
    feature_goal: str = Field(description="The original high-level feature goal.")
    high_level_stories: list[str] = Field(description="7-8 atomic, clear user needs/problems derived from the goal.")
    detailed_spec_markdown: str = Field(description="The complete software specification document in Markdown format, including a dedicated section for the Mermaid Flowchart Syntax.")
    validation_status: str = Field(description="The final status from the Validation Agent (e.g., 'Validated' or 'Needs Refinement').")
    validation_critique: str = Field(description="The detailed log explaining the audit process and any corrections made to achieve validation.")


# --- 1. Master Orchestration Function (Now using LiteLLM Completion) ---

def run_specgen_pipeline(feature_goal: str) -> dict:
    """
    Executes the three-stage multi-agent pipeline using sequential LiteLLM API calls.
    """
    
    if not feature_goal:
        return {"error": "Input feature goal cannot be empty."}

    # --- Stage 1: Goal Agent (Analyzer) - Decomposition ---
    stage_1_prompt = f"""
    You are the Goal Decomposition Analyst. Your goal is to analyze the complex feature goal provided and break it down into a structured list of 7-8 atomic user needs/problems. Focus on mitigating ambiguity.
    
    FEATURE GOAL: "{feature_goal}"
    
    Your output MUST be ONLY a JSON list of strings, where each string is a clear user need starting with 'As a user, I want...'. Do NOT include any other text.
    """
    
    try:
        response_s1 = completion(
            model=GEMINI_MODEL_ID,
            messages=[{"role": "user", "content": stage_1_prompt}],
            temperature=0.3
        )
        # LiteLLM returns a standard OpenAI-style response object
        response_text = response_s1['choices'][0]['message']['content']
        
        # Attempt to parse the JSON list of stories
        stories_json_str = re.search(r'\[.*\]', response_text, re.DOTALL).group(0)
        user_needs_list = json.loads(stories_json_str)
        
    except Exception as e:
        return {"error": f"Stage 1 (Decomposition) Failed: {e}"}


    # --- Stage 2: Feature Agent (Generator) - Specification and Diagram ---
    stage_2_prompt = f"""
    You are the Technical Specification Writer and Visual Planner. Your task is to generate a COMPLETE software specification document in detailed Markdown format based on the following user needs.
    
    USER NEEDS (from Analyst): {user_needs_list}

    The document MUST be comprehensive (FRs, NFRs, Assumptions).
    
    CRITICAL: Include a section titled '## 4. Feature Flow Diagram' containing a single Mermaid syntax block (e.g., '```mermaid\nflowchart TD\n... \n```') that visually represents the core user journey or system logic for this feature.
    """
    
    try:
        response_s2 = completion(
            model=GEMINI_MODEL_ID,
            messages=[{"role": "user", "content": stage_2_prompt}],
            temperature=0.2
        )
        spec_draft_markdown = response_s2['choices'][0]['message']['content']
    except Exception as e:
        return {"error": f"Stage 2 (Generation) Failed: {e}"}


    # --- Stage 3: Validation Agent (Critic) - Audit and Final JSON ---
    stage_3_prompt = f"""
    You are the Senior QA Lead and Specification Auditor. Your goal is to critically review the specification draft provided below against four standards: Testability, Consistency, Completeness, and Clean Markdown/Mermaid Format.
    
    SPECIFICATION DRAFT TO AUDIT:
    ---
    {spec_draft_markdown}
    ---
    
    Perform your audit. If you find any flaws, correct them in the final markdown output.
    
    Your final response MUST be ONLY a single JSON object that strictly adheres to the provided Specification JSON schema. Do not include any text outside the JSON block.
    """

    try:
        # Use LiteLLM's structured output capability
        response_s3 = completion(
            model=GEMINI_MODEL_ID,
            messages=[{"role": "user", "content": stage_3_prompt}],
            response_model=Specification, # This forces the JSON schema
            temperature=0.1
        )
        
        # LiteLLM returns the parsed object, not raw text
        final_spec_object = response_s3.model_dump_json()

    except Exception as e:
        return {"error": f"Stage 3 (Validation/JSON Output) Failed: {e}"}

    # --- Final Output Synthesis ---
    return {
        "final_json_str": final_spec_object,
        "raw_stories": user_needs_list,
        "raw_spec_draft": spec_draft_markdown
    }