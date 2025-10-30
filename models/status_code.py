from pydantic import BaseModel, Field

class StatusCode(BaseModel):
  SUCCESS : int = Field(200)
  ENTITY_CREATION_SUCCESSFUL: int = Field(201)
  REQUEST_ACCEPTED: int = Field(202)  #for background processing
  ENTITY_DELETION_SUCCESSFUL: int = Field(204)
  NO_CONTENT: int = Field(204)
  ENTITY_NOT_FOUND : int = Field(404)
  VALIDATION_ERROR: int = Field(400)
  DUPLICATE_ENTITY: int = Field(409)
  DB_CONNECTION_ERROR: int = Field(503)
  UNPROCESSABLE_ENTITY: int = Field(422)
  UNAUTHORIZED: int = Field(401)
  FORBIDDEN: int = Field(403)
  INTERNAL_SERVER_ERROR: int = Field(500)

# Global singleton instance
sc = StatusCode()
