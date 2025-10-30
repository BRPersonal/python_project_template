from fastapi import APIRouter, HTTPException, Depends, status
from dummy_service import user_service
from models.dummy_models import UserRequest
from utils.commons import to_json_response

dummy_router = APIRouter(prefix="/api/v1/user", tags=["user"])  

@dummy_router.post("")
async def create_user(request: UserRequest):
  result = await user_service.create_user(request)
  return to_json_response(result)

@dummy_router.delete("/{user_id}")
async def delete_user(user_id: int):
  result = await user_service.delete_user(user_id)
  return to_json_response(result)

