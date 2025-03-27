from src.config.settings import get_settings
from enum import Enum
import os
import re

class FeatureType(Enum):
    COPY_WPP = "copy_wpp"
    COPY_SMS = "copy_sms"
    LINKEDIN_POST = "linkedin_post"
    PLAN_ACTION_90D = "plan_action_90d"
    COMPANY_STATUS = "company_status"
    GENERAL = "general"

class LangSmithHelper:
    """
    Classe auxiliar para gerenciar os projetos do LangSmith de acordo com a feature.
    """
    
    @staticmethod
    def get_project_name(feature_type: FeatureType) -> str:
        """
        Obtém o nome do projeto LangSmith com base na feature.
        
        Args:
            feature_type: Tipo de feature
            
        Returns:
            str: Nome do projeto no LangSmith
        """
        settings = get_settings()
        base_project = settings.LANGSMITH_PROJECT
        
        # Se a variável de ambiente for vazia, usa um valor padrão
        if not base_project:
            base_project = "zoppy-copy-ai-local"
        
        # Não adicionar sufixo da feature se já existir
        feature_suffix = f"-{feature_type.value}"
        if not base_project.endswith(feature_suffix):
            return f"{base_project}{feature_suffix}"
        
        return base_project
    
    @staticmethod
    def set_project_env(feature_type: FeatureType) -> None:
        """
        Define a variável de ambiente LANGSMITH_PROJECT para a feature específica.
        Isso afetará todos os agentes subsequentes criados.
        
        Args:
            feature_type: Tipo de feature
        """
        project_name = LangSmithHelper.get_project_name(feature_type)
        
        # Configura tanto LANGSMITH_PROJECT quanto LANGCHAIN_PROJECT para compatibilidade
        os.environ["LANGSMITH_PROJECT"] = project_name
        os.environ["LANGCHAIN_PROJECT"] = project_name
        
        print(f"Projeto do LangSmith definido para: {project_name}")
        
    @staticmethod
    def reset_project_env() -> None:
        """
        Redefine a variável de ambiente LANGSMITH_PROJECT para o valor padrão.
        """
        settings = get_settings()
        base_project = settings.LANGSMITH_PROJECT
        
        # Redefine as variáveis de ambiente para o projeto base
        os.environ["LANGSMITH_PROJECT"] = base_project
        os.environ["LANGCHAIN_PROJECT"] = base_project 