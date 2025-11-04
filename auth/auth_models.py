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

class SignInResponse(BaseModel):
    """Model for sign-in response"""
    firstName: str
    email: str
    token: str
    message: str
    roles: Optional[List[str]] = []
    permissions: Optional[List[str]] = []


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

class AppUser(BaseModel):
    """Model for app user"""
    firstName: str
    lastName: str
    email: EmailStr
    password: str
    roles: Optional[List[str]] = []
    permissions: Optional[List[str]] = []
    social_login_ids: Optional[str] = None
