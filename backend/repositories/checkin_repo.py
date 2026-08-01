"""
backend/repositories/checkin_repo.py
Check-in sessions and daily tasks persistence.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.db.models.checkin import CheckinSession, DailyTask
from backend.repositories.base import BaseRepository


def day_for(d: date | None = None) -> date:
    """Return the calendar day used as the check-in key (today by default)."""
    return d or date.today()


# Backwards-compatible alias
week_start_for = day_for


class CheckinRepository(BaseRepository[CheckinSession]):
    model = CheckinSession

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_current(
        self, *, tenant_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[CheckinSession]:
        today = day_for()
        stmt = (
            select(CheckinSession)
            .options(selectinload(CheckinSession.daily_tasks))
            .where(
                CheckinSession.tenant_id == tenant_id,
                CheckinSession.user_id == user_id,
                CheckinSession.checkin_date == today,
            )
            .order_by(CheckinSession.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_with_tasks(self, session_id: uuid.UUID) -> Optional[CheckinSession]:
        stmt = (
            select(CheckinSession)
            .options(selectinload(CheckinSession.daily_tasks))
            .where(CheckinSession.id == session_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_session(
        self,
        *,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        checkin_date: date | None = None,
    ) -> CheckinSession:
        row = CheckinSession(
            tenant_id=tenant_id,
            user_id=user_id,
            checkin_date=day_for(checkin_date),
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
            .order_by(CheckinSession.checkin_date.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [s.summary for s in result.scalars().all() if s.summary]

    async def list_history(
        self,
        *,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        limit: int = 30,
    ) -> list[CheckinSession]:
        stmt = (
            select(CheckinSession)
            .options(selectinload(CheckinSession.daily_tasks))
            .where(
                CheckinSession.tenant_id == tenant_id,
                CheckinSession.user_id == user_id,
            )
            .order_by(CheckinSession.checkin_date.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def set_mood(
        self, session: CheckinSession, mood_score: int
    ) -> CheckinSession:
        session.mood_score = mood_score
        session.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return session

    async def update_signals(
        self,
        session: CheckinSession,
        *,
        energy_level: int | None = None,
        motivation_level: int | None = None,
        workload_level: str | None = None,
        main_blocker: str | None = None,
        stage: str | None = None,
        turn_count: int | None = None,
    ) -> CheckinSession:
        """Persist structured check-in signals / stage (only non-null updates)."""
        if energy_level is not None:
            session.energy_level = energy_level
        if motivation_level is not None:
            session.motivation_level = motivation_level
        if workload_level is not None:
            session.workload_level = workload_level
        if main_blocker is not None:
            session.main_blocker = main_blocker
        if stage is not None:
            session.stage = stage
        if turn_count is not None:
            session.turn_count = turn_count
        session.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return session

    async def avg_signals_last_days(
        self,
        *,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        window_days: int = 7,
    ) -> dict[str, Any]:
        """
        Average energy/motivation over sessions in the last `window_days`
        that have at least one signal set. Returns counts for XAI.
        """
        from datetime import timedelta

        today = day_for()
        start = today - timedelta(days=window_days - 1)
        stmt = (
            select(CheckinSession)
            .where(
                CheckinSession.tenant_id == tenant_id,
                CheckinSession.user_id == user_id,
                CheckinSession.checkin_date >= start,
                CheckinSession.checkin_date <= today,
            )
        )
        result = await self.session.execute(stmt)
        sessions = list(result.scalars().all())

        energies = [
            s.energy_level
            for s in sessions
            if getattr(s, "energy_level", None) is not None
        ]
        motivations = [
            s.motivation_level
            for s in sessions
            if getattr(s, "motivation_level", None) is not None
        ]
        return {
            "energy_avg": round(sum(energies) / len(energies), 2) if energies else None,
            "motivation_avg": (
                round(sum(motivations) / len(motivations), 2) if motivations else None
            ),
            "signal_days": max(len(energies), len(motivations)),
            "sessions_in_window": len(sessions),
        }

    async def count_for_user(
        self, *, tenant_id: uuid.UUID, user_id: uuid.UUID
    ) -> int:
        from sqlalchemy import func

        stmt = select(func.count()).select_from(CheckinSession).where(
            CheckinSession.tenant_id == tenant_id,
            CheckinSession.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def count_missed_days(
        self,
        *,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        window_days: int = 7,
    ) -> int:
        """How many of the last `window_days` calendar days lack a check-in."""
        from datetime import timedelta

        today = day_for()
        start = today - timedelta(days=window_days - 1)
        stmt = (
            select(CheckinSession.checkin_date)
            .where(
                CheckinSession.tenant_id == tenant_id,
                CheckinSession.user_id == user_id,
                CheckinSession.checkin_date >= start,
                CheckinSession.checkin_date <= today,
            )
        )
        result = await self.session.execute(stmt)
        present = {row[0] for row in result.all()}
        return window_days - len(present)


class DailyTaskRepository(BaseRepository[DailyTask]):
    model = DailyTask

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def replace_tasks(
        self,
        *,
        checkin_session_id: uuid.UUID,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        titles: list[str],
    ) -> list[DailyTask]:
        existing = await self.session.execute(
            select(DailyTask).where(
                DailyTask.checkin_session_id == checkin_session_id
            )
        )
        for row in existing.scalars().all():
            await self.session.delete(row)

        created: list[DailyTask] = []
        for title in titles[:3]:
            task = DailyTask(
                checkin_session_id=checkin_session_id,
                tenant_id=tenant_id,
                user_id=user_id,
                title=title.strip(),
                is_completed=False,
                due_date=day_for(),
            )
            self.session.add(task)
            created.append(task)
        await self.session.flush()
        return created

    async def list_for_user(
        self, *, tenant_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[DailyTask]:
        stmt = (
            select(DailyTask)
            .options(selectinload(DailyTask.checkin_session))
            .where(
                DailyTask.tenant_id == tenant_id,
                DailyTask.user_id == user_id,
            )
            .order_by(DailyTask.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_for_users(
        self, *, tenant_id: uuid.UUID, user_ids: list[uuid.UUID]
    ) -> list[DailyTask]:
        if not user_ids:
            return []
        stmt = (
            select(DailyTask)
            .where(
                DailyTask.tenant_id == tenant_id,
                DailyTask.user_id.in_(user_ids),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def set_completed(
        self, task: DailyTask, completed: bool
    ) -> DailyTask:
        task.is_completed = completed
        task.completed_at = datetime.now(timezone.utc) if completed else None
        await self.session.flush()
        return task

    async def suspend_incomplete(
        self, *, tenant_id: uuid.UUID, user_id: uuid.UUID
    ) -> int:
        """Downscale: mark incomplete open tasks as suspended (AC3)."""
        tasks = await self.list_for_user(tenant_id=tenant_id, user_id=user_id)
        count = 0
        for task in tasks:
            if not task.is_completed and getattr(task, "status", "active") != "suspended":
                if task.title.startswith("[ASKIDA] "):
                    task.title = task.title[len("[ASKIDA] ") :]
                task.status = "suspended"
                count += 1
        await self.session.flush()
        return count


# Backwards-compatible alias
WeeklyTaskRepository = DailyTaskRepository
