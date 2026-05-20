import json
from openai import AsyncOpenAI
from core.config import settings
from models.schemas import LLMSummaryOutput

client = AsyncOpenAI(api_key=settings.openai_api_key)

async def summarize_transcript(transcript: str) -> LLMSummaryOutput:
    """
    Takes the full text transcript of the meeting and asks the LLM
    to extract specific pieces of information.
    
    Args:
        transcript (str): The full text of the meeting.
        
    Returns:
        LLMSummaryOutput: A structured response containing key points, 
                          action items, decisions, and an executive summary.
    """
    
    # We use a system prompt to tell the AI how it should behave.
    system_prompt = (
        "You are an expert executive assistant. Your job is to read a meeting transcript "
        "and provide a highly accurate, structured summary. Extract the key discussion points, "
        "action items with assignees if mentioned, any formal decisions made, and a brief "
        "executive summary of the entire meeting."
    )
    
    try:
        # We use the new "Structured Outputs" feature of OpenAI by passing
        # the Pydantic model to `response_format`. This guarantees the LLM 
        # returns data that perfectly matches our LLMSummaryOutput model.
        response = await client.beta.chat.completions.parse(
            model="gpt-4o-mini", # Cost-effective and fast model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here is the transcript:\n\n{transcript}"}
            ],
            response_format=LLMSummaryOutput,
        )
        
        # Extract the parsed object
        summary = response.choices[0].message.parsed
        return summary
        
    except Exception as e:
        raise Exception(f"Failed to summarize transcript: {str(e)}")
