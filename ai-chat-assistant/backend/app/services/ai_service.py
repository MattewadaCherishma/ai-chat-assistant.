from typing import AsyncIterator
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from ..config import settings

TONE_INSTRUCTIONS = {
    "professional": "Use a professional, clear, respectful tone. Be well-structured and precise.",
    "casual": "Use a friendly, natural, conversational tone. Keep the language approachable.",
    "concise": "Be concise and direct. Prioritize the answer and avoid unnecessary detail."
}

class AIConfigurationError(Exception):
    pass

async def stream_ai_response(prompt: str, tone: str, history: list[dict]) -> AsyncIterator[str]:
    system = (
        "You are a helpful AI chat assistant. Answer accurately, acknowledge uncertainty, "
        "and do not invent facts. " + TONE_INSTRUCTIONS[tone]
    )
    provider = settings.llm_provider.lower()

    if provider == "openai":
        if not settings.openai_api_key:
            raise AIConfigurationError("OPENAI_API_KEY is not configured. Add it to backend/.env.")
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        messages = [{"role": "system", "content": system}]
        messages.extend({"role": m["role"], "content": m["content"]} for m in history[-20:])
        messages.append({"role": "user", "content": prompt})
        stream = await client.chat.completions.create(
            model=settings.openai_model, messages=messages, stream=True, temperature=0.7
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    elif provider == "anthropic":
        if not settings.anthropic_api_key:
            raise AIConfigurationError("ANTHROPIC_API_KEY is not configured. Add it to backend/.env.")
        client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        history_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in history[-20:] if m["role"] in ("user", "assistant")
        ]
        history_messages.append({"role": "user", "content": prompt})
        async with client.messages.stream(
            model=settings.anthropic_model,
            max_tokens=2048,
            system=system,
            messages=history_messages,
            temperature=0.7,
        ) as stream:
            async for text in stream.text_stream:
                yield text
    else:
        raise AIConfigurationError("LLM_PROVIDER must be either 'openai' or 'anthropic'.")
