# src/core/agents/linkedin_post_agent.py
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper  
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.config.settings import get_settings
from src.core.utils.langsmith_helper import LangSmithHelper, FeatureType

class LinkedInPostAgent:
    def __init__(self, set_project: bool = True):
        self.settings = get_settings()
        
        # Configura o projeto LangSmith se solicitado
        if set_project:
            LangSmithHelper.set_project_env(FeatureType.LINKEDIN_POST)
            
        self.llm = ChatOpenAI(model="gpt-4o",
                            temperature=0.7,
                            api_key=self.settings.OPENAI_API_KEY)
        
        self.tools = [self._setup_tavily()]
        self.agent = self._create_agent()

    def _setup_tavily(self):
        tavily_api_wrapper = TavilySearchAPIWrapper(tavily_api_key=self.settings.TAVILY_API_KEY)
        return TavilySearchResults(api_wrapper=tavily_api_wrapper)

    def _create_agent(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um especialista em criar posts para LinkedIn.
            Seu objetivo é gerar conteúdo profissional, informativo e engajante que seja relevante para a audiência de negócios.
            Utilize informações atualizadas e precisas. Caso necessário, realize pesquisas para fundamentar o conteúdo."""),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        return create_tool_calling_agent(self.llm, self.tools, prompt)

    async def generate_post(self, topic: str, tone: str, audience: str, include_hashtags: bool = True):
        """
        Gera um post para LinkedIn sobre o tópico especificado.
        
        Args:
            topic: Tópico principal do post
            tone: Tom desejado (profissional, inspirador, educativo, etc.)
            audience: Público-alvo do post
            include_hashtags: Se deve incluir hashtags relevantes
            
        Returns:
            str: Post formatado para LinkedIn
        """
        agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
        
        result = await agent_executor.ainvoke({
            "messages": [
                {
                    "role": "user",
                    "content": f"""Crie um post para LinkedIn sobre o tópico: {topic}.
                    
                    Tom desejado: {tone}
                    Público-alvo: {audience}
                    Incluir hashtags: {"Sim" if include_hashtags else "Não"}
                    
                    O post deve ser bem estruturado, profissional e encorajar engajamento.
                    Se necessário, faça uma pesquisa para garantir informações precisas e atualizadas.
                    """
                }
            ]
        })
        
        # Restaura o projeto LangSmith se foi alterado
        LangSmithHelper.reset_project_env()
        
        return result["output"]