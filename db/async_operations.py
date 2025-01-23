from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from db.models import Item


async def add_items(items: [Item], session_local: async_sessionmaker[AsyncSession]) -> None:
    async with session_local() as session:
        session.add_all(items)
        await session.commit()

async def query_db(query: Item, session_local: async_sessionmaker[AsyncSession], n=5) -> Sequence[Item]:
    async with session_local() as session:
        answer = (
            await session
            .scalars(
                select(Item)
                .order_by(Item.vec.l2_distance(query))
                .limit(n)
            )
        )
        await session.commit()
        return answer.all()
