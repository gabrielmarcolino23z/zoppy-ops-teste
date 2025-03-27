from fastapi import APIRouter, HTTPException, Depends
from langchain_openai import ChatOpenAI
import time
from uuid import uuid4

from src.config.settings import get_settings
from src.config.auth import get_current_user
from src.api.requests.copy_sms_request import CopySmsRequest
from src.api.response.copy_sms_response import CopySmsResponse
from src.core.workflows.copy_sms_workflow import CopySmsWorkflow

settings = get_settings()
router = APIRouter(tags=["copy-sms"])

@router.post("/generate/copy/sms", response_model=CopySmsResponse)
async def generate_copy_sms(
    request: CopySmsRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Endpoint para gerar copy para SMS
    """
    try:
        start_time = time.time()
        print(f"Usuário autenticado: {current_user.get('email')}")
        
        # Criando o modelo LLM
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL_NAME,
            temperature=0.7
        )
        
        # Criando e executando o workflow
        workflow = CopySmsWorkflow(llm=llm)
        result = await workflow.execute(
            objetivo_copy=request.objetivo_copy,
            tom_de_voz=request.tom_de_voz,
            publico_alvo=request.publico_alvo,
            segmento_loja=request.segmento_loja
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        return CopySmsResponse(
            run_id=result["run_id"],
            copy_text=result["copy_text"],
            tempo_execucao=result["tempo_execucao"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 