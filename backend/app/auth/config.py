import os
from dotenv import load_dotenv

load_dotenv()


class AuthConfig:
    """
    Authentication configuration.
    All sensitive values should be loaded from environment variables.
    """

    # JWT Configuration
    SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        # Default key for development only - MUST be changed in production
        "your-secret-key-change-this-in-production-please-use-a-long-random-string"
    )
    ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Admin User Configuration (for seeding)
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@art.oem")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "changeme")

    @classmethod
    def validate(cls):
        """
        Validate configuration.
        Warns if default values are being used in production.
        """
        if cls.SECRET_KEY == "your-secret-key-change-this-in-production-please-use-a-long-random-string":
            print("WARNING: Using default JWT secret key! This is insecure in production!")

        if cls.ADMIN_PASSWORD == "changeme":
            print("WARNING: Using default admin password! Change this immediately!")

        return True


# Validate config on import
AuthConfig.validate()
