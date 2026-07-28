"""
backend/repositories/checkin_repo.py
Check-in sessions and weekly tasks persistence.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.db.models.checkin import CheckinSession, WeeklyTask
from backend.repositories.base import BaseRepository


def week_start_for(d: date | None = None) -> date:
    today = d or date.today()
    return today.fromordinal(today.toordinal() - today.weekday())


class CheckinRepository(BaseRepository[CheckinSession]):
    model = CheckinSession

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_current(
        self, *, tenant_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[CheckinSession]:
        ws = week_start_for()
        stmt = (
            select(CheckinSession)
            .options(selectinload(CheckinSession.weekly_tasks))
            .where(
                CheckinSession.tenant_id == tenant_id,
                CheckinSession.user_id == user_id,
                CheckinSession.week_start == ws,
            )
            .order_by(CheckinSession.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_with_tasks(self, session_id: uuid.UUID) -> Optional[CheckinSession]:
        stmt = (
            select(CheckinSession)
            .options(selectinload(CheckinSession.weekly_tasks))
            .where(CheckinSession.id == session_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_session(
        self,
        *,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> CheckinSession:
        row = CheckinSession(
            tenant_id=tenant_id,
            user_id=user_id,
            week_start=week_start_for(),
            messages=[],
            status="in_progress",
        )
        return await self.create(row)

    async def append_messages(
        self,
        session: CheckinSession,
        messages: list[dict[str, Any]],
    ) -> CheckinSession:
        current = list(session.messages or [])
        current.extend(messages)
        session.messages = current
        session.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return session

    async def complete(
        self,
        session: CheckinSession,
        *,
        summary: str | None = None,
    ) -> CheckinSession:
        session.status = "completed"
        if summary:
            session.summary = summary
        session.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return session

    async def list_recent_summaries(
        self,
        *,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        limit: int = 4,
    ) -> list[str]:
        stmt = (
            select(CheckinSession)
            .where(
                CheckinSession.tenant_id == tenant_id,
                CheckinSession.user_id == user_id,
                CheckinSession.summary.is_not(None),
            )
            .order_by(CheckinSession.week_start.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [s.summary for s in result.scalars().all() if s.summary]


class WeeklyTaskRepository(BaseRepository[WeeklyTask]):
    model = WeeklyTask

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def replace_tasks(
        self,
        *,
        checkin_session_id: uuid.UUID,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        titles: list[str],
    ) -> list[WeeklyTask]:
        existing = await self.session.execute(
            select(WeeklyTask).where(
                WeeklyTask.checkin_session_id == checkin_session_id
            )
        )
        for row in existing.scalars().all():
            await self.session.delete(row)

        created: list[WeeklyTask] = []
        for title in titles[:3]:
            task = WeeklyTask(
                checkin_session_id=checkin_session_id,
                tenant_id=tenant_id,
                user_id=user_id,
                title=title.strip(),
                is_completed=False,
            )
            self.session.add(task)
            created.append(task)
        await self.session.flush()
        return created

    async def list_for_user(
        self, *, tenant_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[WeeklyTask]:
        stmt = select(WeeklyTask).where(
            WeeklyTask.tenant_id == tenant_id,
            WeeklyTask.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def set_completed(
        self, task: WeeklyTask, completed: bool
    ) -> WeeklyTask:
        task.is_completed = completed
        task.completed_at = datetime.now(timezone.utc) if completed else None
        await self.session.flush()
        return task

    async def suspend_incomplete(
        self, *, tenant_id: uuid.UUID, user_id: uuid.UUID
    ) -> int:
        """Downscale: mark incomplete tasks with [ASKIDA] prefix."""
        tasks = await self.list_for_user(tenant_id=tenant_id, user_id=user_id)
        count = 0
        for task in tasks:
            if not task.is_completed and not task.title.startswith("[ASKIDA]"):
                task.title = f"[ASKIDA] {task.title}"
                count += 1
        await self.session.flush()
        return count
