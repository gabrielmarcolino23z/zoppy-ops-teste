from fastapi import APIRouter, Depends
from src.core.agents.linkedin_post_agent import LinkedInPostAgent
from src.config.settings import get_settings
from src.api.requests.linkedin_post_request import LinkedinPostRequest  

router = APIRouter()
settings = get_settings()

@router.post("/generate-post")
async def generate_post(request: LinkedinPostRequest):
    agent = LinkedInPostAgent()
    post = await agent.generate_post(request.url)  
    return {"post": post}