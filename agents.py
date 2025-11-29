import os
from crewai import Agent, Task, Crew, Process, LLM
from models import Specification # Ensure this import is correct
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------
#  VALIDATE API KEY
# ---------------------------------------------
if "GEMINI_API_KEY" not in os.environ:
    # This check is redundant with the one in app.py, but essential for CLI runs.
    raise ValueError("ERROR: GEMINI_API_KEY is missing from environment variables.")

# ---------------------------------------------
#  LLM CONFIGURATION (Gemini 2.5 Flash - stable and reliable)
# ---------------------------------------------
my_llm = LLM(
    model="gemini-2.5-flash",     # Use the latest, stable model name
    api_key=os.environ["GEMINI_API_KEY"],
    temperature=0.4,
    verbose=True, # Set to True for debugging agent thought process
)

# ---------------------------------------------
#  CREW FACTORY
# ---------------------------------------------
def create_spec_crew(goal_text: str):
    """
    Creates the complete CrewAI pipeline (analyst → writer → reviewer)
    and outputs a Specification pydantic object.
    """

    # ---------------------------
    #  Agent 1 — Analyst (Goal Decomposition Agent)
    # ---------------------------
    analyst = Agent(
        role="Product Analyst",
        goal="Break down high-level feature goals into specific user stories, identify risks, and gather strategic insights.",
        backstory="""You are an experienced product analyst who excels at understanding
        user needs and decomposing complex features into clear, actionable user stories.
        You always think from the user's perspective and perform strategic analysis.""",
        allow_delegation=False,
        verbose=True,
        llm=my_llm,
    )

    # ---------------------------
    #  Agent 2 — Technical Writer (Feature Specification Agent)
    # ---------------------------
    writer = Agent(
        role="Lead Technical Writer",
        goal="Transform analysis into a complete, structured Software Requirement Specification (SRS) in Markdown.",
        backstory="""You are a precision technical writer. You produce clean,
        well-structured SRS documents using standard FR-XXX and NFR-XXX conventions.""",
        allow_delegation=False,
        verbose=True,
        llm=my_llm,
    )

    # ---------------------------
    #  Agent 3 — Reviewer / QA (Validation Agent)
    # ---------------------------
    reviewer = Agent(
        role="QA Engineering Lead",
        goal="Validate the specification for clarity, testability, and produce the final, perfectly structured JSON output matching the Specification model.",
        backstory="""You rigorously verify requirement quality. You ensure every item is testable,
        clear, and formatted properly. You produce the final structured output, and nothing else.""",
        allow_delegation=False,
        verbose=True,
        llm=my_llm,
    )

    # ---------------------------
    #  Task 1 — Analysis & Story Breakdown
    # ---------------------------
    analysis_task = Task(
        description=f"""
        Analyze this product goal and related context:

        "{goal_text}"

        Your output must contain:
        - 3–5 high-level user stories following the 'As a [role], I want [action] so that [benefit]' format.
        - Strategic notes on potential risks, missing workflows, and key features derived from the strategic context in the goal.
        """,
        expected_output="A structured analysis summary containing high-level user stories, risks, and strategic notes.",
        agent=analyst,
    )

    # ---------------------------
    #  Task 2 — Draft the SRS
    # ---------------------------
    drafting_task = Task(
        description="""
        Create a full Software Requirements Specification (SRS) in clean Markdown using the Analyst's output.

        The document MUST be structured with clear headings:
        # Title
        ## Introduction
        ## User Stories
        ## Functional Requirements (FR-001…)
        ## Non-Functional Requirements (NFR-001…)
        ## API Requirements (if applicable)
        ## Data Requirements (if applicable)
        ## Risks & Mitigation
        
        Do NOT output JSON. Only the full Markdown text.
        """,
        agent=writer,
        context=[analysis_task],
        expected_output="A complete, well-formatted SRS document in Markdown.",
    )

    # ---------------------------
    #  Task 3 — Validate & Output JSON
    # ---------------------------
    validation_task = Task(
        description="""
        Review the drafted SRS for completeness and quality.

        You MUST produce a JSON object that strictly matches the Pydantic model: Specification.

        Fill ALL fields:
        - high_level_stories: Extract the list of user stories from the SRS.
        - detailed_spec_markdown: Place the full SRS Markdown document here (as a single string).
        - validation_status: Set to 'Validated' or 'Needs Revision'.
        - validation_critique: A short summary of your quality check.

        Return ONLY the raw JSON object, no Markdown code blocks or commentary.
        """,
        expected_output="A final validated JSON object strictly matching the Specification model.",
        agent=reviewer,
        context=[drafting_task],
        output_pydantic=Specification,
    )

    # ---------------------------
    #  Assemble Crew
    # ---------------------------
    crew = Crew(
        agents=[analyst, writer, reviewer],
        tasks=[analysis_task, drafting_task, validation_task],
        process=Process.sequential,
        verbose=True,
    )

    return crew