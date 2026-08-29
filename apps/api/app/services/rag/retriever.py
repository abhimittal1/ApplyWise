import uuid
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocumentChunk
from app.services.ingestion.embeddings import generate_embedding


async def retrieve_chunks(
    query: str,
    user_id: uuid.UUID,
    db: AsyncSession,
    top_k: int = 8,
    min_similarity: float = 0.25,
) -> list[dict]:
    """
    Retrieve top-K relevant chunks for a user's query using pgvector cosine similarity.
    Enforces strict tenant scoping (user_id) and similarity thresholding.
    Returns list of {content, metadata, score, chunk_id}.
    """
    # Generate query embedding
    query_embedding = await generate_embedding(query)

    # pgvector cosine distance search with tenant isolation pre-filter
    result = await db.execute(
        text("""
            SELECT
                id, content, metadata, chunk_index,
                1 - (embedding <=> CAST(:embedding AS vector)) as similarity
            FROM document_chunks
            WHERE user_id = CAST(:user_id AS uuid)
                AND embedding IS NOT NULL
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :top_k
        """),
        {
            "embedding": str(query_embedding),
            "user_id": str(user_id),
            "top_k": top_k,
        },
    )

    rows = result.fetchall()
    chunks = []
    for row in rows:
        sim_score = float(row[4]) if row[4] else 0.0
        if sim_score >= min_similarity:
            chunks.append({
                "chunk_id": str(row[0]),
                "content": row[1],
                "metadata": row[2] or {},
                "chunk_index": row[3],
                "score": sim_score,
            })
    return chunks
