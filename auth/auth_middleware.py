from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List, Callable, Dict
from .auth_service import auth_service
from .auth_models import AuthenticatedUser
from utils.logger import logger
from utils.config import settings


# Security scheme for FastAPI
security = HTTPBearer(auto_error=False)

class AuthenticationMiddleware:
    """Middleware for handling authentication and authorization"""
    
    async def get_current_user(
        self, 
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> AuthenticatedUser:
        """
        Dependency to get the current authenticated user.
        First checks cache, then validates token if not cached.
        """
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        
        try:
            result = await auth_service.get_user_permissions(token)
            permissions = result.data
            
            authenticated_user = AuthenticatedUser(
                email=permissions.email,
                firstName=permissions.firstName,
                roles=permissions.roles,
                permissions=permissions.permissions,
                token=token
            )
            
            return authenticated_user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def require_roles(self, required_roles: List[str]) -> Callable:
        """
        Dependency factory to require specific roles.
        Usage: Depends(auth_middleware.require_roles(["ADMIN", "USER"]))
        """
        async def check_roles(
            current_user: AuthenticatedUser = Depends(self.get_current_user)
        ) -> AuthenticatedUser:
            if not any(role in current_user.roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required roles: {required_roles}"
                )
            return current_user
        
        return check_roles
    
    def require_permissions(self, required_permissions: List[str]) -> Callable:
        """
        Dependency factory to require specific permissions.
        Usage: Depends(auth_middleware.require_permissions(["READ_USER", "WRITE_USER"]))
        """
        async def check_permissions(
            current_user: AuthenticatedUser = Depends(self.get_current_user)
        ) -> AuthenticatedUser:
            if not any(perm in current_user.permissions for perm in required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required permissions: {required_permissions}"
                )
            return current_user
        
        return check_permissions
    
    def require_admin(self) -> Callable:
        """
        Dependency to require ADMIN role.
        Usage: Depends(auth_middleware.require_admin())
        """
        return self.require_roles(["admin"])

# Global instance
auth_middleware = AuthenticationMiddleware()

