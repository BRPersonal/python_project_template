import jwt
import base64
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any, Callable
from fastapi import Request
from utils.config import settings
from utils.logger import logger
from .jwt_exception import JwtException


class JwtUtil:
    """JWT utility class for token generation, validation, and claim extraction."""
    
    # Constants for claim keys
    FIRST_NAME_KEY = "FIRST_NAME"
    ROLE_KEY = "ROLES"
    PERMISSION_KEY = "PERMISSIONS"
    
    # JWT signing algorithm constant
    JWT_SIGNING_ALGORITHM = "HS256"
    
    def __init__(self):
        """Initialize JWT utility with configuration."""
        self.secret_key = settings.JWT_SECRET_KEY
        self.jwt_expiration = settings.JWT_EXPIRATION
        

    def extract_raw_token_from_header(self, request: Request, throw_exception_if_not_found: bool = False) -> Optional[str]:
        """
        Extract raw JWT token from Authorization header.
        
        Args:
            request: FastAPI Request object
            throw_exception_if_not_found: Whether to raise exception if token not found
            
        Returns:
            Raw JWT token string or None
            
        Raises:
            JwtException: If token is missing and throw_exception_if_not_found is True
        """
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            if throw_exception_if_not_found:
                raise JwtException("Bearer token missing")
            return None
        
        return auth_header[7:]  # Remove "Bearer " prefix
    
    def generate_token(self, username: str, first_name: str, roles: List[str], permissions: List[str]) -> str:
        """
        Generate JWT token with user information.
        
        Args:
            username: User's username/email
            first_name: User's first name
            roles: List of user roles
            permissions: List of user permissions
            
        Returns:
            JWT token string
        """
        extra_claims = {
            self.FIRST_NAME_KEY: first_name,
            self.ROLE_KEY: roles,
            self.PERMISSION_KEY: permissions
        }
        
        return self._generate_token(extra_claims, username)
    
    def is_token_valid(self, token: str) -> bool:
        try:
            return not self.is_token_expired(token)
        except JwtException:
            return False
    
    def is_token_expired(self, token: str) -> bool:
      expiration_date = self.extract_expiration(token)
      return expiration_date < datetime.now(timezone.utc)
    
    def get_issued_date(self, token: str) -> datetime:
        return self._extract_claim(token, lambda claims: datetime.fromtimestamp(claims.get('iat', 0), tz=timezone.utc))
    
    def extract_username(self, token: str) -> str:
        return self._extract_claim(token, lambda claims: claims.get('sub'))
    
    def extract_first_name(self, token: str) -> str:
        return self._extract_claim(token, lambda claims: claims.get(self.FIRST_NAME_KEY))
    
    def extract_roles(self, token: str) -> List[str]:
        return self._extract_claim(token, lambda claims: claims.get(self.ROLE_KEY, []))
    
    def extract_permissions(self, token: str) -> List[str]:
        return self._extract_claim(token, lambda claims: claims.get(self.PERMISSION_KEY, []))
    
    def extract_expiration(self, token: str) -> datetime:
        return self._extract_claim(token, lambda claims: datetime.fromtimestamp(claims.get('exp', 0), tz=timezone.utc))
    
    def _generate_token(self, extra_claims: Dict[str, Any], username: str) -> str:
        """
        Generate JWT token with claims and username.
        
        Args:
            extra_claims: Additional claims to include
            username: Username for subject
            
        Returns:
            JWT token string
        """
        try:
            now = datetime.now(timezone.utc)
            expiration = now + timedelta(milliseconds=self.jwt_expiration)
            
            payload = {
                **extra_claims,
                'sub': username,
                'iat': now,
                'exp': expiration
            }
            
            token = jwt.encode(
                payload,
                self._get_signing_key(),
                algorithm=self.JWT_SIGNING_ALGORITHM
            )
            
            return token
            
        except Exception as e:
            logger.error(f"Error generating JWT token: {str(e)}")
            raise JwtException("Failed to generate JWT token", original_exception=e)
    
    def _extract_claim(self, token: str, resolver: Callable[[Dict[str, Any]], Any]) -> Any:
        """
        Extract specific claim from token using resolver function.
        
        Args:
            token: JWT token string
            resolver: Function to extract specific claim from claims dict
            
        Returns:
            Extracted claim value
            
        Raises:
            JwtException: If token is invalid or malformed
        """
        try:
            all_claims = self._extract_all_claims(token)
            return resolver(all_claims)
        except Exception as e:
            logger.error(f"Error extracting claim from token: {str(e)}")
            raise JwtException("Invalid JWT Token", original_exception=e)
    
    def _extract_all_claims(self, token: str) -> Dict[str, Any]:
        """
        Extract all claims from JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Dictionary of all claims
            
        Raises:
            JwtException: If token is invalid or malformed
        """
        try:
            payload = jwt.decode(
                token,
                self._get_signing_key(),
                algorithms=[self.JWT_SIGNING_ALGORITHM]
            )
            return payload
            
        except jwt.ExpiredSignatureError:
            raise JwtException("JWT token has expired")
        except jwt.InvalidSignatureError:
            raise JwtException("Invalid JWT signature")
        except jwt.DecodeError as e:
            logger.error(f"JWT decode error: {str(e)}")
            raise JwtException("Invalid JWT Token", original_exception=e)
        except Exception as e:
            logger.error(f"Unexpected JWT error: {str(e)}")
            raise JwtException("Invalid JWT Token", original_exception=e)
    
    def _get_signing_key(self) -> str:
        """
        Get the signing key for JWT operations.
        
        Returns:
            Signing key string
            
        Raises:
            JwtException: If secret key is invalid
        """
        try:
            # Decode base64 secret key
            key_bytes = base64.b64decode(self.secret_key)
            return key_bytes
        except Exception as e:
            logger.error(f"Error processing JWT secret key: {str(e)}")
            raise JwtException("Invalid JWT secret key configuration", original_exception=e)
