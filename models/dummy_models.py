#Dummy models just to test exception handling flows
from pydantic import BaseModel, Field,field_validator, model_validator

class User(BaseModel):
  id: str = Field(...,description="unique user id")
  name: str = Field(...,description="full name")
  email: str = Field(...,description="email")

class UserRequest(BaseModel):
  name: str = Field(...,description="full name")
  email: str = Field(...,description="email")
  weight: float = Field(..., description="Current weight in kg (0.1-500)")
  goal_weight: float = Field(..., gt=0, le=300, description="Target weight in kg (0.1-300)")

  @field_validator('weight')
  @classmethod
  def validate_weight(cls, v: float) -> float:
    """Validate weight is within realistic human range"""
    if v < 20.0:
      raise ValueError("Weight must be at least 20 kg for safety")
    if v > 300.0:
      raise ValueError("Weight must be less than 300 kg for realistic calculations")
    return round(v, 1)

  @model_validator(mode='after')
  def validate_realistic_goals(self):
    if self.goal_weight >= self.weight:
      raise ValueError("Goal weight must be less than current weight for weight loss")
    return self


