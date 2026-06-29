from fastapi import APIRouter, Depends
from supabase import Client

from app.database.dependencies import get_admin_client, get_user_client
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/claims", tags=["Claims"])

# ========================================
# CLAIMS ROUTES PATTERN DOCUMENTATION
# ========================================
#
# The ClaimPilot backend uses two distinct database clients:
#
# 1. get_admin_client() -> Client
#    - Uses SERVICE_ROLE_KEY
#    - Bypasses Row Level Security
#    - For: AI agents, audit logging, background jobs, OCR, PDF generation
#    - No authentication required
#
# 2. get_user_client() -> Client
#    - Uses ANON_KEY + authenticated user's JWT
#    - Respects Row Level Security policies
#    - For: User's own claims, documents, profile data
#    - Requires authentication via @Depends(get_current_user)
#
# ========================================
# EXAMPLE: Create a claim (user operation)
# ========================================
#
# @router.post("/claims")
# async def create_claim(
#     request: CreateClaimRequest,
#     current_user = Depends(get_current_user),          # Get authenticated user
#     db_client: Client = Depends(get_user_client),      # Use user-scoped client
# ):
#     claim_service = ClaimService(db_client)
#     claim = claim_service.create_claim(
#         user_id=current_user.id,
#         claim_data=request.dict(),
#     )
#     return success_response(data=claim)
#
# ========================================
# EXAMPLE: Process claims with AI (admin)
# ========================================
#
# @router.post("/admin/claims/{claim_id}/process")
# async def process_claim_with_ai(
#     claim_id: str,
#     db_client: Client = Depends(get_admin_client),     # Use admin client
# ):
#     # AI agent can access all claims, not just user's own
#     ai_service = AICoordinatorService(db_client)
#     result = await ai_service.process_claim(claim_id)
#     return success_response(data=result)
#
# ========================================
# KEY RULES
# ========================================
#
# 1. User operations -> Depends(get_current_user), Depends(get_user_client)
# 2. Admin/AI operations -> Depends(get_admin_client)
# 3. Services receive db_client and never import globals
# 4. Services don't care which client type - they just use it
# 5. RLS policies at database level enforce access control
#
# ========================================

