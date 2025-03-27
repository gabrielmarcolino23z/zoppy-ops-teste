from pydantic import BaseModel

class CopySmsResponse(BaseModel):
    """
    Modelo de dados para resposta da geração de copy para SMS
    """
    run_id: str
    copy_text: str
    tempo_execucao: str 