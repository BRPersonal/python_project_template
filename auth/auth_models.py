from pydantic import BaseModel, EmailStr
from typing import List, Optional


class SignUpRequest(BaseModel):
    """Model for user sign-up request"""
    firstName: str
    lastName: str
    email: EmailStr
    password: str

class SignInRequest(BaseModel):
    """Model for user sign-in request"""
    email: EmailStr
    password: str

class AccessPermissions(BaseModel):
    """Model for user access permissions"""
    firstName: str
    email: str
    roles: Optional[List[str]] = []
    permissions: Optional[List[str]] = []

class AuthenticatedUser(BaseModel):
    """Model for authenticated user context"""
    firstName: str
    email: str
    roles: Optional[List[str]] = []
    permissions: Optional[List[str]] = []
    token: str = None

class AssignRolesRequest(BaseModel):
    """Model for assigning roles request"""
    email: EmailStr
    roles: List[str]

class AssignPermissionsRequest(BaseModel):
    """Model for assigning permissions request"""
    email: EmailStr
    permissions: List[str]


class AppUser(BaseModel):
    """Model for app user"""
    firstName: str
    lastName: str
    email: EmailStr
    password: str
    roles: Optional[str] = None
    permissions: Optional[str] = None
    social_login_ids: Optional[str] = None
