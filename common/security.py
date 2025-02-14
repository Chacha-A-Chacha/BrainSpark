# app/security.py
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.logger import logger
import hashlib
import httpx
import re
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, validator
from typing import Optional, Callable
from app.core.config import settings

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)
http_bearer = HTTPBearer(auto_error=False)

class SecurityService:
    def __init__(self):
        self.recaptcha_url = "https://www.google.com/recaptcha/api/siteverify"
        
    def get_voter_identifier(self, request: Request) -> str:
        """
        Generate a unique voter hash using IP, User-Agent, and secret pepper
        """
        ip = request.client.host
        user_agent = request.headers.get("User-Agent", "")
        secret_pepper = settings.SECRET_KEY.encode()
        
        digest = hashlib.pbkdf2_hmac(
            'sha256',
            f"{ip}-{user_agent}".encode(),
            secret_pepper,
            100000
        )
        return digest.hex()

    async def validate_captcha(self, token: str) -> bool:
        """
        Verify reCAPTCHA v3 token with Google's API
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.recaptcha_url,
                    data={
                        "secret": settings.RECAPTCHA_SECRET,
                        "response": token
                    }
                )
                result = response.json()
                return result.get("success", False) and result.get("score", 0) >= 0.5
        except Exception as e:
            logger.error(f"reCAPTCHA validation failed: {str(e)}")
            return False

    def rate_limit_check(self, request: Request):
        """
        Custom rate limiting using voter identifier
        """
        identifier = self.get_voter_identifier(request)
        return identifier

# Initialize security service
security_service = SecurityService()

# Rate limiters using voter identifier
submission_limiter = Limiter(key_func=security_service.rate_limit_check)
voting_limiter = Limiter(key_func=security_service.rate_limit_check)

def input_sanitizer(field: str) -> str:
    """
    Sanitize user input to prevent XSS and injection attacks
    """
    cleaned = re.sub(r'<[^>]*>', '', field)  # Remove HTML tags
    return cleaned.strip()[:500]  # Limit length

class SanitizedText(BaseModel):
    """
    Pydantic model with automatic input sanitization
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise ValueError("Must be a string")
        return input_sanitizer(v)

async def verify_captcha_dependency(
    request: Request,
    captcha_token: Optional[str] = None
):
    """
    Dependency for CAPTCHA validation
    """
    if settings.ENABLE_RECAPTCHA:
        if not captcha_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CAPTCHA token required"
            )
            
        if not await security_service.validate_captcha(captcha_token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid CAPTCHA verification"
            )

async def rate_limit_exceeded_handler(
    request: Request,
    exc: RateLimitExceeded
):
    """
    Custom rate limit exceeded response
    """
    logger.warning(f"Rate limit exceeded for {request.client.host}")
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Too many requests. Please try again later."
    )

def security_headers(request: Request, call_next):
    """
    Add security headers to all responses
    """
    response = call_next(request)
    response.headers.update({
        "Content-Security-Policy": "default-src 'self'",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    })
    return response
