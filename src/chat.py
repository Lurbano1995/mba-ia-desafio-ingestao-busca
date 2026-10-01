"""CLI de perguntas e respostas baseada exclusivamente no PDF ingerido."""
from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from search import search
ROOT_DIR=Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")
CHAT_MODEL=os.getenv("OPENAI_CHAT_MODEL","gpt-5.6-sol")
FALLBACK="Não tenho informações necessárias para responder sua pergunta."
PROMPT_TEMPLATE="""CONTEXTO:\n{context}\n\nREGRAS:\n- Responda somente com base no CONTEXTO.\n- Se a informação não estiver explicitamente no CONTEXTO, responda:\n"Não tenho informações necessárias para responder sua pergunta."\n- Nunca invente ou use conhecimento externo.\n- Nunca produza opiniões ou interpretações além do que está escrito.\n\nPERGUNTA DO USUÁRIO:\n{question}\n\nRESPONDA A "PERGUNTA DO USUÁRIO""""
def build_context(results):
    parts=[]
    for pos,(doc,score) in enumerate(results,1):
        page=doc.metadata.get("page"); label=f"Página {page+1}" if isinstance(page,int) else "Página desconhecida"
        parts.append(f"[RESULTADO {pos} | {label} | distância={score:.6f}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)
def answer_question(question:str)->str:
    results=search(question,k=10)
    context=build_context(results)
    llm=ChatOpenAI(model=CHAT_MODEL,reasoning_effort="low")
    response=llm.invoke(PROMPT_TEMPLATE.format(context=context,question=question))
    answer=response.content if isinstance(response.content,str) else str(response.content)
    return answer.strip() or FALLBACK
def main()->None:
    print("Busca semântica no PDF"); print("Digite 'sair' para encerrar.\n")
    while True:
        try: question=input("PERGUNTA: ").strip()
        except (EOFError,KeyboardInterrupt): print("\nAté mais!"); break
        if question.lower() in {"sair","exit","quit"}: print("Até mais!"); break
        if not question: continue
        try: print(f"RESPOSTA: {answer_question(question)}\n")
        except Exception as exc: print(f"ERRO: {exc}\n")
if __name__=="__main__": main()
