from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "This blueprint outlines the development of a state-of-the-art solution for: 'create a whatsapp'. Designed with modern scalability, security, and modularity in mind, the system leverages FastAPI, React, TailwindCSS and a PostgreSQL database to deliver a seamless user experience."
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite+aiosqlite:///./aether.db"
    
    class Config:
        case_sensitive = True

settings = Settings()
