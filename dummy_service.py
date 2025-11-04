from models.dummy_models import User,UserRequest
from models.api_responses import SuccessResponse,ErrorResponse
from models.status_code import sc
from business_exception import BusinessException
from utils.mongo_db_manager import mongodb_manager
from mongo_collection_names import CollectionNames
from pymongo.errors import DuplicateKeyError


class UserService:
  
  async def create_user(self,request: UserRequest) -> SuccessResponse[User]:

    try:
      if request.weight == 100:  #simulate business logic violation exception
        raise BusinessException(
            message="User with weight 100 is not acceptable",
            error_code=sc.VALIDATION_ERROR
        )
      elif request.weight == 200: #simulate unexpected exception
        raise ValueError("Something unexpected happened for weight 200")

      user_profile_collection = mongodb_manager.get_collection(CollectionNames.USER_PROFILE)
      result = await user_profile_collection.insert_one(request.model_dump(exclude_none=True))

      return SuccessResponse[User](
              data=User(id=str(result.inserted_id),name=request.name,email=request.email),
              message="User creation successful",
              status_code=sc.ENTITY_CREATION_SUCCESSFUL
      )

    except DuplicateKeyError:
      raise BusinessException(
        message=f"email {request.email} already exists",
        error_code=sc.VALIDATION_ERROR
      )

  async def delete_user(self,email: str) -> SuccessResponse[None]:

    user_profile_collection = mongodb_manager.get_collection(CollectionNames.USER_PROFILE)
    result = await user_profile_collection.delete_one({"email": email})

    if result.deleted_count == 0:
      raise BusinessException(
        message=f"User {email} not found",
        error_code = sc.ENTITY_NOT_FOUND
      )
    else:
      return SuccessResponse[None](
        data=None,
        message=f"User {email } deleted successfully",
        status_code = sc.ENTITY_DELETION_SUCCESSFUL
      )


#Global instance
user_service = UserService()