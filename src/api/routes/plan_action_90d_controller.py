from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from src.core.workflows.generate_action_plan_workflow import GenerateActionPlanWorkflow
from src.api.requests.plan_action_90d_request import PlanAction90dRequest
from src.core.tools.markdown_to_docx import convert_markdown_to_docx
import logging
import datetime as dt
import os
import tempfile

router = APIRouter(tags=["Plan Action 90d"])
logger = logging.getLogger(__name__)

@router.post("/plan-action-90d")
async def generate_plan_action_90d(request: PlanAction90dRequest):
    tmp_path = None
    try:
        workflow = GenerateActionPlanWorkflow()
        
        if not request.commercial_transcript or not request.onboarding_transcript or not request.discovery_transcript:
            raise HTTPException(
                status_code=400, 
                detail="É necessário fornecer a transcrição completa de todas as três reuniões"
            )
        
        # Gera a data atual no formato brasileiro
        current_date = dt.datetime.now().strftime("%d/%m/%Y")
        
        # Executa o workflow completo
        result = await workflow.execute(
            company_name=request.company_name,
            plan=request.plan,
            commercial_transcript=request.commercial_transcript,
            onboarding_transcript=request.onboarding_transcript,
            discovery_transcript=request.discovery_transcript,
            commercial_meeting=request.commercial_meeting,
            onboarding_meeting=request.onboarding_meeting,
            discovery_meeting=request.discovery_meeting,
            current_date=current_date
        )
        
        # Converte o markdown para DOCX
        docx_content = convert_markdown_to_docx(result["action_plan"], request.company_name)
        
        # Formata o nome do arquivo removendo caracteres especiais e espaços
        filename = f"plano_acao_90d_{request.company_name.lower().replace(' ', '_')}.docx"
        
        # Cria um arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
            tmp.write(docx_content)
            tmp_path = tmp.name
        
        # Retorna o arquivo
        return FileResponse(
            path=tmp_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar plano de ação de 90 dias: {str(e)}")
        # Limpa o arquivo temporário se houver erro
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar plano de ação: {str(e)}"
        )
    

@router.get("/test-docx")
async def test_docx():
    """
    Rota de teste que retorna um documento DOCX simples
    """
    try:
        # Cria um markdown simples para teste
        test_markdown = """
        # Documento de Teste

        Este é um documento de teste para verificar o download do DOCX.

        ## Seção 1
        - Item 1
        - Item 2
        - Item 3

        ## Seção 2
        Este é um parágrafo de teste.
        """
        # Converte para DOCX
        docx_content = convert_markdown_to_docx(test_markdown, "Teste")
        
        # Cria um arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
            tmp.write(docx_content)
            tmp_path = tmp.name
        
        # Retorna o arquivo
        return FileResponse(
            path=tmp_path,
            filename="teste.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        logger.error(f"Erro no teste DOCX: {str(e)}")
        # Limpa o arquivo temporário se houver erro
        if 'tmp_path' in locals():
            os.unlink(tmp_path)
        raise HTTPException(
            status_code=500,
            detail=f"Erro no teste: {str(e)}"
        )