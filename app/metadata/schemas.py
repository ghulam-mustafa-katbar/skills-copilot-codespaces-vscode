"""Pydantic schemas for AI generated metadata."""

from pydantic import BaseModel, Field


class VideoMetadata(BaseModel):
    """SEO and upload metadata for a YouTube Short."""

    title: str = Field(min_length=5, max_length=100)
    description: str = Field(min_length=10, max_length=5000)
    tags: list[str] = Field(default_factory=list)
    hashtags: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    category: str = "Education"
    language: str = "en"
    visibility: str = "private"
