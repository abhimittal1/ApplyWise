"""add pgvector HNSW indexes and tenant composite indexes

Revision ID: 003
Revises: 002
"""
from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create HNSW index for high-performance approximate nearest neighbor search using cosine distance
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_hnsw "
        "ON document_chunks USING hnsw (embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64);"
    )

    # 2. Create HNSW index for jobs vector search
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_jobs_embedding_hnsw "
        "ON jobs USING hnsw (embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64);"
    )

    # 3. Composite tenant index on document_chunks to accelerate tenant-scoped vector scans
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_document_chunks_user_doc "
        "ON document_chunks (user_id, document_id);"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_user_doc;")
    op.execute("DROP INDEX IF EXISTS ix_jobs_embedding_hnsw;")
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding_hnsw;")
