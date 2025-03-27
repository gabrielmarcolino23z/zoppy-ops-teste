from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class PlanAction90dResponse(BaseModel):
    """
    Modelo de resposta para o plano de ação de 90 dias
    """
    action_plan: str = Field(..., description="Plano de ação detalhado para os 90 primeiros dias")