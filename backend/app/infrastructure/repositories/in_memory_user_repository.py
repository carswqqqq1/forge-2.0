from datetime import UTC, datetime
from typing import List, Optional

from app.core.config import get_settings
from app.domain.models.user import User, UserRole
from app.domain.repositories.user_repository import UserRepository


class InMemoryUserRepository(UserRepository):
    """In-memory user repository for standalone development."""

    def __init__(self):
        self._users: dict[str, User] = {}
        self._settings = get_settings()
        self._seed_builtin_users()

    def _seed_builtin_users(self) -> None:
        if self._settings.auth_provider == "none" and "anonymous" not in self._users:
            self._users["anonymous"] = User(
                id="anonymous",
                fullname="anonymous",
                email="anonymous@localhost",
                role=UserRole.USER,
                is_active=True,
            )

        if self._settings.auth_provider == "local" and "local_admin" not in self._users:
            self._users["local_admin"] = User(
                id="local_admin",
                fullname="Local Admin",
                email=self._settings.local_auth_email,
                role=UserRole.ADMIN,
                is_active=True,
            )

    @staticmethod
    def _clone(user: User) -> User:
        return user.model_copy(deep=True)

    async def create_user(self, user: User) -> User:
        self._users[user.id] = self._clone(user)
        return self._clone(user)

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        user = self._users.get(user_id)
        return self._clone(user) if user else None

    async def get_user_by_fullname(self, fullname: str) -> Optional[User]:
        for user in self._users.values():
            if user.fullname == fullname:
                return self._clone(user)
        return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        normalized_email = email.strip().lower()
        for user in self._users.values():
            if user.email == normalized_email:
                return self._clone(user)
        return None

    async def update_user(self, user: User) -> User:
        if user.id not in self._users:
            raise ValueError(f"User not found: {user.id}")
        user.updated_at = datetime.now(UTC)
        self._users[user.id] = self._clone(user)
        return self._clone(user)

    async def delete_user(self, user_id: str) -> bool:
        if user_id not in self._users:
            return False
        del self._users[user_id]
        return True

    async def list_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        users = list(self._users.values())
        return [self._clone(user) for user in users[offset:offset + limit]]

    async def fullname_exists(self, fullname: str) -> bool:
        return any(user.fullname == fullname for user in self._users.values())

    async def email_exists(self, email: str) -> bool:
        normalized_email = email.strip().lower()
        return any(user.email == normalized_email for user in self._users.values())
