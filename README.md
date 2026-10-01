# Ingestão e Busca Semântica com LangChain e PostgreSQL

Projeto do desafio de Ingestão e Busca Semântica com LangChain e pgVector. O sistema lê um PDF, divide o conteúdo em chunks de 1000 caracteres com overlap de 150, gera embeddings e persiste os vetores em PostgreSQL com pgVector. Depois, permite perguntas pelo terminal e gera respostas usando somente os chunks recuperados.

## Stack

- Python 3.11+
- LangChain
- PostgreSQL 17 + pgVector
- Docker Compose
- OpenAI embeddings: `text-embedding-3-small`
- OpenAI LLM: configurável por `OPENAI_CHAT_MODEL`

## Pré-requisitos

- Python 3.11+
- Docker + Docker Compose v2
- Uma API Key da OpenAI

## Configuração

Crie o ambiente virtual e instale as dependências:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copie `.env.example` para `.env` e preencha:

```env
OPENAI_API_KEY=sua-chave-aqui
```

O exemplo usa `gpt-5.6-sol` como modelo de chat. O modelo pode ser alterado pela variável `OPENAI_CHAT_MODEL` conforme os modelos disponíveis para a sua conta/API.

Substitua o `document.pdf` de exemplo pelo PDF real do desafio.

## Execução

Suba o PostgreSQL:

```bash
docker compose up -d
```

O arquivo `init.sql` cria automaticamente a extensão `vector` na inicialização do PostgreSQL.

Faça a ingestão:

```bash
python src/ingest.py
```

Execute o chat:

```bash
python src/chat.py
```

## Ingestão

A ingestão executa:

1. `PyPDFLoader` para ler o PDF;
2. `RecursiveCharacterTextSplitter` com `chunk_size=1000` e `chunk_overlap=150`;
3. embeddings para cada chunk;
4. persistência no PostgreSQL usando `PGVector`.

Por padrão, `RESET_COLLECTION=true`, então uma nova ingestão recria a collection antes de inserir os chunks.

## Busca e chat

Para cada pergunta, `src/search.py` chama:

```python
similarity_search_with_score(query, k=10)
```

Os 10 chunks recuperados são enviados à LLM junto com o prompt do desafio. O prompt restringe a resposta ao contexto recuperado e exige exatamente:

```text
Não tenho informações necessárias para responder sua pergunta.
```

quando a informação solicitada não estiver explicitamente disponível no contexto.

## Reiniciar o banco

```bash
docker compose down -v
docker compose up -d
python src/ingest.py
```

## Segurança

Nunca faça commit do arquivo `.env`. A chave da OpenAI deve permanecer somente no ambiente local.

## Estrutura

```text
├── docker-compose.yml
├── init.sql
├── requirements.txt
├── .env.example
├── src/
│   ├── ingest.py
│   ├── search.py
│   └── chat.py
├── document.pdf
└── README.md
```
