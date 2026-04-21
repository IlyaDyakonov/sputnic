from src.infrastructure.tasks.celery_app import celery_app
from src.infrastructure.tasks.workers import extract_file_metadata, scan_file_for_threats, send_file_alert

# Backward-compatible entrypoint for `celery -A src.tasks.celery_app`.
