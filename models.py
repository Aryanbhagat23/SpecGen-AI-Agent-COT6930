from pydantic import BaseModel, Field
from typing import List

class Specification(BaseModel):
    """
    Data model for the generated specification.
    """
    high_level_stories: List[str] = Field(
        description="List of user stories decomposed from the feature goal",
        min_length=3
    )
    detailed_spec_markdown: str = Field(
        description="Complete specification document in markdown format with FRs, NFRs, and acceptance criteria"
    )
    validation_status: str = Field(
        default="Validated",
        description="Status of validation: 'Validated' or 'Needs Revision'"
    )
    validation_critique: str = Field(
        default="All requirements meet quality standards.",
        description="Quality feedback from validation agent"
    )

    class Config:
        # Configuration for Pydantic to handle the model correctly
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "high_level_stories": [
                    "As a user, I want to manage my profile settings easily.",
                    "As an admin, I need to approve new user accounts."
                ],
                "detailed_spec_markdown": "# Software Specification\n\n## 1. Introduction...",
                "validation_status": "Validated",
                "validation_critique": "All requirements are clear, testable, and follow GIVEN/WHEN/THEN format."
            }
        }