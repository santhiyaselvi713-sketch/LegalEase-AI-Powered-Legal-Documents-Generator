from typing import Optional

from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):

    document_type: str = Field(
        ...,
        min_length=2,
        max_length=200
    )

    parties: str = Field(
        ...,
        min_length=2,
        max_length=10000
    )

    terms: str = Field(
        ...,
        min_length=2,
        max_length=20000
    )

    dates: str = Field(
        ...,
        min_length=2,
        max_length=500
    )

    jurisdiction: Optional[str] = Field(
        default="",
        max_length=500
    )

    language: str = Field(
        default="English",
        max_length=50
    )

    @field_validator(
        "document_type",
        "parties",
        "terms",
        "dates",
        "jurisdiction",
        "language"
    )
    @classmethod
    def clean_values(cls, value: str) -> str:
        return value.strip()


class DocumentResponse(BaseModel):

    document: str

    model: str

    ai_generated: bool

    warning: str


class HealthResponse(BaseModel):

    status: str

    service: str


class ExportRequest(BaseModel):

    document: str = Field(
        ...,
        min_length=1,
        max_length=50000
    )

    document_type: str = Field(
        ...,
        min_length=1,
        max_length=200
    )