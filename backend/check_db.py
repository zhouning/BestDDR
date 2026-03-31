import asyncio
import os
import asyncpg

async def check():
    url = "postgresql://agent_user:SuperMap%40123@119.3.175.198:5432/flights_dataset"
    print(f"Connecting to {url}")
    conn = await asyncpg.connect(url)
    try:
        await conn.execute("ALTER TABLE money_companies ADD COLUMN owner_id INTEGER;")
        print("Added owner_id")
    except Exception as e:
        print(f"Error 1: {e}")
        
    try:
        await conn.execute("ALTER TABLE money_companies ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;")
        print("Added created_at")
    except Exception as e:
        print(f"Error 2: {e}")
        
    try:
        await conn.execute("ALTER TABLE money_companies ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;")
        print("Added updated_at")
    except Exception as e:
        print(f"Error 3: {e}")
        
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check())
