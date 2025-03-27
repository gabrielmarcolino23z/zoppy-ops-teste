"""
Script para indexar documentos da Zoppy e varejo para uso pelo agente de plano de ação de 90 dias.
Execute este script antes de iniciar a aplicação para garantir que o banco de dados vetorial
esteja atualizado.
"""
import logging
import sys
import os

# Configura o path do projeto corretamente
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from src.core.tools.index_zoppy_docs import ZoppyDocsIndexer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Função principal para indexar documentos"""
    logger.info("Iniciando indexação de documentos da Zoppy e varejo...")
    
    try:
        # Configura o caminho do vectorstorage
        vector_store_path = os.path.join(project_root, "data", "vectorstorage")
        
        # Garante que o diretório existe
        os.makedirs(vector_store_path, exist_ok=True)
        
        indexer = ZoppyDocsIndexer(vector_store_path=vector_store_path)
        indexer.index_documents()
        logger.info("Indexação concluída com sucesso!")
    except Exception as e:
        logger.error(f"Erro durante a indexação: {str(e)}")
        sys.exit(1)
    
    logger.info("Banco de dados vetorial criado e pronto para uso.")

if __name__ == "__main__":
    main()