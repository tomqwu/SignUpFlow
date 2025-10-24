"""
Configuration settings for SignUpFlow application.

Loads settings from environment variables with validation.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "sqlite:///./roster.db"

    # JWT Authentication
    SECRET_KEY: str = "change-this-to-a-random-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    # Application
    APP_URL: str = "http://localhost:8000"
    TESTING: bool = False

    # Email Service (General)
    EMAIL_FROM: str = "noreply@signupflow.io"
    EMAIL_FROM_NAME: str = "SignUpFlow"
    EMAIL_ENABLED: bool = True

    # Mailtrap (Development Email Testing)
    MAILTRAP_SMTP_HOST: str = "sandbox.smtp.mailtrap.io"
    MAILTRAP_SMTP_PORT: int = 2525
    MAILTRAP_SMTP_USER: Optional[str] = None
    MAILTRAP_SMTP_PASSWORD: Optional[str] = None
    MAILTRAP_API_TOKEN: Optional[str] = None
    MAILTRAP_ACCOUNT_ID: Optional[str] = None
    MAILTRAP_INBOX_ID: Optional[str] = None

    # SendGrid (Production Email Delivery)
    SENDGRID_API_KEY: Optional[str] = None

    # Celery Task Queue
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Email Notification Features
    EMAIL_SEND_ASSIGNMENT_NOTIFICATIONS: bool = True
    EMAIL_SEND_REMINDERS: bool = True
    EMAIL_SEND_UPDATE_NOTIFICATIONS: bool = True
    EMAIL_REMINDER_HOURS_BEFORE: int = 24

    # Rate Limiting
    RATE_LIMIT_SIGNUP_MAX: int = 3
    RATE_LIMIT_SIGNUP_WINDOW: int = 3600
    RATE_LIMIT_LOGIN_MAX: int = 5
    RATE_LIMIT_LOGIN_WINDOW: int = 300
    RATE_LIMIT_CREATE_ORG_MAX: int = 2
    RATE_LIMIT_CREATE_ORG_WINDOW: int = 3600
    RATE_LIMIT_CREATE_INVITATION_MAX: int = 10
    RATE_LIMIT_CREATE_INVITATION_WINDOW: int = 300
    RATE_LIMIT_VERIFY_INVITATION_MAX: int = 10
    RATE_LIMIT_VERIFY_INVITATION_WINDOW: int = 60
    RATE_LIMIT_PASSWORD_RESET_MAX: int = 3
    RATE_LIMIT_PASSWORD_RESET_WINDOW: int = 3600
    RATE_LIMIT_PASSWORD_RESET_CONFIRM_MAX: int = 5
    RATE_LIMIT_PASSWORD_RESET_CONFIRM_WINDOW: int = 300

    # reCAPTCHA
    RECAPTCHA_SITE_KEY: Optional[str] = None
    RECAPTCHA_SECRET_KEY: Optional[str] = None

    # Stripe Payment Processing
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_PUBLIC_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_TEST_MODE: bool = True
    STRIPE_PRICE_STARTER_MONTHLY: Optional[str] = None
    STRIPE_PRICE_STARTER_ANNUAL: Optional[str] = None
    STRIPE_PRICE_PRO_MONTHLY: Optional[str] = None
    STRIPE_PRICE_PRO_ANNUAL: Optional[str] = None
    STRIPE_PRICE_ENTERPRISE_MONTHLY: Optional[str] = None
    STRIPE_PRICE_ENTERPRISE_ANNUAL: Optional[str] = None

    # Twilio SMS Service
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    TWILIO_TEST_MODE: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
