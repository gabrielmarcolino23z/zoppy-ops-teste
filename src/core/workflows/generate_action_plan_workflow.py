from typing import List, Dict
from src.core.agents.company_status_agent import CompanyStatusAgent
from src.core.agents.plan_action_90d_agent import PlanAction90dAgent
from src.core.utils.langsmith_helper import LangSmithHelper, FeatureType

class GenerateActionPlanWorkflow:
    def __init__(self):
        # Define o projeto LangSmith específico para esta feature
        LangSmithHelper.set_project_env(FeatureType.PLAN_ACTION_90D)
        
        self.company_status_agent = CompanyStatusAgent()
        self.plan_action_90d_agent = PlanAction90dAgent()

    async def execute(self,
                     company_name: str,
                     plan: str,
                     commercial_transcript: str,
                     onboarding_transcript: str,
                     discovery_transcript: str,
                     commercial_meeting: List[Dict[str, str]],
                     onboarding_meeting: List[Dict[str, str]],
                     discovery_meeting: List[Dict[str, str]],
                     current_date: str) -> Dict[str, str]:
        """
        Executa o fluxo completo de geração do plano de ação para os 90 primeiros dias.
        
        Args:
            company_name: Nome do cliente
            plan: Plano do cliente
            commercial_transcript: Transcrição completa da reunião comercial
            onboarding_transcript: Transcrição completa da reunião de onboarding
            discovery_transcript: Transcrição completa da reunião de discovery
            commercial_meeting: Lista de perguntas e respostas da reunião comercial
            onboarding_meeting: Lista de perguntas e respostas da reunião de onboarding
            discovery_meeting: Lista de perguntas e respostas da reunião de discovery
            current_date: Data atual
            
        Returns:
            Dict[str, str]: Dicionário contendo:
                - company_status: Status detalhado do cliente
                - action_plan: Plano de ação para os 90 primeiros dias
        """
        # 1. Gera o status do cliente usando o CompanyStatusAgent com as transcrições completas
        company_status = await self.company_status_agent.generate_company_status(
            company_name=company_name,
            plan=plan,
            commercial_transcript=commercial_transcript,
            onboarding_transcript=onboarding_transcript,
            discovery_transcript=discovery_transcript
        )
        
        # 2. Gera o plano de ação usando o PlanAction90dAgent com os dados estruturados
        action_plan = await self.plan_action_90d_agent.generate_action_plan(
            company_name=company_name,
            plan=plan,
            commercial_meeting=commercial_meeting,
            onboarding_meeting=onboarding_meeting,
            discovery_meeting=discovery_meeting,
            company_status=company_status,
            current_date=current_date
        )
        
        # Restaura o projeto LangSmith para o valor padrão ao finalizar
        LangSmithHelper.reset_project_env()
        
        return {
            "company_status": company_status,
            "action_plan": action_plan
        } 