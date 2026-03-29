import json
import uuid
import logging

import openai
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.chat import Conversation, ChatMessage
from app.schemas.knowledge import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    ChatMessageResponse,
    SourceChunk,
)
from app.services.rag.retriever import retrieve_chunks
from app.services.rag.generator import generate_answer, generate_answer_stream

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse)
async def knowledge_chat(
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Get or create conversation
    if body.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == body.conversation_id,
                Conversation.user_id == current_user.id,
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=current_user.id,
            title=body.message[:100],
        )
        db.add(conversation)
        await db.flush()

    # Get conversation history
    history_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation.id)
        .order_by(ChatMessage.created_at.asc())
    )
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in history_result.scalars().all()
    ]

    # Retrieve relevant chunks and generate answer
    try:
        chunks = await retrieve_chunks(body.message, current_user.id, db, top_k=8)
        answer = await generate_answer(body.message, chunks, history)
    except RuntimeError as e:
        logger.error(f"Chat service error: {e}")
        raise HTTPException(status_code=503, detail="AI service not configured. Please set your OpenAI API key.")
    except openai.AuthenticationError:
        logger.error("OpenAI authentication failed")
        raise HTTPException(status_code=503, detail="AI service authentication failed. Check your API key.")
    except openai.RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again shortly.")
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=502, detail="AI service temporarily unavailable. Please try again.")
    except Exception as e:
        logger.exception(f"Unexpected chat error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your question.")

    # Build sources
    sources = [
        SourceChunk(
            chunk_id=c["chunk_id"],
            content=c["content"][:200],
            filename=c.get("metadata", {}).get("filename"),
            score=c["score"],
        )
        for c in chunks[:4]
    ]

    # Save messages
    user_msg = ChatMessage(
        id=uuid.uuid4(),
        conversation_id=conversation.id,
        role="user",
        content=body.message,
    )
    assistant_msg = ChatMessage(
        id=uuid.uuid4(),
        conversation_id=conversation.id,
        role="assistant",
        content=answer,
        sources={"chunks": [s.model_dump() for s in sources]},
    )
    db.add(user_msg)
    db.add(assistant_msg)

    return ChatResponse(
        answer=answer,
        sources=sources,
        conversation_id=conversation.id,
    )


@router.post("/chat/stream")
async def knowledge_chat_stream(
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stream chat response via Server-Sent Events."""
    # Get or create conversation
    if body.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == body.conversation_id,
                Conversation.user_id == current_user.id,
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=current_user.id,
            title=body.message[:100],
        )
        db.add(conversation)
        await db.flush()

    # Get history
    history_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation.id)
        .order_by(ChatMessage.created_at.asc())
    )
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in history_result.scalars().all()
    ]

    # Retrieve chunks
    try:
        chunks = await retrieve_chunks(body.message, current_user.id, db, top_k=8)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail="AI service not configured.")
    except openai.AuthenticationError:
        raise HTTPException(status_code=503, detail="AI service authentication failed.")
    except openai.RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    except openai.APIError:
        raise HTTPException(status_code=502, detail="AI service temporarily unavailable.")
    except Exception as e:
        logger.exception(f"Stream retrieval error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

    sources = [
        {
            "chunk_id": c["chunk_id"],
            "content": c["content"][:200],
            "filename": c.get("metadata", {}).get("filename"),
            "score": c["score"],
        }
        for c in chunks[:4]
    ]

    # Save user message
    user_msg = ChatMessage(
        id=uuid.uuid4(),
        conversation_id=conversation.id,
        role="user",
        content=body.message,
    )
    db.add(user_msg)
    await db.flush()

    async def event_stream():
        full_answer = ""
        # Send sources first
        yield f"data: {json.dumps({'type': 'sources', 'sources': sources, 'conversation_id': str(conversation.id)})}\n\n"

        try:
            async for token in generate_answer_stream(body.message, chunks, history):
                full_answer += token
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
        except Exception as e:
            logger.error(f"Stream generation error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': 'AI service error during response generation.'})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

        # Save assistant message after streaming
        assistant_msg = ChatMessage(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            role="assistant",
            content=full_answer,
            sources={"chunks": sources},
        )
        db.add(assistant_msg)
        await db.flush()

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.created_at.desc())
    )
    return result.scalars().all()


@router.get("/conversations/{conversation_id}/messages", response_model=list[ChatMessageResponse])
async def get_conversation_messages(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify ownership
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.asc())
    )
    return msg_result.scalars().all()


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await db.delete(conversation)
