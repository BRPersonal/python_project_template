from fastapi.responses import JSONResponse,Response
from models.api_responses import SuccessResponse,ErrorResponse
from typing import Union
from models.status_code import sc

def to_json_response(result: Union[SuccessResponse, ErrorResponse]) -> Union[JSONResponse | Response]:

  if result.status_code == sc.NO_CONTENT:
    return Response(status_code=sc.NO_CONTENT)
  else:
    return JSONResponse(
          content=result.model_dump(exclude_none=True),
          status_code=result.status_code)

