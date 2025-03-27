# src/core/tools/index_zoppy_docs.py
import os
import glob
import logging
import random
from typing import List, Optional
from langchain_community.document_loaders import (
    DirectoryLoader, 
    TextLoader, 
    PDFMinerLoader,
    PyPDFLoader,
    CSVLoader,
    Docx2txtLoader,
    PyPDFLoader
)

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from src.config.settings import get_settings

logger = logging.getLogger(__name__)

class ZoppyDocsIndexer:
    """
    Classe para indexar documentos da Zoppy e criar um banco de dados vetorial
    para consulta pelo agente de plano de ação de 90 dias.
    """
    def __init__(self, vector_store_path: Optional[str] = None):
        self.settings = get_settings()
        
        # Configura o seed para reprodutibilidade
        if hasattr(self.settings, 'SEED'):
            random.seed(self.settings.SEED)
            logger.info(f"Seed configurado: {self.settings.SEED}")
        
        # Obtém o caminho raiz do projeto (2 níveis acima do arquivo atual)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        
        self.docs_directories = [
            # Diretórios com documentação da Zoppy a serem indexados
            os.path.join(project_root, "src/docs/zoppy"),
        ]
        
        # Define o caminho do banco vetorial
        if vector_store_path:
            self.vector_db_path = vector_store_path
        else:
            # Cria o diretório data/vectorstorage se não existir
            self.vector_db_path = os.path.join(project_root, "data", "vectorstorage")
            os.makedirs(self.vector_db_path, exist_ok=True)
            logger.info(f"Criando diretório do banco vetorial em: {self.vector_db_path}")
        
        self.chunk_size = 1000
        self.chunk_overlap = 200
        
        logger.info(f"Project root: {project_root}")
        logger.info(f"Diretórios de documentos configurados: {self.docs_directories}")
        logger.info(f"Vector DB path: {self.vector_db_path}")

    def load_documents(self) -> List[Document]:
        """
        Carrega documentos de múltiplos diretórios e formatos.
        
        Returns:
            List[Document]: Lista de documentos carregados
        """
        documents = []
        
        # Mapeamento de extensões de arquivo para loaders
        loaders_map = {
            ".txt": TextLoader,
            ".md": TextLoader,
            ".pdf": PyPDFLoader,
            ".csv": CSVLoader,
            ".docx": Docx2txtLoader
        }
        
        for directory in self.docs_directories:
            logger.info(f"Verificando diretório: {directory}")
            if not os.path.exists(directory):
                logger.warning(f"Diretório {directory} não encontrado. Caminho atual: {os.getcwd()}")
                continue
                
            logger.info(f"Carregando documentos do diretório: {directory}")
            
            # Carregar documentos de cada tipo de arquivo
            for ext, loader_cls in loaders_map.items():
                file_pattern = os.path.join(directory, f"**/*{ext}")
                logger.info(f"Buscando arquivos com padrão: {file_pattern}")
                files = glob.glob(file_pattern, recursive=True)
                
                if not files:
                    logger.info(f"Nenhum arquivo {ext} encontrado em {directory}")
                    continue
                    
                logger.info(f"Arquivos {ext} encontrados: {files}")
                for file_path in files:
                    try:
                        loader = loader_cls(file_path)
                        docs = loader.load()
                        logger.info(f"Carregado: {file_path} - {len(docs)} documentos")
                        documents.extend(docs)
                    except Exception as e:
                        logger.error(f"Erro ao carregar {file_path}: {str(e)}")
                        logger.exception(e)
        
        if not documents:
            logger.warning("Nenhum documento foi carregado! Verifique se os arquivos existem nos diretórios configurados.")
        else:
            logger.info(f"Total de documentos carregados: {len(documents)}")
        
        return documents

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Divide documentos em chunks menores para indexação.
        
        Args:
            documents: Lista de documentos a serem divididos
            
        Returns:
            List[Document]: Lista de documentos divididos
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        
        split_docs = text_splitter.split_documents(documents)
        logger.info(f"Documentos divididos em {len(split_docs)} chunks")
        return split_docs

    def create_vector_db(self, documents: List[Document]) -> Chroma:
        """
        Cria ou atualiza o banco de dados vetorial com os documentos.
        
        Args:
            documents: Lista de documentos a serem indexados
            
        Returns:
            Chroma: Instância do banco de dados vetorial
        """
        logger.info(f"Criando banco de dados vetorial em: {self.vector_db_path}")
        
        # Criar diretório para o banco vetorial se não existir
        os.makedirs(self.vector_db_path, exist_ok=True)
        
        # Inicializar embeddings da OpenAI
        embeddings = OpenAIEmbeddings(api_key=self.settings.OPENAI_API_KEY)
        
        # Criar ou atualizar o banco vetorial
        vectordb = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=self.vector_db_path
        )
        
        logger.info(f"Banco de dados vetorial criado com {len(documents)} documentos")
        
        return vectordb

    def index_documents(self) -> None:
        """
        Processo completo de indexação: carrega, divide e cria o banco vetorial.
        """
        try:
            # Carregar documentos
            documents = self.load_documents()
            if not documents:
                logger.warning("Nenhum documento encontrado para indexação")
                return
            
            # Dividir documentos em chunks
            split_documents = self.split_documents(documents)
            
            # Criar banco de dados vetorial
            self.create_vector_db(split_documents)
            
            logger.info("Indexação de documentos concluída com sucesso")
            
        except Exception as e:
            logger.error(f"Erro durante a indexação: {str(e)}")
            raise

def main():
    """Função principal para executar a indexação via linha de comando"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    indexer = ZoppyDocsIndexer()
    indexer.index_documents()

if __name__ == "__main__":
    main()