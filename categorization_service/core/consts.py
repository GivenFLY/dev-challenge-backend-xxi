import logging


class RequestStatuses:
    Pending = "pending"
    Processing = "processing"
    Done = "done"
    Failed = "failed"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("arq.worker")
