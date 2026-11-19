import asyncio
import json
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ..schemas.chat import SendMessageRequest, RegenerateRequest
from ..services import chat_service
from ..services.ai_service import stream_ai_response, AIConfigurationError

router = APIRouter(prefix="/api", tags=["chat"])
logger = logging.getLogger(__name__)

def sse(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False, default=str)}\n\n"

@router.post("/chats")
async def create_chat():
    doc = await chat_service.create_conversation()
    return {"conversation_id": doc["conversation_id"], "created_at": doc["created_at"]}

@router.get("/chats")
async def get_chats():
    return await chat_service.list_conversations()

@router.get("/chats/{conversation_id}")
async def get_chat(conversation_id: str):
    doc = await chat_service.get_conversation(conversation_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return doc

@router.post("/chats/{conversation_id}/messages")
async def send_message(conversation_id: str, body: SendMessageRequest):
    prompt = body.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=422, detail="Prompt cannot be empty")
    if len(prompt) > 12000:
        raise HTTPException(status_code=422, detail="Prompt is too long")
    doc = await chat_service.get_conversation(conversation_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await chat_service.append_message(conversation_id, "user", prompt, body.tone)
    history = doc.get("messages", [])

    async def generate():
        accumulated = ""
        try:
            async for token in stream_ai_response(prompt, body.tone, history):
                accumulated += token
                # Emit one character per SSE event so the UI reveals text progressively.
                for character in token:
                    yield sse("token", {"content": character})
            if not accumulated:
                raise RuntimeError("The AI provider returned an empty response.")
            await chat_service.append_message(conversation_id, "assistant", accumulated, body.tone)
            yield sse("done", {"conversation_id": conversation_id})
        except AIConfigurationError as exc:
            logger.warning("AI configuration error: %s", exc)
            yield sse("error", {"message": str(exc)})
        except Exception:
            logger.exception("AI response generation failed")
            yield sse("error", {"message": "The AI response could not be generated. Check the backend logs and try again."})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )

@router.post("/chats/{conversation_id}/regenerate")
async def regenerate(conversation_id: str, body: RegenerateRequest):
    doc = await chat_service.get_conversation(conversation_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = doc.get("messages", [])
    if not messages or messages[-1]["role"] != "assistant":
        raise HTTPException(status_code=400, detail="There is no assistant response to regenerate.")
    if len(messages) < 2 or messages[-2]["role"] != "user":
        raise HTTPException(status_code=400, detail="Could not find the prompt for regeneration.")
    prompt = messages[-2]["content"]
    history = messages[:-2]

    async def generate():
        accumulated = ""
        try:
            async for token in stream_ai_response(prompt, body.tone, history):
                accumulated += token
                # Emit one character per SSE event so the UI reveals text progressively.
                for character in token:
                    yield sse("token", {"content": character})
            if not accumulated:
                raise RuntimeError("The AI provider returned an empty response.")
            await chat_service.replace_last_assistant(conversation_id, accumulated, body.tone)
            yield sse("done", {"conversation_id": conversation_id})
        except AIConfigurationError as exc:
            yield sse("error", {"message": str(exc)})
        except Exception:
            logger.exception("AI regeneration failed")
            yield sse("error", {"message": "Regeneration failed. Please try again."})

    return StreamingResponse(
        generate(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )
