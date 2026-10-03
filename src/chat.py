"""CLI de perguntas e respostas baseada exclusivamente no PDF ingerido."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from search import search

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-5.6-sol")
FALLBACK = "Não tenho informações necessárias para responder sua pergunta."

PROMPT_TEMPLATE = """CONTEXTO:
{context}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
"Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

PERGUNTA DO USUÁRIO:
{question}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""


def build_context(results):
    parts = []
    for pos, (doc, score) in enumerate(results, 1):
        page = doc.metadata.get("page")
        label = f"Página {page + 1}" if isinstance(page, int) else "Página desconhecida"
        parts.append(
            f"[RESULTADO {pos} | {label} | distância={score:.6f}]\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(parts)


def normalize_response_content(content) -> str:
    """Converte respostas textuais simples ou blocos de conteúdo em texto."""
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict):
                text = block.get("text")
                if isinstance(text, str):
                    texts.append(text)
            elif isinstance(block, str):
                texts.append(block)
        return "\n".join(texts).strip()

    return str(content).strip()


def answer_question(question: str) -> str:
    results = search(question, k=10)
    context = build_context(results)

    llm = ChatOpenAI(model=CHAT_MODEL, reasoning_effort="low")
    response = llm.invoke(
        PROMPT_TEMPLATE.format(context=context, question=question)
    )

    answer = normalize_response_content(response.content)
    return answer or FALLBACK


def main() -> None:
    print("Busca semântica no PDF")
    print("Digite 'sair' para encerrar.\n")

    while True:
        try:
            question = input("PERGUNTA: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAté mais!")
            break

        if question.lower() in {"sair", "exit", "quit"}:
            print("Até mais!")
            break

        if not question:
            continue

        try:
            print(f"RESPOSTA: {answer_question(question)}\n")
        except Exception as exc:
            print(f"ERRO: {exc}\n")


if __name__ == "__main__":
    main()
