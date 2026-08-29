"""database security hardening: RLS policies, search path pinning, and tenant composite constraints

Revision ID: 004
Revises: 003
Create Date: 2026-08-29
"""
from typing import Sequence, Union

from alembic import op


revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES_WITH_RLS = [
    "users",
    "refresh_tokens",
    "documents",
    "document_chunks",
    "skills",
    "document_skills",
    "jobs",
    "job_skills",
    "job_matches",
    "applications",
    "conversations",
    "chat_messages",
    "generated_outputs",
]


def upgrade() -> None:
    # 1. Ensure auth schema and auth.uid() function exist (compatible with Supabase & standalone PostgreSQL)
    op.execute(
        """
        DO $$
        BEGIN
            BEGIN
                CREATE SCHEMA IF NOT EXISTS auth;
            EXCEPTION
                WHEN insufficient_privilege OR duplicate_schema THEN
                    NULL;
            END;

            BEGIN
                CREATE OR REPLACE FUNCTION auth.uid()
                RETURNS uuid
                LANGUAGE sql
                STABLE
                SET search_path = public, pg_temp
                AS $func$
                    SELECT NULLIF(
                        COALESCE(
                            current_setting('request.jwt.claim.sub', true),
                            (current_setting('request.jwt.claims', true)::jsonb ->> 'sub')
                        ),
                        ''
                    )::uuid;
                $func$;
            EXCEPTION
                WHEN insufficient_privilege THEN
                    NULL;
            END;
        END $$;
        """
    )

    # 2. Add Unique Constraints for Composite Keys to enforce parent multi-tenant bounds
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'uq_documents_id_user_id'
            ) THEN
                ALTER TABLE documents ADD CONSTRAINT uq_documents_id_user_id UNIQUE (id, user_id);
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'uq_jobs_id_user_id'
            ) THEN
                ALTER TABLE jobs ADD CONSTRAINT uq_jobs_id_user_id UNIQUE (id, user_id);
            END IF;
        END $$;
        """
    )

    # 3. Add Composite Foreign Keys to prevent cross-tenant privilege escalation
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_document_chunks_document_user'
            ) THEN
                ALTER TABLE document_chunks
                ADD CONSTRAINT fk_document_chunks_document_user
                FOREIGN KEY (document_id, user_id)
                REFERENCES documents (id, user_id)
                ON DELETE CASCADE;
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_job_matches_job_user'
            ) THEN
                ALTER TABLE job_matches
                ADD CONSTRAINT fk_job_matches_job_user
                FOREIGN KEY (job_id, user_id)
                REFERENCES jobs (id, user_id)
                ON DELETE CASCADE;
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_applications_job_user'
            ) THEN
                ALTER TABLE applications
                ADD CONSTRAINT fk_applications_job_user
                FOREIGN KEY (job_id, user_id)
                REFERENCES jobs (id, user_id)
                ON DELETE CASCADE;
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_generated_outputs_job_user'
            ) THEN
                ALTER TABLE generated_outputs
                ADD CONSTRAINT fk_generated_outputs_job_user
                FOREIGN KEY (job_id, user_id)
                REFERENCES jobs (id, user_id)
                ON DELETE CASCADE;
            END IF;
        END $$;
        """
    )

    # 4. Enable and Force Row Level Security (RLS) on all 13 tables
    for table in TABLES_WITH_RLS:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;")

    # 5. Create RLS Policies
    op.execute(
        """
        -- Direct Tenant Tables (users, documents, document_chunks, jobs, job_matches, applications, conversations, generated_outputs)
        DROP POLICY IF EXISTS users_tenant_policy ON users;
        CREATE POLICY users_tenant_policy ON users
            FOR ALL
            USING (id = auth.uid())
            WITH CHECK (id = auth.uid());

        DROP POLICY IF EXISTS documents_tenant_policy ON documents;
        CREATE POLICY documents_tenant_policy ON documents
            FOR ALL
            USING (user_id = auth.uid())
            WITH CHECK (user_id = auth.uid());

        DROP POLICY IF EXISTS document_chunks_tenant_policy ON document_chunks;
        CREATE POLICY document_chunks_tenant_policy ON document_chunks
            FOR ALL
            USING (user_id = auth.uid())
            WITH CHECK (user_id = auth.uid());

        DROP POLICY IF EXISTS jobs_tenant_policy ON jobs;
        CREATE POLICY jobs_tenant_policy ON jobs
            FOR ALL
            USING (user_id = auth.uid())
            WITH CHECK (user_id = auth.uid());

        DROP POLICY IF EXISTS job_matches_tenant_policy ON job_matches;
        CREATE POLICY job_matches_tenant_policy ON job_matches
            FOR ALL
            USING (user_id = auth.uid())
            WITH CHECK (user_id = auth.uid());

        DROP POLICY IF EXISTS applications_tenant_policy ON applications;
        CREATE POLICY applications_tenant_policy ON applications
            FOR ALL
            USING (user_id = auth.uid())
            WITH CHECK (user_id = auth.uid());

        DROP POLICY IF EXISTS conversations_tenant_policy ON conversations;
        CREATE POLICY conversations_tenant_policy ON conversations
            FOR ALL
            USING (user_id = auth.uid())
            WITH CHECK (user_id = auth.uid());

        DROP POLICY IF EXISTS generated_outputs_tenant_policy ON generated_outputs;
        CREATE POLICY generated_outputs_tenant_policy ON generated_outputs
            FOR ALL
            USING (user_id = auth.uid())
            WITH CHECK (user_id = auth.uid());

        -- Indirect & Junction Tables
        DROP POLICY IF EXISTS chat_messages_tenant_policy ON chat_messages;
        CREATE POLICY chat_messages_tenant_policy ON chat_messages
            FOR ALL
            USING (
                EXISTS (
                    SELECT 1 FROM conversations
                    WHERE conversations.id = chat_messages.conversation_id
                    AND conversations.user_id = auth.uid()
                )
            )
            WITH CHECK (
                EXISTS (
                    SELECT 1 FROM conversations
                    WHERE conversations.id = chat_messages.conversation_id
                    AND conversations.user_id = auth.uid()
                )
            );

        DROP POLICY IF EXISTS document_skills_tenant_policy ON document_skills;
        CREATE POLICY document_skills_tenant_policy ON document_skills
            FOR ALL
            USING (
                EXISTS (
                    SELECT 1 FROM documents
                    WHERE documents.id = document_skills.document_id
                    AND documents.user_id = auth.uid()
                )
            )
            WITH CHECK (
                EXISTS (
                    SELECT 1 FROM documents
                    WHERE documents.id = document_skills.document_id
                    AND documents.user_id = auth.uid()
                )
            );

        DROP POLICY IF EXISTS job_skills_tenant_policy ON job_skills;
        CREATE POLICY job_skills_tenant_policy ON job_skills
            FOR ALL
            USING (
                EXISTS (
                    SELECT 1 FROM jobs
                    WHERE jobs.id = job_skills.job_id
                    AND jobs.user_id = auth.uid()
                )
            )
            WITH CHECK (
                EXISTS (
                    SELECT 1 FROM jobs
                    WHERE jobs.id = job_skills.job_id
                    AND jobs.user_id = auth.uid()
                )
            );

        -- Shared Reference Catalog Table (skills)
        DROP POLICY IF EXISTS skills_read_policy ON skills;
        CREATE POLICY skills_read_policy ON skills
            FOR SELECT
            USING (true);

        -- Refresh Tokens (Restricted exclusively to token owner)
        DROP POLICY IF EXISTS refresh_tokens_tenant_policy ON refresh_tokens;
        CREATE POLICY refresh_tokens_tenant_policy ON refresh_tokens
            FOR ALL
            USING (user_id = auth.uid())
            WITH CHECK (user_id = auth.uid());
        """
    )

    # 6. Secure Session Context Helper Function with Fixed Search Path
    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_request_user_id(uid uuid)
        RETURNS void
        LANGUAGE plpgsql
        SECURITY DEFINER
        SET search_path = public, pg_temp
        AS $$
        BEGIN
            PERFORM set_config('request.jwt.claim.sub', uid::text, true);
        END;
        $$;
        """
    )

    # 7. PostgREST Permissions & Sensitive Field Shielding (for Supabase roles)
    op.execute(
        """
        DO $$
        BEGIN
            BEGIN
                -- Revoke all access on refresh_tokens from PostgREST public roles
                IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON refresh_tokens FROM anon;
                END IF;
                IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON refresh_tokens FROM authenticated;
                END IF;

                -- Shield sensitive columns (hashed_password) from public exposure
                IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON users FROM anon;
                    GRANT SELECT (id, email, name, avatar_url, created_at, updated_at) ON users TO anon;
                END IF;
                IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON users FROM authenticated;
                    GRANT SELECT (id, email, name, avatar_url, oauth_provider, oauth_provider_id, created_at, updated_at) ON users TO authenticated;
                    GRANT UPDATE (name, avatar_url) ON users TO authenticated;
                END IF;
            EXCEPTION
                WHEN insufficient_privilege THEN
                    NULL;
            END;
        END $$;
        """
    )


def downgrade() -> None:
    # 1. Drop Security Definer Helper Function
    op.execute("DROP FUNCTION IF EXISTS set_request_user_id(uuid);")

    # 2. Drop all RLS Policies
    op.execute(
        """
        DROP POLICY IF EXISTS users_tenant_policy ON users;
        DROP POLICY IF EXISTS documents_tenant_policy ON documents;
        DROP POLICY IF EXISTS document_chunks_tenant_policy ON document_chunks;
        DROP POLICY IF EXISTS jobs_tenant_policy ON jobs;
        DROP POLICY IF EXISTS job_matches_tenant_policy ON job_matches;
        DROP POLICY IF EXISTS applications_tenant_policy ON applications;
        DROP POLICY IF EXISTS conversations_tenant_policy ON conversations;
        DROP POLICY IF EXISTS generated_outputs_tenant_policy ON generated_outputs;
        DROP POLICY IF EXISTS chat_messages_tenant_policy ON chat_messages;
        DROP POLICY IF EXISTS document_skills_tenant_policy ON document_skills;
        DROP POLICY IF EXISTS job_skills_tenant_policy ON job_skills;
        DROP POLICY IF EXISTS skills_read_policy ON skills;
        DROP POLICY IF EXISTS refresh_tokens_tenant_policy ON refresh_tokens;
        """
    )

    # 3. Disable RLS on all 13 tables
    for table in TABLES_WITH_RLS:
        op.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY;")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")

    # 4. Drop Composite Foreign Keys
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_generated_outputs_job_user'
            ) THEN
                ALTER TABLE generated_outputs DROP CONSTRAINT fk_generated_outputs_job_user;
            END IF;

            IF EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_applications_job_user'
            ) THEN
                ALTER TABLE applications DROP CONSTRAINT fk_applications_job_user;
            END IF;

            IF EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_job_matches_job_user'
            ) THEN
                ALTER TABLE job_matches DROP CONSTRAINT fk_job_matches_job_user;
            END IF;

            IF EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_document_chunks_document_user'
            ) THEN
                ALTER TABLE document_chunks DROP CONSTRAINT fk_document_chunks_document_user;
            END IF;
        END $$;
        """
    )

    # 5. Drop Unique Constraints
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'uq_jobs_id_user_id'
            ) THEN
                ALTER TABLE jobs DROP CONSTRAINT uq_jobs_id_user_id;
            END IF;

            IF EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'uq_documents_id_user_id'
            ) THEN
                ALTER TABLE documents DROP CONSTRAINT uq_documents_id_user_id;
            END IF;
        END $$;
        """
    )
