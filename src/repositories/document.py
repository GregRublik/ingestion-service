from repositories.base import SQLAlchemyRepository
from models.document import Document
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from exceptions import ModelNoFoundException


class DocumentRepository(SQLAlchemyRepository):
    model = Document

    async def get_by_status(self, session: AsyncSession, status: str):
        stmt = select(self.model).where(self.model.status == status)
        try:
            res = await session.execute(stmt)
            return res.scalars().all()
        except NoResultFound:
            raise ModelNoFoundException
