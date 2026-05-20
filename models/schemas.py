from pydantic import BaseModel
from typing import List

class SummaryResponse(BaseModel):
    """
    This defines the structure of the data we will return to the user.
    Pydantic ensures that our API always returns data in this exact format.
    """
    key_points: List[str]
    action_items: List[str]
    decisions_made: List[str]
    executive_summary: str
    audio_summary_url: str  # We will return the URL/path where the audio file is saved

class LLMSummaryOutput(BaseModel):
    """
    This defines the structure we expect the LLM to return.
    It does not include the audio_summary_url yet, because we get this from the LLM first.
    """
    key_points: List[str]
    action_items: List[str]
    decisions_made: List[str]
    executive_summary: str
