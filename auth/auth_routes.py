from fastapi import APIRouter,  Depends
from utils.commons import to_json_response
from .auth_models import SignInRequest, SignUpRequest, AuthenticatedUser, AssignRolesRequest,AssignPermissionsRequest
from .auth_service import auth_service
from auth.auth_middleware import auth_middleware
from utils.logger import logger


# Create authentication router
auth_router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

@auth_router.post("/signup")
async def signup(signup_request: SignUpRequest):
    """Register a new user"""
    result = await auth_service.sign_up(signup_request)
    logger.info(f"User registration successful for: {signup_request.email}")
    return to_json_response(result)

@auth_router.post("/signin")
async def signin(signin_request: SignInRequest):
    """Authenticate user and return JWT token"""
    result = await auth_service.sign_in(signin_request)
    logger.info(f"User authentication successful for: {signin_request.email}")
    return to_json_response(result)

@auth_router.post("/signout")
async def signout(current_user: AuthenticatedUser = Depends(auth_middleware.get_current_user)):
    """Sign out the current user"""
    result = await auth_service.sign_out(current_user.token)
    logger.info(f"User logout successful for: {current_user.email}")
    return to_json_response(result)


@auth_router.get("/permissions")
async def get_permissions(current_user: AuthenticatedUser = Depends(auth_middleware.get_current_user)):
    """Get current user's permissions and roles"""
    result = await auth_service.get_user_permissions(current_user.token)
    logger.debug(f"Permissions retrieved for: {current_user.email}")
    return to_json_response(result)

@auth_router.post("/assign-roles")
async def assign_roles(
    assign_roles_request: AssignRolesRequest,
    current_user: AuthenticatedUser = Depends(auth_middleware.require_roles(["admin"]))
):
    """Assign roles to a user (admin only)"""
    result = await auth_service.assign_roles(assign_roles_request.email, assign_roles_request.roles,current_user.firstName)
    logger.info(f"Roles assigned by admin {current_user.firstName} to user: {assign_roles_request.email}")
    return to_json_response(result)

@auth_router.post("/assign-permissions")
async def assign_permissions(
    assign_permissions_request: AssignPermissionsRequest,
    current_user: AuthenticatedUser = Depends(auth_middleware.require_admin())
):
    """Assign permissions to a user (admin only)"""
    result = await auth_service.assign_permissions(assign_permissions_request.email, assign_permissions_request.permissions,current_user.firstName)
    logger.info(f"Permissions assigned by admin {current_user.firstName} to user: {assign_permissions_request.email}")
    return to_json_response(result)
