"""Scheduler Task that will fire the LWT."""

import datetime
import time

from apscheduler.schedulers.background import BackgroundScheduler

from backend.still_here.bootstrap import get_device_repository
from backend.still_here.core.service.unit_of_work import InMemoryDeviceUnitOfWork
from backend.still_here.settings import get_logger

logger = get_logger()


class FirePoller:
    """Polls the in-memory device repository for scheduled LWT events.

    Tracks the last poll time and provides the `check_and_fire` method to trigger events for devices whose `fire_at`
    has elapsed.
    """

    def __init__(self, interval_sec: int = 10):
        """Initialize the FirePoller.

        Args:
            interval_sec (int): Polling interval in seconds. Defaults to 10.
        """
        self._last_poll = int(time.time())
        self.interval_sec = interval_sec

    def check_and_fire(self):
        """Poll devices scheduled to fire between the last and current timestamp.

        This method checks the in-memory repository for devices whose `fire_at` timestamps fall within the interval
        since the last polling cycle. If found, their last will events are triggered via the message bus.

        Updates the internal `_last_poll` timestamp after each run.
        """
        now = int(time.time())
        start_time = self._last_poll + 1
        end_time = now

        uow = InMemoryDeviceUnitOfWork(repository=get_device_repository())
        logger.debug(f"Polling for devices scheduled between {start_time} and {end_time} (UTC seconds)")

        with uow:
            devices = uow.devices.get_fire_at_between(start_time, end_time)
            for device in devices:
                fire_at_iso = datetime.datetime.fromtimestamp(device.fire_at, datetime.UTC).isoformat()
                now_iso = datetime.datetime.fromtimestamp(device.fire_at, datetime.UTC).isoformat()
                logger.info(
                    f"[LWT Triggered] Device UUID: {device.uuid} | "
                    f"Scheduled fire_at: {fire_at_iso} | "
                    f"Triggered at: {now_iso} | "
                    f"Last will: {device.last_will}",
                )

        self._last_poll = now


def start():
    """Start the background scheduler for polling LWT devices.

    This function initializes and starts an APScheduler `BackgroundScheduler` that runs the `check_and_fire` task at a
    fixed interval (every 10 seconds).

    The scheduler is non-blocking and runs in the background thread.

    Note:
        Make sure this is called once during application startup to avoid multiple schedulers running concurrently.
    """
    poller = FirePoller()
    scheduler = BackgroundScheduler()
    scheduler.add_job(poller.check_and_fire, "interval", seconds=poller.interval_sec)
    scheduler.start()
