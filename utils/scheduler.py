from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

_scheduler = None

def get_scheduler():
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
        _scheduler.start()
        atexit.register(lambda: _scheduler.shutdown())
    return _scheduler

def schedule_every(func, hours: int):
    sched = get_scheduler()
    sched.add_job(func, IntervalTrigger(hours=hours), id="trend_job", replace_existing=True)
