# src/geosnap/batch_processor.py
"""Batch processing queue for multiple folder jobs."""

import logging
from dataclasses import dataclass, field
from typing import List, Callable, Optional
from threading import Event

from .main import process_photos_backend
from .exceptions import GeoSnapError

logger = logging.getLogger(__name__)


@dataclass
class BatchJob:
    """Represents a single processing job in the queue."""

    input_path: str
    output_path: str
    project_name: str
    include_no_gps: bool = False
    status: str = "pending"  # pending, running, completed, failed, cancelled
    error_message: str = ""


@dataclass
class BatchResult:
    """Result of batch processing."""

    total_jobs: int
    completed: int
    failed: int
    cancelled: int
    details: List[str] = field(default_factory=list)


class BatchProcessor:
    """Manages a queue of processing jobs."""

    def __init__(self):
        self.queue: List[BatchJob] = []
        self._stop_event: Optional[Event] = None

    def add_job(self, input_path: str, output_path: str, project_name: str, include_no_gps: bool = False) -> int:
        """Add a job to the queue. Returns job index."""
        job = BatchJob(
            input_path=input_path, output_path=output_path, project_name=project_name, include_no_gps=include_no_gps
        )
        self.queue.append(job)
        return len(self.queue) - 1

    def remove_job(self, index: int) -> bool:
        """Remove a pending job from the queue."""
        if 0 <= index < len(self.queue) and self.queue[index].status == "pending":
            self.queue.pop(index)
            return True
        return False

    def clear_queue(self) -> None:
        """Clear all pending jobs."""
        self.queue = [job for job in self.queue if job.status != "pending"]

    def get_pending_count(self) -> int:
        """Get number of pending jobs."""
        return sum(1 for job in self.queue if job.status == "pending")

    def process_all(
        self, progress_callback: Optional[Callable[[int, int, str], None]] = None, stop_event: Optional[Event] = None
    ) -> BatchResult:
        """
        Process all pending jobs in the queue.

        Args:
            progress_callback: Callback(current_job, total_jobs, message)
            stop_event: Event to signal cancellation

        Returns:
            BatchResult with processing summary
        """
        self._stop_event = stop_event
        pending_jobs = [job for job in self.queue if job.status == "pending"]
        total = len(pending_jobs)
        completed = 0
        failed = 0
        cancelled = 0
        details = []

        for i, job in enumerate(pending_jobs):
            # Check for cancellation
            if stop_event and stop_event.is_set():
                job.status = "cancelled"
                cancelled += 1
                details.append(f"❌ Cancelado: {job.project_name}")
                continue

            # Update progress
            job.status = "running"
            if progress_callback:
                progress_callback(i + 1, total, f"Procesando: {job.project_name}")

            try:
                # Process this job
                result_msg = process_photos_backend(
                    input_path_str=job.input_path,
                    output_path_str=job.output_path,
                    project_name_str=job.project_name,
                    progress_callback=None,  # Use batch-level progress
                    stop_event=stop_event,
                    include_no_gps=job.include_no_gps,
                )
                job.status = "completed"
                completed += 1
                details.append(f"✅ {job.project_name}: {result_msg}")
                logger.info(f"Batch job completed: {job.project_name}")

            except GeoSnapError as e:
                job.status = "failed"
                job.error_message = str(e)
                failed += 1
                details.append(f"⚠️ {job.project_name}: {e}")
                logger.warning(f"Batch job failed: {job.project_name} - {e}")

            except Exception as e:
                job.status = "failed"
                job.error_message = str(e)
                failed += 1
                details.append(f"❌ {job.project_name}: Error - {e}")
                logger.error(f"Batch job error: {job.project_name} - {e}")

        # Mark remaining as cancelled if stopped
        if stop_event and stop_event.is_set():
            for job in pending_jobs:
                if job.status == "pending":
                    job.status = "cancelled"
                    cancelled += 1

        return BatchResult(total_jobs=total, completed=completed, failed=failed, cancelled=cancelled, details=details)

    def get_summary(self) -> str:
        """Get a summary of the current queue state."""
        pending = sum(1 for j in self.queue if j.status == "pending")
        running = sum(1 for j in self.queue if j.status == "running")
        completed = sum(1 for j in self.queue if j.status == "completed")
        failed = sum(1 for j in self.queue if j.status == "failed")

        return f"Cola: {pending} pendientes, {running} en proceso, {completed} completados, {failed} fallidos"
