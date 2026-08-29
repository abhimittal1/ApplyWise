-- ==============================================================================
-- ApplyWise / CareerOS Database Security Hardening Script for Supabase / PostgreSQL
-- ==============================================================================
--
-- This script hardens the database against:
-- 1. Row-Level Security (RLS) gaps & public data exposure
-- 2. Search path manipulation & unpinned function execution
-- 3. Cross-tenant privilege escalation & foreign key tampering
-- 4. Sensitive credential exposure (hashed_password, refresh_tokens) via PostgREST
--
-- Execution: Paste and run directly in Supabase SQL Editor or run via psql.
-- ==============================================================================

BEGIN;

-- ==============================================================================
-- 1. AUTH COMPATIBILITY & SEARCH PATH PINNING
-- ==============================================================================

CREATE SCHEMA IF NOT EXISTS auth;

-- Fallback auth.uid() definition for environments without native Supabase Auth
CREATE OR REPLACE FUNCTION auth.uid()
RETURNS uuid
LANGUAGE sql
STABLE
SET search_path = public, pg_temp
AS $$
    SELECT NULLIF(
        COALESCE(
            current_setting('request.jwt.claim.sub', true),
            (current_setting('request.jwt.claims', true)::jsonb ->> 'sub')
        ),
        ''
    )::uuid;
$$;

-- Secure session helper with explicit fixed search path
CREATE OR REPLACE FUNCTION public.set_request_user_id(uid uuid)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    PERFORM set_config('request.jwt.claim.sub', uid::text, true);
END;
$$;


-- ==============================================================================
-- 2. TENANT INTEGRITY: COMPOSITE CONSTRAINTS & FOREIGN KEYS
-- ==============================================================================

-- Parent table composite unique constraints
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

-- Child table composite foreign keys to guarantee tenant matching
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


-- ==============================================================================
-- 3. ENABLE & FORCE ROW-LEVEL SECURITY (RLS) ACROSS ALL 13 TABLES
-- ==============================================================================

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE users FORCE ROW LEVEL SECURITY;

ALTER TABLE refresh_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE refresh_tokens FORCE ROW LEVEL SECURITY;

ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents FORCE ROW LEVEL SECURITY;

ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks FORCE ROW LEVEL SECURITY;

ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills FORCE ROW LEVEL SECURITY;

ALTER TABLE document_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_skills FORCE ROW LEVEL SECURITY;

ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs FORCE ROW LEVEL SECURITY;

ALTER TABLE job_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_skills FORCE ROW LEVEL SECURITY;

ALTER TABLE job_matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_matches FORCE ROW LEVEL SECURITY;

ALTER TABLE applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE applications FORCE ROW LEVEL SECURITY;

ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations FORCE ROW LEVEL SECURITY;

ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages FORCE ROW LEVEL SECURITY;

ALTER TABLE generated_outputs ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_outputs FORCE ROW LEVEL SECURITY;


-- ==============================================================================
-- 4. RLS POLICIES FOR DIRECT TENANT TABLES
-- ==============================================================================

-- Users: Each tenant can only access and modify their own record
DROP POLICY IF EXISTS users_tenant_policy ON users;
CREATE POLICY users_tenant_policy ON users
    FOR ALL
    USING (id = auth.uid())
    WITH CHECK (id = auth.uid());

-- Documents: Tenant scoped by user_id
DROP POLICY IF EXISTS documents_tenant_policy ON documents;
CREATE POLICY documents_tenant_policy ON documents
    FOR ALL
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Document Chunks: Tenant scoped by user_id
DROP POLICY IF EXISTS document_chunks_tenant_policy ON document_chunks;
CREATE POLICY document_chunks_tenant_policy ON document_chunks
    FOR ALL
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Jobs: Tenant scoped by user_id
DROP POLICY IF EXISTS jobs_tenant_policy ON jobs;
CREATE POLICY jobs_tenant_policy ON jobs
    FOR ALL
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Job Matches: Tenant scoped by user_id
DROP POLICY IF EXISTS job_matches_tenant_policy ON job_matches;
CREATE POLICY job_matches_tenant_policy ON job_matches
    FOR ALL
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Applications: Tenant scoped by user_id
DROP POLICY IF EXISTS applications_tenant_policy ON applications;
CREATE POLICY applications_tenant_policy ON applications
    FOR ALL
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Conversations: Tenant scoped by user_id
DROP POLICY IF EXISTS conversations_tenant_policy ON conversations;
CREATE POLICY conversations_tenant_policy ON conversations
    FOR ALL
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Generated Outputs: Tenant scoped by user_id
DROP POLICY IF EXISTS generated_outputs_tenant_policy ON generated_outputs;
CREATE POLICY generated_outputs_tenant_policy ON generated_outputs
    FOR ALL
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Refresh Tokens: Restricted to token owner
DROP POLICY IF EXISTS refresh_tokens_tenant_policy ON refresh_tokens;
CREATE POLICY refresh_tokens_tenant_policy ON refresh_tokens
    FOR ALL
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());


-- ==============================================================================
-- 5. RLS POLICIES FOR INDIRECT & JUNCTION TABLES
-- ==============================================================================

-- Chat Messages: Indirect tenant scoping via parent conversation
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

-- Document Skills: Indirect tenant scoping via parent document
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

-- Job Skills: Indirect tenant scoping via parent job
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


-- ==============================================================================
-- 6. SHARED REFERENCE CATALOG TABLES
-- ==============================================================================

-- Skills: Read-only for authenticated & anon clients; writes restricted to service_role
DROP POLICY IF EXISTS skills_read_policy ON skills;
CREATE POLICY skills_read_policy ON skills
    FOR SELECT
    USING (true);


-- ==============================================================================
-- 7. POSTGREST ROLE PERMISSIONS & SENSITIVE FIELD SHIELDING
-- ==============================================================================

DO $$
BEGIN
    -- Block direct PostgREST REST API access to refresh_tokens
    IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'anon') THEN
        REVOKE ALL ON refresh_tokens FROM anon;
    END IF;
    IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'authenticated') THEN
        REVOKE ALL ON refresh_tokens FROM authenticated;
    END IF;

    -- Protect users.hashed_password from exposure in PostgREST endpoints
    IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'anon') THEN
        REVOKE ALL ON users FROM anon;
        GRANT SELECT (id, email, name, avatar_url, created_at, updated_at) ON users TO anon;
    END IF;
    IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'authenticated') THEN
        REVOKE ALL ON users FROM authenticated;
        GRANT SELECT (id, email, name, avatar_url, oauth_provider, oauth_provider_id, created_at, updated_at) ON users TO authenticated;
        GRANT UPDATE (name, avatar_url) ON users TO authenticated;
    END IF;
END $$;

COMMIT;
