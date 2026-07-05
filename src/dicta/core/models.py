"""Pydantic contracts for the Dicta semantic kernel."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from dicta.core.qualification import QualificationStrength


class Datum(BaseModel):
    """Received material before meaning is settled."""

    model_config = ConfigDict(extra="forbid")

    value: Any = Field(description="Received material before meaning is settled.")
    source: str | None = Field(default=None, description="Where the datum came from.")
    note: str | None = Field(default=None, description="Optional contextual note.")


class Qualification(BaseModel):
    """How a Dictum stands."""

    model_config = ConfigDict(extra="forbid")

    strength: QualificationStrength = Field(default=QualificationStrength.ASSERTED)
    basis: str = Field(default="")
    conditions: list[str] = Field(default_factory=list)
    timing: str | None = Field(default=None)


class Dictum(BaseModel):
    """Bounded statement of meaning."""

    model_config = ConfigDict(extra="forbid")

    subject: str
    meaning: str
    qualification: Qualification = Field(default_factory=Qualification)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Purpose(BaseModel):
    """Direction of a Concept."""

    model_config = ConfigDict(extra="forbid")

    statement: str
    mode: str = Field(default="general")


class Concept(BaseModel):
    """Bounded structure of qualified Dicta."""

    model_config = ConfigDict(extra="forbid")

    name: str
    dicta: list[Dictum] = Field(default_factory=list)
    purpose: Purpose | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Disparity(BaseModel):
    """Meaningful gap revealed under Purpose."""

    model_config = ConfigDict(extra="forbid")

    datum: Datum
    concept: Concept
    purpose: Purpose
    description: str
    severity: str = Field(default="noted")


class Inference(BaseModel):
    """What follows from qualified meaning under Purpose."""

    model_config = ConfigDict(extra="forbid")

    from_disparity: Disparity
    derived: str
    basis: str = Field(default="")


class Outcome(BaseModel):
    """What actually resulted."""

    model_config = ConfigDict(extra="forbid")

    inference: Inference
    result: Any
    status: str = Field(default="observed")


class Revision(BaseModel):
    """Appraised change to a Program's Concept after Outcome."""

    model_config = ConfigDict(extra="forbid")

    outcome: Outcome
    changes: list[str] = Field(default_factory=list)
    note: str | None = None


class Program(BaseModel):
    """Purposeful Concept in motion."""

    model_config = ConfigDict(extra="forbid")

    name: str
    concept: Concept
    history: list[Revision] = Field(default_factory=list)
