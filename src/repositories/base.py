from abc import ABC, abstractmethod

from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete
from sqlalchemy.exc import IntegrityError, NoResultFound, MultipleResultsFound

from exceptions import ModelAlreadyExistsException, ModelNotFoundException, ModelMultipleResultsFoundException

class AbstractRepository(ABC):
    """
    Абстрактный репозиторий нужен чтобы при наследовании определяли его базовые методы работы с бд
    """
    model = None

    @abstractmethod
    async def add_one(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, *args, **kwargs):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    """
    Репозиторий для работы с sqlalchemy
    """
    model = None

    async def add_one(self, session: AsyncSession, data: dict):
        stmt = insert(self.model).values(**data).returning(self.model)
        try:
            res = await session.execute(stmt)
            return res.scalar_one()
        except IntegrityError:
            raise ModelAlreadyExistsException

    async def change_one(self, session: AsyncSession, object_id: int | UUID4, data: dict):
        stmt = update(self.model).where(self.model.id == object_id).values(**data).returning(self.model)
        try:
            res = await session.execute(stmt)
            return res.scalar_one()
        except NoResultFound:
            raise ModelNotFoundException

    async def delete_by_id(
        self,
        session: AsyncSession,
        object_id: int | UUID4
    ):
        stmt = (
            delete(self.model)
            .where(self.model.id == object_id)
            .returning(self.model)
        )

        res = await session.execute(stmt)

        obj = res.scalar_one_or_none()

        if obj is None:
            raise ModelNotFoundException

        return obj

    async def get_all(self, session: AsyncSession):
        stmt = select(self.model).order_by(self.model.id) # self.model.id.desc()
        try:
            res = await session.execute(stmt)
            return res.scalars().all()
        except NoResultFound:
            raise ModelNotFoundException

    async def get_by_id(self, session: AsyncSession, object_id: int | UUID4):
        stmt = select(self.model).where(self.model.id == object_id).limit(1)
        try:
            res = await session.execute(stmt)
            return res.scalar_one()
        except NoResultFound:
            raise ModelNotFoundException
        except MultipleResultsFound:
            raise ModelMultipleResultsFoundException
