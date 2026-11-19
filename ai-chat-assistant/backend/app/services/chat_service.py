from datetime import datetime, timezone
from uuid import UUID
from ..database import get_database


def now():
    return datetime.now(timezone.utc).isoformat()


def _conversation_with_messages(conversation: dict) -> dict:
    db = get_database()
    result = (
        db.table("messages")
        .select("id,conversation_id,role,content,created_at")
        .eq("conversation_id", conversation["id"])
        .order("created_at")
        .execute()
    )
    messages = []
    for item in result.data:
        messages.append({
            "message_id": item["id"],
            "role": item["role"],
            "content": item["content"],
            "timestamp": item["created_at"],
        })
    return {
        "conversation_id": conversation["id"],
        "title": conversation.get("title") or "New conversation",
        "created_at": conversation["created_at"],
        "updated_at": conversation["updated_at"],
        "tone": conversation.get("tone", "professional"),
        "messages": messages,
    }


async def create_conversation():
    timestamp = now()
    result = get_database().table("conversations").insert({
        "title": "New conversation",
        "tone": "professional",
        "created_at": timestamp,
        "updated_at": timestamp,
    }).execute()
    if not result.data:
        raise RuntimeError("Supabase did not return the created conversation")
    row = result.data[0]
    return {
        "conversation_id": row["id"],
        "title": row["title"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "messages": [],
    }


async def get_conversation(conversation_id: str):
    try:
        UUID(conversation_id)
    except ValueError:
        return None
    result = get_database().table("conversations").select("*").eq("id", conversation_id).limit(1).execute()
    if not result.data:
        return None
    return _conversation_with_messages(result.data[0])


async def list_conversations():
    result = (
        get_database().table("conversations")
        .select("id,title,created_at,updated_at")
        .order("updated_at", desc=True)
        .limit(100)
        .execute()
    )
    return [{
        "conversation_id": row["id"],
        "title": row.get("title") or "New conversation",
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    } for row in result.data]


async def append_message(conversation_id: str, role: str, content: str, tone=None):
    db = get_database()
    timestamp = now()
    payload = {
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "created_at": timestamp,
    }
    inserted = db.table("messages").insert(payload).execute()
    if not inserted.data:
        raise RuntimeError("Supabase did not save the message")

    update = {"updated_at": timestamp}
    if tone:
        update["tone"] = tone
    if role == "user":
        update["title"] = content[:60] + ("…" if len(content) > 60 else "")
    db.table("conversations").update(update).eq("id", conversation_id).execute()
    row = inserted.data[0]
    return {"message_id": row["id"], "role": role, "content": content, "timestamp": row["created_at"], "tone": tone}


async def replace_last_assistant(conversation_id: str, content: str, tone: str):
    db = get_database()
    last = (
        db.table("messages").select("id,role")
        .eq("conversation_id", conversation_id)
        .order("created_at", desc=True).limit(1).execute()
    )
    if last.data and last.data[0]["role"] == "assistant":
        db.table("messages").delete().eq("id", last.data[0]["id"]).execute()
    return await append_message(conversation_id, "assistant", content, tone)
