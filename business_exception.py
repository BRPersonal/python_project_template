from typing import Optional, Any

class BusinessException(Exception):
  def __init__(
    self,
    message: str,
    error_code: int,
    original_exception: Optional[Exception] = None,
    details: Optional[Any] = None
  ):
    self.message = message
    self.error_code = error_code
    self.original_exception = original_exception
    self.details = details or {}
    super().__init__(self.message)

  def __str__(self) -> str:
    return f"[{self.error_code}] {self.message}"

  def __repr__(self) -> str:
    return (f"{self.__class__.__name__}(message={self.message!r}, "
            f"error_code={self.error_code!r}, "
            f"details={self.details!r})")
