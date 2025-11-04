from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from utils.logger import logger
from .auth_models import (
    SignInRequest, SignUpRequest, SignInResponse, AppUser,
    AccessPermissions
)
from models.api_responses import SuccessResponse
from models.status_code import sc
from .auth_repository import create_user, get_users_count,get_app_user, verify_password, is_user_exists
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
            roles="user",  # Default role
            permissions=""  # Default empty permissions
        )

        #If this is the first signup make the user as admin
        user_count = await get_users_count()
        if user_count == 0:
            app_user.roles = "admin"

        # Save user to database
        await create_user(app_user)

        logger.info(f"User registration successful for email: {signup_request.email}")
        return SuccessResponse(
            data={"message": "User registered successfully", "status": "success"},
            status_code=sc.ENTITY_CREATION_SUCCESSFUL
        )

    async def sign_in(self, signin_request: SignInRequest) -> SuccessResponse[SignInResponse]:
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

        # Split comma-separated roles and permissions into arrays
        roles = app_user.roles.split(',') if app_user.roles else []
        roles = [role.strip() for role in roles if role.strip()]

        permissions = app_user.permissions.split(',') if app_user.permissions else []
        permissions = [permission.strip() for permission in permissions if permission.strip()]

        # Generate JWT token
        token = self.jwt_util.generate_token(
            username=signin_request.email,
            first_name=app_user.firstName,
            roles=roles,
            permissions=permissions
        )

        logger.info(f"User authentication successful for email: {signin_request.email}")
        return SuccessResponse(
            data=SignInResponse(
                    firstName=app_user.firstName,
                    token=token,
                    message="Login successful",
                    roles=roles,
                    permissions=permissions
                ),
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

#Global instance
auth_service = AuthenticationService()