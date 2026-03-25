import asyncio
import httpx
from app.database import AsyncSessionLocal
from app.models.user import User
from app.auth.jwt import create_access_token
from sqlalchemy import select

async def test():
    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).limit(1))
    
    token = create_access_token({"user_id": str(user.id), "role": user.role.value})
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "http://localhost:8000/chat", 
            json={"message": "hello", "conversation_history": []}, 
            headers={"Authorization": f"Bearer {token}"}, 
            timeout=20.0
        )
        print("STATUS:", res.status_code)
        print("BODY:", res.text)

if __name__ == "__main__":
    asyncio.run(test())
