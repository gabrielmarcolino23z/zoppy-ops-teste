from pydantic import BaseModel

class LinkedinPostRequest(BaseModel):
    url: str
