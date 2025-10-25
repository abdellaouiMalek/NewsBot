from fastapi import APIRouter

from app.core.scheduler import scheduler

router = APIRouter()


@router.get("/jobs")
async def list_jobs():
    jobs_info = []
    for job in scheduler.get_jobs():
        jobs_info.append(
            {
                "id": job.id,
                "next_run": job.next_run_time,
                "trigger": str(job.trigger),
            }
        )
    return jobs_info
