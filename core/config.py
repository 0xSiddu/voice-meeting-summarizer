from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    Application Settings.
    This class loads environment variables from the .env file.
    It provides a centralized and type-safe way to access configuration.
    """
    
    # OpenAI API Key for Speech-to-Text and Summarization
    openai_api_key: str = Field(default="", description="OpenAI API Key")
    
    # ElevenLabs API Key for Text-to-Speech
    elevenlabs_api_key: str = Field(default="", description="ElevenLabs API Key")
    
    # Max size of an audio chunk in milliseconds (default: 10 minutes)
    chunk_threshold_ms: int = Field(default=600000, description="Chunk threshold in ms")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Ignore extra variables in .env that aren't defined here
    )

# Create a global settings object to be imported by other modules
settings = Settings()
