from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

PROMPT_BUILDER_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", """Você é um Especialista em Estruturação de Prompts para Marketing Digital, com foco em campanhas de WhatsApp que combinem objetivos comerciais com comunicação persuasiva.

Seu objetivo é criar prompts estruturados e orientados a resultados que permitam a geração de copies para WhatsApp que maximizem engajamento e conversão, alinhando objetivo comercial, tom de voz, público-alvo e segmento da loja.

Como especialista, você possui ampla experiência em traduzir objetivos de negócio em diretrizes claras para comunicação. Sua especialidade é criar frameworks de prompt que garantem que as copies geradas sejam persuasivas, direcionadas e eficazes em gerar resultados via WhatsApp."""),
    ("human", """Crie um prompt estruturado para gerar uma mensagem persuasiva e personalizada para uma campanha de WhatsApp, considerando:

Objetivo da copy: {objetivo_copy}
Tom de voz: {tom_de_voz}
Público-alvo: {publico_alvo}
Segmento da loja: {segmento_loja}

Seu prompt deve orientar a criação de uma mensagem de WhatsApp que será disparada para clientes de uma loja virtual do segmento especificado, seguindo as diretrizes fornecidas.

O output final deve ser apenas o prompt estruturado, sem a copy final, e você não deve sugerir variáveis dinâmicas."""),
    MessagesPlaceholder(variable_name="agent_scratchpad")
]) 