from pydantic import BaseModel

class CopyWppResponse(BaseModel):
    """
    Modelo de dados para resposta da geração de copy para WhatsApp
    """
    run_id: str
    copy_text: str
    tempo_execucao: str 