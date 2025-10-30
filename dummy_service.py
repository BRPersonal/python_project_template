from utils.logger import logger
from models.dummy_models import User,UserRequest
from models.api_responses import SuccessResponse,ErrorResponse
from models.status_code import sc
from business_exception import BusinessException
from typing import TypeAlias,Union

UserResponse : TypeAlias = Union[SuccessResponse[User], ErrorResponse]

class UserService:
  
  async def create_user(self,request: UserRequest) -> UserResponse:
    if request.weight == 100:  #simulate business logic violation exception
      raise BusinessException(
          message="User with weight 100 is not accepted",
          error_code=sc.VALIDATION_ERROR
      )
    elif request.weight == 200: #simulate unexpected exception
      raise ValueError("Something unexpected happened for weight 200")

    return SuccessResponse[User](
            data=User(id=100,name=request.name,email=request.email),
            message="User creation successful",
            status_code=sc.ENTITY_CREATION_SUCCESSFUL
    )

  async def delete_user(self,user_id: int) -> Union[SuccessResponse[None], ErrorResponse]:
    if user_id == 100:
      return SuccessResponse[None](
        data=None,
        message=f"User {user_id } deleted successfully",
        status_code = sc.ENTITY_DELETION_SUCCESSFUL
      )
    else:
      raise BusinessException(
        message=f"User {user_id} not found",
        error_code = sc.ENTITY_NOT_FOUND
      )

#Global instance
user_service = UserService()