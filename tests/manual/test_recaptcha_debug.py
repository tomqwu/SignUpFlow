"""Quick test to see what Google returns for our keys."""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from api.utils.recaptcha import verify_recaptcha

async def test():
    # Test with a fake token to see the error
    is_valid, score = await verify_recaptcha("test_fake_token_12345", "127.0.0.1")
    print(f"Result: is_valid={is_valid}, score={score}")

if __name__ == "__main__":
    asyncio.run(test())
