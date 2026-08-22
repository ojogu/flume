import hashlib
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.analytics import PageView
from src.model.job import Job
from src.utils.log import get_logger
from src.utils.redis import get_redis

logger = get_logger(__name__)

VISITOR_HASH_SALT = "flume-pageview-salt"
PAGEVIEW_DEDUPE_TTL = 300  # 5 minutes


class PageViewService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _visitor_hash(ip: str, user_agent: str) -> str:
        """SHA-256(IP + user_agent + salt) for pseudonymous tracking."""
        raw = f"{ip}:{user_agent}:{VISITOR_HASH_SALT}"
        return hashlib.sha256(raw.encode()).hexdigest()

    async def record_visit(
        self,
        path: str,
        ip: str,
        user_agent: str | None = None,
        referrer: str | None = None,
    ) -> bool:
        """Record a page view, deduplicated by (visitor_hash, path) within 5 minutes.

        Returns True if the visit was recorded, False if deduplicated.
        """
        visitor_hash = self._visitor_hash(ip, user_agent or "")
        dedup_key = f"pv:{visitor_hash}:{path}"

        try:
            redis = await get_redis()
            exists = await redis.exists(dedup_key)
            if exists:
                return False
            await redis.set(dedup_key, "1", ex=PAGEVIEW_DEDUPE_TTL)
        except Exception as e:
            logger.warning(f"Redis dedupe failed, recording anyway: {e}")

        page_view = PageView(
            path=path,
            visitor_hash=visitor_hash,
            referrer=referrer,
            user_agent=user_agent,
        )
        self.db.add(page_view)
        try:
            await self.db.flush()
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error recording page view: {e}")
            return False

    async def get_stats(self, days: int = 30) -> dict:
        """Return aggregated stats for the admin dashboard."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        # Total page views in period
        total_views = await self.db.scalar(
            select(func.count(PageView.id)).where(PageView.created_at >= cutoff)
        )

        # Unique visitors in period
        unique_visitors = await self.db.scalar(
            select(func.count(func.distinct(PageView.visitor_hash))).where(
                PageView.created_at >= cutoff
            )
        )

        # Top paths
        top_paths_result = await self.db.execute(
            select(PageView.path, func.count(PageView.id).label("views"))
            .where(PageView.created_at >= cutoff)
            .group_by(PageView.path)
            .order_by(text("views DESC"))
            .limit(10)
        )
        top_paths = [{"path": row[0], "views": row[1]} for row in top_paths_result.all()]

        # Top referrers (excluding null)
        top_referrers_result = await self.db.execute(
            select(PageView.referrer, func.count(PageView.id).label("views"))
            .where(PageView.created_at >= cutoff, PageView.referrer.isnot(None))
            .group_by(PageView.referrer)
            .order_by(text("views DESC"))
            .limit(10)
        )
        top_referrers = [
            {"referrer": row[0], "views": row[1]} for row in top_referrers_result.all()
        ]

        # Job origin breakdown
        job_origin_result = await self.db.execute(
            select(Job.origin, func.count(Job.id))
            .where(Job.created_at >= cutoff)
            .group_by(Job.origin)
        )
        jobs_by_origin = {row[0]: row[1] for row in job_origin_result.all()}

        # Job status breakdown
        job_status_result = await self.db.execute(
            select(Job.status, func.count(Job.id))
            .where(Job.created_at >= cutoff)
            .group_by(Job.status)
        )
        jobs_by_status = {row[0]: row[1] for row in job_status_result.all()}

        # Total jobs in period
        total_jobs = sum(jobs_by_status.values())

        return {
            "period_days": days,
            "page_views": {
                "total": total_views or 0,
                "unique_visitors": unique_visitors or 0,
                "top_paths": top_paths,
                "top_referrers": top_referrers,
            },
            "jobs": {
                "total": total_jobs,
                "by_origin": jobs_by_origin,
                "by_status": jobs_by_status,
            },
        }
