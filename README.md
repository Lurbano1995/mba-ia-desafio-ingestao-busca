# Ingestão e Busca Semântica com LangChain e PostgreSQL

Projeto do desafio de Ingestão e Busca Semântica com LangChain e pgVector. O sistema lê um PDF, divide o conteúdo em chunks de 1000 caracteres com overlap de 150, gera embeddings e persiste os vetores em PostgreSQL com pgVector. Depois, permite perguntas pelo terminal e gera respostas usando somente os chunks recuperados.

## Arquitetura

```text
                 ┌─────────────────┐
                 │   document.pdf  │
                 └────────┬────────┘
                          │ PyPDFLoader
                          ▼
                 ┌─────────────────┐
                 │ Text Splitter   │
                 │ 1000 / overlap  │
                 │      150        │
                 └────────┬────────┘
                          │ embeddings
                          ▼
                 ┌─────────────────┐
                 │ PostgreSQL      │
                 │ + pgVector      │
                 └────────┬────────┘
                          │ top 10
                          ▼
                 ┌─────────────────┐
 PERGUNTA ──────►│ LangChain       │
                 │ + LLM           │
                 └────────┬────────┘
                          ▼
                       RESPOSTA
```

## Stack

- Python
- LangChain
- PostgreSQL 17
- pgVector
- Docker Compose
- OpenAI embeddings: `text-embedding-3-small`
- OpenAI LLM: configurável por `OPENAI_CHAT_MODEL`

## Pré-requisitos

- Python 3.11+
- Docker + Docker Compose v2
- Uma API Key da OpenAI

## 1. Criar o ambiente virtual

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## 2. Configurar as variáveis

```bash
cp .env.example .env
```

No Windows, crie uma cópia de `.env.example` chamada `.env`.

Preencha pelo menos:

```env
OPENAI_API_KEY=sua-chave-aqui
```

O projeto usa por padrão:

```env
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-5.6-luna
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=pdf_documents
PDF_PATH=document.pdf
RESET_COLLECTION=true
```

Os modelos podem ser alterados sem modificar o código. Se trocar o modelo de embeddings depois da primeira ingestão, apague a collection/volume e faça a ingestão novamente, pois a dimensão dos vetores pode mudar.

## 3. Colocar o PDF

Substitua o `document.pdf` da raiz pelo PDF que será usado no desafio. O caminho pode ser alterado com `PDF_PATH`.

## 4. Subir PostgreSQL + pgVector

```bash
docker compose up -d
```

Confira os containers:

```bash
docker compose ps
```

O serviço `bootstrap_vector_ext` cria a extensão `vector` automaticamente depois que o PostgreSQL estiver saudável.

## 5. Fazer a ingestão

```bash
python src/ingest.py
```

A ingestão executa:

1. `PyPDFLoader` para ler o PDF;
2. `RecursiveCharacterTextSplitter` com `chunk_size=1000` e `chunk_overlap=150`;
3. embeddings OpenAI para cada chunk;
4. persistência no PostgreSQL usando `PGVector`.

Por padrão `RESET_COLLECTION=true`, então uma nova ingestão recria a collection antes de inserir os chunks e evita duplicação durante testes.

## 6. Rodar o chat

```bash
python src/chat.py
```

Exemplo:

```text
Busca semântica no PDF
Digite 'sair' para encerrar.

PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.

PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

## Como a busca funciona

Para cada pergunta, `src/search.py` chama:

```python
similarity_search_with_score(query, k=10)
```

Os 10 chunks recuperados são concatenados e enviados à LLM junto com o prompt obrigatório do desafio. A LLM recebe uma instrução explícita para não usar conhecimento externo e retornar a frase de fallback quando a informação não estiver explicitamente no contexto.

## Observação sobre o score

O valor retornado por `similarity_search_with_score` é mantido apenas como metadado de diagnóstico. Não há um threshold arbitrário no código porque o enunciado determina que a consulta deve recuperar `k=10`; a decisão de responder ou usar a frase de fallback fica restrita ao contexto fornecido ao modelo.

## Reiniciar completamente o banco

Se trocar o modelo de embeddings e ocorrer incompatibilidade de dimensão, remova o volume do PostgreSQL e recrie a infraestrutura:

```bash
docker compose down -v
docker compose up -d
python src/ingest.py
```

## Segurança

Nunca faça commit do `.env`. A chave da OpenAI deve ficar somente no ambiente local.

## Estrutura

```text
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── src/
│   ├── ingest.py
│   ├── search.py
│   └── chat.py
├── document.pdf
└── README.md
```
