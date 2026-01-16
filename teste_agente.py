from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.youtube_reader import YouTubeReader
from agno.vectordb.pgvector import PgVector

# tools 
from agno.models.openai import OpenAIChat
from agno.tools.openai import OpenAITools
from agno.tools.duckduckgo import DuckDuckGoTools

# memory
from agno.db.postgres import PostgresDb



from dotenv import load_dotenv
import os

# 
load_dotenv()

# Verificação de segurança da API Key
if not os.getenv("OPENAI_API_KEY"):
    print("❌ Erro: OPENAI_API_KEY não encontrada no arquivo .env")
    exit()
# Verificação de segurança do DB postgres 
if not os.getenv("db_url"):
    print("❌ Erro: db_url não encontrada no arquivo .env")
    exit()

db_url = os.getenv("db_url")


# Create Knowledge Instance
knowledge_base = Knowledge(
    name="YouTube Knowledge Base",
    description="Knowledge base from YouTube video transcripts",
    vector_db=PgVector(
        table_name="youtube_vectors", 
        db_url=db_url
    ),
)


# Add YouTube video content synchronously
knowledge_base.add_content(
    metadata={"source": "youtube", "type": "educational"},
    #url="https://www.youtube.com/watch?v=6pJ4o3jJ2cU", # efap 368
    #url="https://www.youtube.com/watch?v=9H8EJLN9qXU", # efap 369
    url="https://www.youtube.com/watch?v=I8U6kjqLkJQ", # Randon Game of thrones
    skip_if_exists= True,

    reader=YouTubeReader(),
)
knowledge_base.add_content(
    metadata={"source": "youtube", "type": "educational"},
    url="https://www.youtube.com/watch?v=6pJ4o3jJ2cU",
    skip_if_exists= True,

    reader=YouTubeReader(),
)

knowledge_base.add_content(
    metadata={"source": "youtube", "type": "educational"},
    url="https://www.youtube.com/watch?v=9H8EJLN9qXU",
    skip_if_exists= True,

    reader=YouTubeReader(),
)
#knowledge_base.load(recreate=False) # não funciona na versão atual 

# Configura o armazenamento das conversas no mesmo banco do Docker
db = PostgresDb(
  db_url=db_url,
  memory_table="user_memories",  # Optionally specify a table name for the memories
)




# Create an agent with the knowledge
agent = Agent(
    model= OpenAIChat(id="gpt-5-nano",
                      instructions=[
                          "fale primeiro quais são os dados que existem em knowkedge",
                          "reconheça a diferença entre cada um dos locutores do podcast",
                          "Sempre diga se a informação veio do Knowledge Base ou da sua base de treinamento.",
                          "Se encontrar a resposta no Knowledge Base, cite trechos específicos.",
                          " Sabemos que os comentaristas que geralmente falam no podcast EFAP (everyframeapause ) são :Fringy,Rags,Mauler,The Little Platoon "

                          ]
                      ),
    tools=[OpenAITools(all),DuckDuckGoTools()],
    # acesso ao banco de dados
    knowledge=knowledge_base,
    search_knowledge=True,

    # acesso as conversas anteriores. para informar a resposta
    db=db,
    # Give the Agent the ability to update memories
    enable_agentic_memory=True,
    # OR - Run the MemoryManager automatically after each response
    enable_user_memories=True,


    markdown=True,
    debug_mode=True,
)

"""""
# Query the knowledge base
agent.print_response(
    "O que esta salvo em knowledge",
    markdown=True
)
"""""
while True:
    pergunta = input("\nVocê: ")
    if pergunta.lower() in ["sair", "exit", "quit"]:
        break
    
    # O agente processa a pergunta e busca no DuckDB
    agent.print_response(pergunta, stream=True)