from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from .auth_models import AppUser
from business_exception import BusinessException
from models.status_code import sc
from utils.config import settings
import bcrypt
from utils.logger import logger
from utils.postgre_db_manager import postgre_manager

def _hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    try:
        # Generate salt and hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception as error:
        raise BusinessException(
            message=f"Failed to hash password: {str(error)}",
            error_code = sc.VALIDATION_ERROR,
            original_exception=error
        )


async def create_user(user: AppUser) -> None:
    """Create a new user in the app_user table"""
    try:
        # Prepare SQL query to INSERT a new user
        insert_query = """
            INSERT INTO app_user (first_name, last_name, email_id, password, roles, permissions, created_by, created_on, last_updated_by, last_updated_on)
            VALUES (:firstName, :lastName, :email, :password, :roles, :permissions, :createdBy, NOW(), :lastUpdatedBy, NOW());
        """

        # Hash the password before storing
        hashed_password = _hash_password(user.password)

        # Convert roles and permissions lists to comma-separated strings
        roles_str = ','.join(user.roles) if user.roles else ''
        permissions_str = ','.join(user.permissions) if user.permissions else ''

        values = {
            'firstName': user.firstName,
            'lastName': user.lastName,
            'email': user.email,
            'password': hashed_password,
            'roles': roles_str,
            'permissions': permissions_str,
            'createdBy': 'system',
            'lastUpdatedBy': 'system'
        }

        await postgre_manager.execute(query=insert_query, values=values)

    except Exception as error:
        raise BusinessException(
            message=f"Failed to create user: {str(error)}",
            error_code = sc.VALIDATION_ERROR,
            original_exception=error,
            details={"user_email": user.email}
        )

async def is_user_exists(email: str) -> bool:
    """Check if a user exists by email"""
    query = "SELECT COUNT('x') FROM app_user WHERE email_id = :email"
    params = {"email": email}
    result =  await postgre_manager.fetch_one(query=query, values=params)
    return True if result and result[0] != 0 else False

async def get_users_count() -> int:
    """Get the total count of users in the app_user table"""
    query = "SELECT COUNT('x') FROM app_user"
    result = await postgre_manager.fetch_one(query=query)
    return result[0] if result else 0

async def get_app_user(email: str) -> AppUser:
    """Get user by email address"""
    query = """
        SELECT first_name, last_name, email_id, password, roles, permissions, social_login_ids
        FROM app_user 
        WHERE email_id = :email
    """
    params = {"email": email}
    record = await postgre_manager.fetch_one(query=query, values=params)

    if not record:
        raise BusinessException(
            message=f"User with email '{email}' not found",
            error_code=sc.ENTITY_NOT_FOUND
        )

    # Convert comma-separated strings to lists
    roles = record['roles'].split(',') if record['roles'] else []
    roles = [role.strip() for role in roles if role.strip()]

    permissions = record['permissions'].split(',') if record['permissions'] else []
    permissions = [permission.strip() for permission in permissions if permission.strip()]

    return AppUser(
        firstName=record['first_name'],
        lastName=record['last_name'],
        email=record['email_id'],
        password=record['password'],  # Return actual password hash
        roles=roles,
        permissions=permissions,
        social_login_ids=record['social_login_ids'] if record['social_login_ids'] else None
    )


async def assign_roles(email: str, roles: list[str],admin_user:str) -> None:
    """Assign roles to a user by email"""
    # Check if user exists
    user_exists = await is_user_exists(email)
    if not user_exists:
        raise BusinessException(
            message=f"User with email '{email}' not found",
            error_code=sc.ENTITY_NOT_FOUND
        )

    # Update roles
    roles_str = ','.join(roles) if roles else ''
    update_query = """
        UPDATE app_user 
        SET roles = :roles, last_updated_by = :updatedBy, last_updated_on = NOW()
        WHERE email_id = :email
    """

    values = {
        'roles': roles_str,
        'updatedBy': admin_user,
        'email': email
    }
    await postgre_manager.execute(query=update_query,values=values)


async def assign_permissions(email: str, permissions: list[str],admin_user:str) -> None:
    """Assign permissions to a user by email"""
    # Check if user exists
    user_exists = await is_user_exists(email)
    if not user_exists:
        raise BusinessException(
            message=f"User with email '{email}' not found",
            error_code=sc.ENTITY_NOT_FOUND
        )

    # Update permissions
    permissions_str = ','.join(permissions) if permissions else ''
    update_query = """
        UPDATE app_user 
        SET permissions = :permissions, last_updated_by = :updatedBy, last_updated_on = NOW()
        WHERE email_id = :email
    """

    values = {
        'permissions': permissions_str,
        'updatedBy': admin_user,
        'email': email
    }
    await postgre_manager.execute(query=update_query,values=values)

def get_all_roles() -> list[str]:
    """Get all allowed roles from configuration"""
    roles_str = settings.ALLOWED_ROLES
    if not roles_str or roles_str.strip() == '':
        return []
    
    # Split by comma and clean up whitespace
    roles = [role.strip() for role in roles_str.split(',') if role.strip()]
    return roles

def get_all_permissions() -> list[str]:
    """Get all allowed permissions from configuration"""
    permissions_str = settings.ALLOWED_PERMISSIONS
    if not permissions_str or permissions_str.strip() == '':
        return []
    
    # Split by comma and clean up whitespace
    permissions = [permission.strip() for permission in permissions_str.split(',') if permission.strip()]
    return permissions

async def update_password(email: str, new_password: str) -> None:
    """Update user password by email"""
    # Check if user exists
    user_exists = await is_user_exists(email)
    if not user_exists:
        raise BusinessException(
            message=f"User with email '{email}' not found",
            error_code=sc.ENTITY_NOT_FOUND
        )

    # Hash the new password before storing
    hashed_password = _hash_password(new_password)

    # Update password
    update_query = """
        UPDATE app_user 
        SET password = :password, last_updated_by = :updatedBy, last_updated_on = NOW()
        WHERE email_id = :email
    """

    values = {
        'password': hashed_password,
        'updatedBy': 'system',
        'email': email
    }
    await postgre_manager.execute(query=update_query, values=values)



def verify_password(user_password: str, password_in_db: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(user_password.encode('utf-8'), password_in_db.encode('utf-8'))
