from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from typing import List, Dict
from src.config.settings import get_settings
from src.core.prompts.plan_action_90d_prompt import PLAN_ACTION_90D_PROMPT
import os
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

class PlanAction90dAgent:
    def __init__(self):
        self.settings = get_settings()
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.2,
            api_key=self.settings.OPENAI_API_KEY,
            seed=self.settings.SEED
        )
        
        # Configuração do vetor de documentos da Zoppy
        self.tools = self._setup_tools()
        self.agent = self._create_agent()

    def _setup_tools(self):
        """Configura as ferramentas para o agente, incluindo o retriever do banco vetorial"""
        tools = []
        
        # Inicializa o retriever para consulta de documentos da Zoppy
        try:
            # Obtém o caminho raiz do projeto
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
            vector_db_path = os.path.join(project_root, "data", "vectorstorage")
            print(f"Tentando acessar banco vetorial em: {vector_db_path}")
            
            # Garanta que o diretório exista
            os.makedirs(vector_db_path, exist_ok=True)
            
            # Carrega o banco de dados vetorial existente
            embeddings = OpenAIEmbeddings(api_key=self.settings.OPENAI_API_KEY)
            print(f"Inicializando Chroma com path: {vector_db_path}")
            vectordb = Chroma(
                persist_directory=vector_db_path,
                embedding_function=embeddings
            )
            
            # Mostra estatísticas sobre o banco
            collection = vectordb._collection
            print(f"Número de documentos no banco vetorial: {collection.count()}")
            
            # Configura compressor para extrair apenas informações relevantes
            compressor = LLMChainExtractor.from_llm(self.llm)
            
            # Cria um retriever com compressão contextual
            retriever = vectordb.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}  
            )
            compression_retriever = ContextualCompressionRetriever(
                base_compressor=compressor,
                base_retriever=retriever,
                document_compressor_kwargs={"top_n": 3} 
            )
            
            # Cria ferramenta de recuperação de documentos
            retriever_tool = create_retriever_tool(
                retriever=compression_retriever,
                name="zoppy_knowledge_base",
                description="Útil para buscar informações sobre a Zoppy, suas funcionalidades, integrações e melhores práticas para varejistas. Use esta ferramenta múltiplas vezes conforme necessário para obter informações detalhadas sobre diferentes aspectos da plataforma. Além de datas comemorativas, você pode usar esta ferramenta para buscar informações sobre eventos, datas especiais e sazonalidades relevantes para o segmento do cliente."
            )
            
            tools.append(retriever_tool)
            print("Ferramenta de recuperação de documentos criada com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar o banco vetorial: {e}")
            import traceback
            traceback.print_exc()
            print("Continuando sem a ferramenta de recuperação de documentos.")
        
        return tools

    def _create_agent(self):
        """Cria o agente com o prompt e ferramentas configuradas"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", PLAN_ACTION_90D_PROMPT),
            ("human", "Nome do Cliente: {company_name}\n\nReunião Comercial: {commercial_meeting}\n\nReunião de Onboarding: {onboarding_meeting}\n\nReunião de Discovery: {discovery_meeting}\n\nResumo do status do cliente: {company_status}\n\nPlano contratado: {plan}\n\nData Atual: {current_date}\n\nGere o plano de ação para os 90 primeiros dias:"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])

        return create_tool_calling_agent(self.llm, self.tools, prompt)

    async def generate_action_plan(self,  
                                company_name: str,
                                plan: str,
                                commercial_meeting: List[Dict[str, str]], 
                                onboarding_meeting: List[Dict[str, str]],
                                discovery_meeting: List[Dict[str, str]],
                                company_status: str,
                                current_date: str) -> str:
        """
        Gera um plano de ação para os 90 primeiros dias do cliente.
        
        Args:
            company_name: Nome do cliente
            plan: Plano do cliente
            commercial_meeting: Lista de perguntas e respostas da reunião comercial
            onboarding_meeting: Lista de perguntas e respostas da reunião de onboarding
            discovery_meeting: Lista de perguntas e respostas da reunião de discovery
            company_status: Status detalhado do cliente gerado pelo CompanyStatusAgent
            current_date: Data atual
            
        Returns:
            str: Plano de ação detalhado para os 90 primeiros dias
        """
        agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,  # Permite mais iterações para múltiplas consultas
            early_stopping_method="generate",  # Permite que o agente decida quando parar
            handle_parsing_errors=True  # Lida melhor com erros de parsing
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
                    "commercial_meeting": commercial_meeting,
                    "onboarding_meeting": onboarding_meeting,
                    "discovery_meeting": discovery_meeting,
                    "company_status": company_status,
                    "current_date": current_date
                })
            except (RateLimitError, APIError) as e:
                print(f"Rate limit atingido. Aguardando antes de tentar novamente: {str(e)}")
                time.sleep(1)  # Pausa mínima antes do backoff
                raise
        
        # Executa com retry
        result = await execute_with_retry()
        
        return result["output"]