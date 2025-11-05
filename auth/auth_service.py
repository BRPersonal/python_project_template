from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from utils.logger import logger
from .auth_models import (
    SignInRequest, SignUpRequest, AuthenticatedUser, AppUser,
    AccessPermissions
)
from models.api_responses import SuccessResponse
from models.status_code import sc
from .auth_repository import create_user, get_users_count,get_app_user, verify_password, is_user_exists, assign_roles, assign_permissions
from .jwt_util import JwtUtil


class AuthenticationService:
    """Service for handling authentication with PostgreSQL database"""
    
    def __init__(self):
        self.jwt_util = JwtUtil()
        logger.info("Initialized AuthenticationService with PostgreSQL database")
    
    async def sign_up(self, signup_request: SignUpRequest) -> SuccessResponse[Dict[str, Any]]:
        """Register a new user in PostgreSQL database"""
        # Check if user already exists
        if await is_user_exists(signup_request.email):
            logger.warning(f"User registration failed - user already exists: {signup_request.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email '{signup_request.email}' already exists"
            )

        # Create AppUser object for database
        app_user = AppUser(
            firstName=signup_request.firstName,
            lastName=signup_request.lastName,
            email=signup_request.email,
            password=signup_request.password,
            roles=["user"],  # Default role
            permissions=[]  # Default empty permissions
        )

        #If this is the first signup make the user as admin
        user_count = await get_users_count()
        if user_count == 0:
            app_user.roles = ["admin"]

        # Save user to database
        await create_user(app_user)

        logger.info(f"User registration successful for email: {signup_request.email}")
        return SuccessResponse(
            data={"message": "User registered successfully", "status": "success"},
            status_code=sc.ENTITY_CREATION_SUCCESSFUL
        )

    async def sign_in(self, signin_request: SignInRequest) -> SuccessResponse[AuthenticatedUser]:
        """Authenticate user via PostgreSQL database"""
        # First, get user details from database
        app_user = await get_app_user(signin_request.email)

        # Verify user password using the retrieved password hash
        if not  verify_password(signin_request.password, app_user.password):
            logger.warning(f"User authentication failed - invalid credentials: {signin_request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Generate JWT token
        token = self.jwt_util.generate_token(
            username=signin_request.email,
            first_name=app_user.firstName,
            roles=app_user.roles,
            permissions=app_user.permissions
        )

        return SuccessResponse(
            data=AuthenticatedUser(
                    firstName=app_user.firstName,
                    email=signin_request.email,
                    token=token,
                    roles=app_user.roles,
                    permissions=app_user.permissions
                ),
            message="Login successful",
            status_code=sc.SUCCESS)

    async def sign_out(self, token: str) -> SuccessResponse[Dict[str, Any]]:
      logger.info("User signout successful")
      return SuccessResponse(
          data={"message": "user logout successful", "status": "success"},
          status_code=sc.SUCCESS)
    
    async def get_user_permissions(self, token: str) -> SuccessResponse[AccessPermissions]:
        """Get user permissions by validating JWT token"""
        # Validate JWT token
        if not self.jwt_util.is_token_valid(token):
            logger.warning("Invalid JWT token provided for permissions request")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        # Extract user information from JWT token
        email = self.jwt_util.extract_username(token)
        first_name = self.jwt_util.extract_first_name(token)
        roles = self.jwt_util.extract_roles(token)
        permissions = self.jwt_util.extract_permissions(token)

        logger.debug(f"Retrieved permissions for user: {email}")
        return SuccessResponse(
            data=AccessPermissions(
                    firstName=first_name,
                    email=email,
                    roles=roles,
                    permissions=permissions
                ),
            status_code=sc.SUCCESS)

    async def assign_roles(self, email: str, roles: list[str],admin_user:str) -> SuccessResponse[Dict[str, Any]]:
        """Assign roles to a user by email"""
        # Validate roles list is not empty
        if not roles:
            logger.warning(f"Empty roles list provided for user: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Roles list cannot be empty"
            )

        # Assign roles via repository (raises BusinessException if user not found)
        await assign_roles(email, roles,admin_user)

        logger.info(f"Roles assigned successfully for user: {email}, roles: {roles}")
        return SuccessResponse(
            data={"message": "Roles assigned successfully", "status": "success", "email": email, "roles": roles},
            status_code=sc.SUCCESS
        )

    async def assign_permissions(self, email: str, permissions: list[str],admin_user:str) -> SuccessResponse[Dict[str, Any]]:
        """Assign permissions to a user by email"""
        # Validate permissions list is not empty
        if not permissions:
            logger.warning(f"Empty permissions list provided for user: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permissions list cannot be empty"
            )

        # Assign permissions via repository (raises BusinessException if user not found)
        await assign_permissions(email, permissions,admin_user)

        logger.info(f"Permissions assigned successfully for user: {email}, permissions: {permissions}")
        return SuccessResponse(
            data={"message": "Permissions assigned successfully", "status": "success", "email": email, "permissions": permissions},
            status_code=sc.SUCCESS
        )

#Global instance
auth_service = AuthenticationService()