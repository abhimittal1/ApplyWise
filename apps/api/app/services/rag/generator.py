import openai
from app.core.config import get_settings

settings = get_settings()

client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

SYSTEM_PROMPT = """You are CareerOS Knowledge Assistant. You help users understand their own skills, projects, and career history based on documents they have uploaded.

Answer only from the provided context. If the answer is not in the context, say "I don't have that information in your documents."

Format your answers using markdown for readability (bold, lists, headers, etc). Do not mention or cite source document names."""

MAX_CONTEXT_TOKENS = 3000
MAX_HISTORY_MESSAGES = 6


def build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a context string."""
    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(
            f"[{i+1}]\n{chunk['content']}\n---"
        )
    return "\n\n".join(context_parts)


async def generate_answer(
    query: str,
    chunks: list[dict],
    conversation_history: list[dict] | None = None,
) -> str:
    """Generate an answer using LLM with retrieved context."""
    if not client:
        raise RuntimeError("OpenAI API key not configured")

    context = build_context(chunks)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add context as system message
    messages.append({
        "role": "system",
        "content": f"Here is relevant information from the user's documents:\n\n{context}",
    })

    # Add conversation history (last N messages)
    if conversation_history:
        for msg in conversation_history[-MAX_HISTORY_MESSAGES:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

    # Add current query
    messages.append({"role": "user", "content": query})

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=3000,
        temperature=0.3,
    )

    return response.choices[0].message.content or "I wasn't able to generate a response."


async def generate_answer_stream(
    query: str,
    chunks: list[dict],
    conversation_history: list[dict] | None = None,
):
    """Generate a streaming answer using LLM with retrieved context."""
    if not client:
        raise RuntimeError("OpenAI API key not configured")

    context = build_context(chunks)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.append({
        "role": "system",
        "content": f"Here is relevant information from the user's documents:\n\n{context}",
    })

    if conversation_history:
        for msg in conversation_history[-MAX_HISTORY_MESSAGES:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": query})

    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=3000,
        temperature=0.3,
        stream=True,
    )

    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
