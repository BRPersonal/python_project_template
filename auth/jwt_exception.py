from business_exception import BusinessException
from models.status_code import sc
from typing import Optional

class JwtException(BusinessException):
    def __init__(
        self,
        message: str,
        original_exception: Optional[Exception] = None
    ):
        super().__init__(message=message,
                         error_code=sc.FORBIDDEN,
                         original_exception=original_exception)
