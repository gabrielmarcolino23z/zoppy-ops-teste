from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Dict
from src.config.settings import get_settings
from src.core.prompts.company_status_prompt import COMPANY_STATUS_PROMPT
import backoff
import time
from openai import RateLimitError, APIError

class CompanyStatusAgent:
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
        prompt = ChatPromptTemplate.from_messages([
            ("system", COMPANY_STATUS_PROMPT),
            ("human", "Nome do Cliente: {company_name}\n\nPlano: {plan}\n\nTranscrição da Reunião Comercial: {commercial_transcript}\n\nTranscrição da Reunião de Onboarding: {onboarding_transcript}\n\nTranscrição da Reunião de Discovery: {discovery_transcript}\n\nAnalise as transcrições e gere o status detalhado do cliente:"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        return create_tool_calling_agent(self.llm, [], prompt)

    async def generate_company_status(self,
                                    company_name: str,
                                    plan: str,
                                    commercial_transcript: str,
                                    onboarding_transcript: str,
                                    discovery_transcript: str) -> str:
        """
        Gera um status detalhado do cliente baseado nas transcrições das reuniões.
        
        Args:
            company_name: Nome do cliente
            plan: Plano do cliente
            commercial_transcript: Transcrição completa da reunião comercial
            onboarding_transcript: Transcrição completa da reunião de onboarding
            discovery_transcript: Transcrição completa da reunião de discovery
            
        Returns:
            str: Status detalhado do cliente incluindo restrições técnicas, preferências operacionais,
                 maturidade digital, desafios específicos e recomendações de implementação
        """
        agent_executor = AgentExecutor(
            agent=self.agent,
            tools=[],
            verbose=True,
            max_iterations=3,
            early_stopping_method="generate",
            handle_parsing_errors=True
        )
        
        # Implementa retry para lidar com rate limits
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
                    "company_name": company_name,
                    "plan": plan,
                    "commercial_transcript": commercial_transcript,
                    "onboarding_transcript": onboarding_transcript,
                    "discovery_transcript": discovery_transcript
                })
            except (RateLimitError, APIError) as e:
                print(f"Rate limit atingido. Aguardando antes de tentar novamente: {str(e)}")
                time.sleep(1)  # Pausa mínima antes do backoff
                raise
        
        # Executa com retry
        result = await execute_with_retry()
        
        return result["output"] 