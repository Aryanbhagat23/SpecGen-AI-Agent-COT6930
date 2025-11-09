import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, CrewOutput, LLM
from pydantic import BaseModel, Field

# --- Import local modules ---
try:
    from models import Specification
except ImportError:
    # Fallback/Error handling if models.py is missing
    raise ImportError("Failed to import Specification from models.py. Ensure models.py is in the directory.")


# Load environment variables
load_dotenv()

# --- LLM and Client Setup (The FIX for LiteLLM) ---
try:
    # Explicitly configure LiteLLM to use the Gemini provider
    # LiteLLM automatically uses the GEMINI_API_KEY environment variable
    GEMINI_MODEL_ID = "gemini/gemini-2.5-flash"
    
    # Instantiate the LLM object for CrewAI
    gemini_llm = LLM(model=GEMINI_MODEL_ID) 

except Exception as e:
    print(f"Error during LLM setup: {e}")
    raise Exception(f"Failed to initialize LLM for CrewAI. Check API Key or LiteLLM installation: {e}")


# --- 1. Define Agent Roles ---

# 1.1. Goal Agent (Analyzer)
goal_agent = Agent(
    role='Goal Decomposition Analyst',
    goal='Decompose a single, complex feature goal into a list of 7-8 atomic, clear, and actionable user needs/problems. Focus on mitigating ambiguity.',
    backstory='You are an expert product manager focused on ensuring clarity and preventing ambiguity at the start of any software project.',
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm
)

# 1.2. Feature Agent (Generator & Multimodal Diagrammer)
feature_agent = Agent(
    role='Technical Specification Writer and Visual Planner',
    goal='Take a list of user needs and generate a COMPLETE software specification document in detailed Markdown format. You MUST include a dedicated section titled \'## 4. Feature Flow Diagram\' containing a single Mermaid syntax block (e.g., \'```mermaid\\nflowchart TD\\n...\\n```\') that visually represents the core user journey or system logic for this feature.',
    backstory='You are a rigorous technical writer who ensures every requirement is testable and clearly documented for the engineering team. Your output is production-ready.',
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm
)

# 1.3. Validation Agent (Critic)
validation_agent = Agent(
    role='Senior QA Lead and Specification Auditor',
    goal="""
    Critically review the full technical specification provided in the context against four core quality standards: Testability (GIVEN/WHEN/THEN format), Consistency, Completeness, and Clean Markdown Format.
    Your primary function is to enforce rigorous quality control. 
    1. Check for Testability: MUST ensure every high-level user need has complete GIVEN/WHEN/THEN acceptance criteria.
    2. Check for Consistency: MUST flag or correct any contradictory statements or subjective terms (e.g., "fast," "easy") with measurable, objective criteria.
    3. Check for Completeness: MUST ensure the document includes all required sections AND the Mermaid flowchart syntax.
    4. Check for Format: MUST verify the syntax of the Mermaid diagram is valid and the overall Markdown is clean.

    If ALL checks pass, output the final Specification JSON object with 'validation_status' set to 'Validated'.
    If ANY fail, you must list the exact failures in the 'validation_critique' and then rewrite/correct the 'detailed_spec_markdown' content to resolve the issues before outputting the final JSON.
    """,
    backstory='You are a security-conscious, highly meticulous auditor who enforces that all specifications are robust and ready for development.',
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm
)


# --- 2. Define the Tasks (The Workflow) ---

def create_tasks(feature_goal: str):
    task1 = Task(
        description=f"Decompose the following high-level feature goal into a list of 7-8 atomic user needs (starting with 'As a user, I want...'): {feature_goal}. Output only the list of needs.",
        agent=goal_agent,
        expected_output="A structured list of 7-8 specific, actionable user needs derived from the goal."
    )

    task2 = Task(
        description="""Generate a full technical specification in detailed Markdown format based on the user needs provided. 
        The document MUST be comprehensive (FRs, NFRs, Assumptions). 
        CRITICAL: Include a section titled '## 4. Feature Flow Diagram' containing a single Mermaid syntax block (e.g., '```mermaid\\nflowchart TD\\n...\\n```') that visually represents the core user journey or system logic for this feature.""",
        agent=feature_agent,
        context=[task1], 
        expected_output="A complete software specification document in Markdown format that strictly includes the Mermaid flowchart syntax."
    )

    task3 = Task(
        description="Critically review the generated specification and Mermaid syntax for compliance, testability, and consistency, then prepare the final output using the required JSON schema.",
        agent=validation_agent,
        context=[task2], 
        output_json=Specification,
        expected_output="A Pydantic JSON object containing the complete, audited specification and the final validation status and critique."
    )
    
    return [task1, task2, task3]


# --- 3. Assemble the Crew ---

def create_spec_crew(feature_goal: str):
    tasks = create_tasks(feature_goal)
    crew = Crew(
        agents=[goal_agent, feature_agent, validation_agent],
        tasks=tasks,
        process=Process.sequential, 
        verbose=1 
    )
    return crew