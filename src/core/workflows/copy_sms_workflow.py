from typing import Dict, Any
import time
import uuid
from langchain_core.language_models import BaseChatModel
from src.core.agents.prompt_builder_sms_agent import PromptBuilderSmsAgent
from src.core.agents.variable_suggester_sms_agent import VariableSuggesterSmsAgent
from src.core.agents.copywriter_sms_agent import CopywriterSmsAgent
from src.core.utils.langsmith_helper import LangSmithHelper, FeatureType


class CopySmsWorkflow:
    """
    Classe principal que gerencia o workflow de geração de copy para SMS
    """
    
    def __init__(self, llm: BaseChatModel = None):
        # Define o projeto LangSmith específico para esta feature
        LangSmithHelper.set_project_env(FeatureType.COPY_SMS)
        
        self.prompt_builder = PromptBuilderSmsAgent()
        self.variable_suggester = VariableSuggesterSmsAgent()
        self.copywriter = CopywriterSmsAgent()
    
    async def execute(self, 
                     objetivo_copy: str,
                     tom_de_voz: str,
                     publico_alvo: str,
                     segmento_loja: str) -> Dict[str, Any]:
        """
        Executa o workflow completo de geração de copy para SMS
        
        Args:
            objetivo_copy: Objetivo principal da mensagem
            tom_de_voz: Tom de voz a ser utilizado (formal, informal, etc)
            publico_alvo: Descrição do público-alvo
            segmento_loja: Segmento da loja (ex: moda, eletrônicos, cosméticos)
            
        Returns:
            Dict[str, Any]: Dicionário contendo o run_id, copy final e tempo de execução
        """
        # Inicia o timer
        start_time = time.time()
        
        run_id = str(uuid.uuid4())
        
        prompt_formatado = await self.prompt_builder.generate_prompt(
            objetivo_copy=objetivo_copy,
            tom_de_voz=tom_de_voz,
            publico_alvo=publico_alvo,
            segmento_loja=segmento_loja
        )

        variaveis_sugeridas = await self.variable_suggester.suggest_variables(
            prompt_formatado=prompt_formatado,
            objetivo_copy=objetivo_copy,
            tom_de_voz=tom_de_voz,
            publico_alvo=publico_alvo,
            segmento_loja=segmento_loja
        )
        
        copy_text = await self.copywriter.generate_copy(
            prompt_formatado=prompt_formatado,
            variaveis_sugeridas=variaveis_sugeridas
        )
        
        execution_time = round(time.time() - start_time, 2)
        
        # Restaura o projeto LangSmith para o valor padrão ao finalizar
        LangSmithHelper.reset_project_env()
        
        # Retorna o resultado no formato esperado
        return {
            "run_id": run_id,
            "copy_text": copy_text,
            "tempo_execucao": f"{execution_time}s"
        } 