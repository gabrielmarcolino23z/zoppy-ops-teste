from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from typing import Dict
from src.config.settings import get_settings
from src.core.prompts.copywriter_prompt import COPYWRITER_TEMPLATE
import backoff
import time
from openai import RateLimitError, APIError

# Função auxiliar com retry para operações com OpenAI
@backoff.on_exception(
    backoff.expo,
    (RateLimitError, APIError),
    max_tries=8,
    factor=2,
    jitter=backoff.full_jitter
)
def with_retry(func, *args, **kwargs):
    """Executa uma função com retry usando backoff exponencial para erros de rate limit"""
    try:
        return func(*args, **kwargs)
    except (RateLimitError, APIError) as e:
        print(f"OpenAI API error: {str(e)}. Aguardando antes de tentar novamente...")
        time.sleep(1)  # Pausa mínima antes do backoff
        raise

class CopywriterAgent:
    def __init__(self):
        self.settings = get_settings()
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.2,
            api_key=self.settings.OPENAI_API_KEY,
            seed=self.settings.SEED
        )
        self.agent = self._create_agent()

    def _create_agent(self):
        """Cria o agente com o prompt configurado"""
        return create_tool_calling_agent(self.llm, [], COPYWRITER_TEMPLATE)

    async def generate_copy(self, 
                          prompt_formatado: str,
                          variaveis_sugeridas: str) -> str:
        """
        Gera o copy final para WhatsApp.
        
        Args:
            prompt_formatado: Prompt detalhado gerado pelo PromptBuilderAgent
            variaveis_sugeridas: Variáveis sugeridas pelo VariableSuggesterAgent
            
        Returns:
            str: Copy final para WhatsApp
        """
        agent_executor = AgentExecutor(
            agent=self.agent,
            tools=[],
            verbose=True,
            max_iterations=3,
            early_stopping_method="generate",
            handle_parsing_errors=True
        )
        
        @backoff.on_exception(
            backoff.expo,
            (RateLimitError, APIError),
            max_tries=8,
            factor=2,
            jitter=backoff.full_jitter
        )
        async def execute_with_retry():
            try:
                return await agent_executor.ainvoke({
                    "prompt_formatado": prompt_formatado,
                    "variaveis_sugeridas": variaveis_sugeridas
                })
            except (RateLimitError, APIError) as e:
                print(f"Rate limit atingido. Aguardando antes de tentar novamente: {str(e)}")
                time.sleep(1)
                raise
        
        result = await execute_with_retry()
        return result["output"] 