# Send retrieved context to the LLM and return an answer with sources


from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from rag.config import LLM_MODEL, TOP_K


def answer_question(question, vector_store):
    results = vector_store.similarity_search(
        question,
        k=TOP_K
    )

    if not results:
        return {
            "answer": "I could not find relevant information in your documents.",
            "sources": []
        }

    context_parts = []
    sources = []

    for doc in results:
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page")

        location = f"Source: {source}"

        if page is not None:
            location += f", Page: {page + 1}"

        context_parts.append(
            f"{location}\n{doc.page_content}"
        )

        sources.append({
            "source": source,
            "page": page,
            "content": doc.page_content
        })

    context = "\n\n".join(context_parts)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Answer the question using only the supplied context. "
            "If the answer is not in the context, say you do not know "
            "based on these documents. Do not invent facts."
        ),
        (
            "human",
            "Context:\n{context}\n\nQuestion: {question}"
        )
    ])

    model = ChatOllama(
        model=LLM_MODEL,
        temperature=0
    )

    chain = prompt | model

    response = chain.invoke({
        "context": context,
        "question": question
    })

    return {
        "answer": response.content,
        "sources": sources
    }
