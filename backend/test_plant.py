import asyncio
import sys
sys.path.append('/Users/admin/Downloads/label check/backend')

from app.services.substance_mapper_service import SubstanceMapperService

async def test():
    mapper = SubstanceMapperService()
    result = await mapper._find_plant_in_db("екстракт півонії")
    print(f"Знайдено: {result}")

asyncio.run(test())
