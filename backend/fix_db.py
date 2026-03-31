import asyncio
from sqlalchemy import text
from app.database import engine

async def fix():
    async with engine.begin() as conn:
        print('Executing ALTER TABLE...')
        try:
            await conn.execute(text('ALTER TABLE money_companies ADD COLUMN owner_id INTEGER;'))
            print('Added owner_id to money_companies')
        except Exception as e:
            print(f'Error adding owner_id: {e}')
            
        try:
            await conn.execute(text('ALTER TABLE money_companies ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;'))
            await conn.execute(text('ALTER TABLE money_companies ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;'))
            print('Added timestamp columns')
        except Exception as e:
            print(f'Error adding timestamp columns: {e}')
    
    print('done')

asyncio.run(fix())
