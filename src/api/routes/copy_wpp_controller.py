import os
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from src.config.auth import get_current_user
from src.config.settings import get_settings
from src.core.workflows.copy_wpp_workflow import CopyWhatsappWorkflow
from src.api.requests.copy_wpp_request import CopyWppRequest
from src.api.response.copy_wpp_response import CopyWppResponse
from dotenv import load_dotenv
import time
from uuid import uuid4

load_dotenv()

settings = get_settings()
router = APIRouter(tags=["copy-wpp"])

@router.post("/generate/copy/whatsapp", response_model=CopyWppResponse)
async def generate_copy_whatsapp(
    request: CopyWppRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Endpoint para gerar copy para WhatsApp
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
        workflow = CopyWhatsappWorkflow(llm=llm)
        result = await workflow.execute(
            objetivo_copy=request.objetivo_copy,
            tom_de_voz=request.tom_de_voz,
            publico_alvo=request.publico_alvo,
            segmento_loja=request.segmento_loja
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        return CopyWppResponse(
            run_id=result["run_id"],
            copy_text=result["copy_text"],
            tempo_execucao=result["tempo_execucao"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 