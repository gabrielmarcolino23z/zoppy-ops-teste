from pydantic import BaseModel

class CopyWppRequest(BaseModel):
    """
    Modelo de dados para requisição de geração de copy para WhatsApp
    """
    objetivo_copy: str
    tom_de_voz: str
    publico_alvo: str 
    segmento_loja: str

