from typing import List, Optional, Dict, Any, Literal, Union
from pydantic import BaseModel, Field, field_validator
from datetime import date


class ExtractionFieldSchema(BaseModel):
    """Schema for a single extraction field."""
    type: Literal["string", "date", "boolean", "number"] = Field(
        ..., description="Data type of the field"
    )
    description: str = Field(..., description="Human-readable description of the field")
    validation: Literal["required", "optional"] = Field(
        ..., description="Whether the field is required or optional"
    )
    confidence_threshold: float = Field(
        ..., ge=0.0, le=1.0, description="Minimum confidence threshold for extraction"
    )

    @field_validator("confidence_threshold")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("confidence_threshold must be between 0.0 and 1.0")
        return v


class QuestionFlowStep(BaseModel):
    """A single step/question in the call flow."""
    step: int = Field(..., ge=1, description="Step number in the flow")
    question: str = Field(..., description="The question to ask the caller")


class EscalationRule(BaseModel):
    """Rule for when to escalate to a human."""
    trigger: str = Field(..., description="Description of the trigger condition")
    action: Literal["transfer", "flag", "end_call"] = Field(
        default="transfer", description="Action to take on trigger"
    )


class DomainConfig(BaseModel):
    """Complete domain configuration for a call use case."""
    domain_id: str = Field(
        ..., pattern=r"^[a-z0-9-]+$", description="Unique identifier (kebab-case)"
    )
    name: str = Field(..., min_length=1, max_length=100, description="Human-readable name")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$", description="Semantic version")
    system_prompt: str = Field(
        ..., min_length=10, description="System prompt for the LLM agent"
    )
    mandatory_disclosure: str = Field(
        ..., min_length=10, description="Mandatory AI disclosure script (FR-11)"
    )
    question_flow: List[QuestionFlowStep] = Field(
        ..., min_length=1, description="Ordered list of questions to ask"
    )
    extraction_schema: Dict[str, ExtractionFieldSchema] = Field(
        ..., description="Fields to extract from the conversation"
    )
    escalation_rules: List[str] = Field(
        ..., min_length=1, description="Conditions that trigger human escalation"
    )
    fallback_responses: List[str] = Field(
        ..., min_length=1, description="Responses for unhandled/low-confidence turns"
    )

    @field_validator("question_flow")
    @classmethod
    def validate_step_order(cls, v: List[QuestionFlowStep]) -> List[QuestionFlowStep]:
        """Ensure steps are sequential starting from 1."""
        return ensure_sequential_steps(v)

    @field_validator("extraction_schema")
    @classmethod
    def validate_required_fields(cls, v: Dict[str, ExtractionFieldSchema]) -> Dict[str, ExtractionFieldSchema]:
        """Ensure required extraction fields are present for absent-student domain."""
        required_fields = {"reason_for_absence", "expected_return_date", "call_outcome"}
        missing = required_fields - set(v.keys())
        if missing:
            raise ValueError(f"Missing required extraction fields: {missing}")
        return v


def ensure_sequential_steps(steps: List["QuestionFlowStep"]) -> List["QuestionFlowStep"]:
    """Shared rule: flow steps must be numbered sequentially starting at 1."""
    expected_step = 1
    for step in steps:
        if step.step != expected_step:
            raise ValueError(
                f"question_flow steps must be sequential starting from 1. "
                f"Expected step {expected_step}, got {step.step}"
            )
        expected_step += 1
    return steps


class AgentVersionPayload(BaseModel):
    """Request schema for ``POST /api/agents/{id}/versions``.

    Reuses the structural rules of :class:`DomainConfig` (field schemas,
    sequential flow steps, prompt/disclosure minimum lengths) without its
    domain-specific required-fields rule — every call domain is valid here.
    """
    system_prompt: str = Field(..., min_length=10, description="System prompt for the LLM agent")
    company_context: Dict[str, Any] = Field(default_factory=dict)
    question_flow: List[QuestionFlowStep] = Field(
        ..., min_length=1, description="Ordered list of questions to ask"
    )
    extraction_schema: Dict[str, ExtractionFieldSchema] = Field(
        ..., description="Fields to extract from the conversation"
    )
    disclosure_script: str = Field(
        ..., min_length=10, description="Mandatory AI disclosure script (FR-11)"
    )
    escalation_rules: List[Union[str, EscalationRule]] = Field(
        ..., min_length=1, description="Conditions that trigger human escalation"
    )
    voice_settings: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("question_flow")
    @classmethod
    def validate_step_order(cls, v: List[QuestionFlowStep]) -> List[QuestionFlowStep]:
        """Ensure steps are sequential starting from 1 (shared legacy rule)."""
        return ensure_sequential_steps(v)


def validate_agent_version_payload(payload: Dict[str, Any]) -> AgentVersionPayload:
    """Validate an agent-version payload dictionary (raises pydantic ValidationError)."""
    return AgentVersionPayload(**payload)


def validate_domain_config(config: Dict[str, Any]) -> DomainConfig:
    """Validate a domain config dictionary and return a DomainConfig instance."""
    return DomainConfig(**config)


def validate_domain_config_file(file_path: str) -> DomainConfig:
    """Load and validate a domain config from a JSON file."""
    import json
    with open(file_path, "r") as f:
        config = json.load(f)
    return validate_domain_config(config)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        config = validate_domain_config_file(sys.argv[1])
        print(f"✓ Validated: {config.domain_id} v{config.version}")
        print(f"  Name: {config.name}")
        print(f"  Steps: {len(config.question_flow)}")
        print(f"  Extraction fields: {list(config.extraction_schema.keys())}")
    else:
        print("Usage: python domain_config_schema.py <path-to-config.json>")