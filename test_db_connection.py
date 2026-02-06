"""
Test Neon PostgreSQL database connection.
"""

import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from backend.config import settings

async def test_connection():
    """Test database connection"""
    print("Testing connection to Neon database...")
    print("Host: ep-odd-queen-a77a8hbk-pooler.ap-southeast-2.aws.neon.tech")

    try:
        engine = create_async_engine(settings.database_url, echo=False)

        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"SUCCESS: Connection successful! Test query returned: {row}")

        await engine.dispose()
        print("SUCCESS: Database connection verified")
        return True

    except Exception as e:
        print(f"FAILED: Connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    exit(0 if success else 1)
