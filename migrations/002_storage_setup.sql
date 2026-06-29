/*
===============================================================================
Migration  : 002_storage_setup.sql
Project    : ClaimPilot
Author     : Fazil P Raphi
Version    : 1.0.0

Description
-------------------------------------------------------------------------------
Creates the Supabase Storage bucket used by ClaimPilot.

DO NOT MODIFY AFTER EXECUTION.
===============================================================================
*/

BEGIN;

-- ============================================================================
-- STORAGE BUCKET
-- ============================================================================

INSERT INTO storage.buckets (
    id,
    name,
    public,
    file_size_limit,
    allowed_mime_types
)
VALUES (
    'claim-files',
    'claim-files',
    FALSE,
    10485760,
    ARRAY[
        'application/pdf',
        'image/jpeg',
        'image/png',
        'image/webp'
    ]
);
COMMIT;

