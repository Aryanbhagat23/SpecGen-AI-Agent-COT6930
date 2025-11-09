from pydantic import BaseModel, Field

class Specification(BaseModel):
    """
    A strictly structured Pydantic model for the final feature specification document,
    including the audit trail for academic reporting.
    """
    feature_goal: str = Field(
        description="The original high-level feature goal provided by the user."
    )
    high_level_stories: list[str] = Field(
        description="A list of 5-8 atomic user needs/problems derived from the goal."
    )
    detailed_spec_markdown: str = Field(
        description="The complete, final, and validated specification document in detailed Markdown format. MUST include sections for Functional Requirements, Non-Functional Requirements, and GIVEN/WHEN/THEN clauses."
    )
    validation_status: str = Field(
        description="The final audit status. Must be 'Validated' or 'Needs Refinement: [Reason]'."
    )
    validation_critique: str = Field(
        description="The Validation Agent's full reasoning log, detailing the checks performed (Testability, Consistency, Completeness) and the final decision."
    )