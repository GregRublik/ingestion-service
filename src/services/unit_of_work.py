from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import asyncpg
from exceptions import DatabaseUnavailableException


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc is not None:
            try:
                await self.session.rollback()
            finally:
                await self.session.close()

            # 👉 здесь обрабатываем ошибку подключения
            if isinstance(
                exc,
                (
                    SQLAlchemyError,
                    asyncpg.PostgresError,
                    ConnectionRefusedError,
                    OSError,
                ),
            ):
                raise DatabaseUnavailableException(exc) from exc

            # если это не ошибка БД — пробрасываем дальше
            raise exc

        # если ошибки не было
        try:
            await self.session.commit()
        except (
            SQLAlchemyError,
            asyncpg.PostgresError,
            ConnectionRefusedError,
            OSError,
        ) as e:
            await self.session.rollback()
            raise DatabaseUnavailableException(e) from e
        finally:
            await self.session.close()
