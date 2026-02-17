from abc import ABC, abstractmethod
from datetime import datetime
import uuid
import json
from pathlib import Path

from src.event_bus.event_dispatcher import EventDispatcher


class BaseIngestor(ABC):
    def __init__(self, domain: str, source: str):
        self.domain = domain
        self.source = source
        self.run_id = str(uuid.uuid4())
        self.ingestion_timestamp = datetime.utcnow().isoformat()

    @abstractmethod
    def fetch(self):
        """
        Fetch raw data from an external source.
        Must be implemented by all concrete ingestors.
        """
        pass

    def write_raw(self, data, file_ext: str = "csv") -> Path:
        """
        Write raw data to the Bronze layer.
        Raw data is immutable and stored exactly as received.
        """
        date_str = datetime.utcnow().date().isoformat()
        base_path = Path("data") / "bronze" / self.domain / date_str
        base_path.mkdir(parents=True, exist_ok=True)

        file_path = base_path / f"raw_data.{file_ext}"

        if file_ext == "csv":
            data.to_csv(file_path, index=False)
        elif file_ext == "json":
            with open(file_path, "w") as f:
                json.dump(data, f)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

        return file_path

    def log_run(
        self,
        data_date: str,
        storage_path: Path,
        record_count: int,
        status: str,
        error_message: str = None,
    ):
        """
        Append a single ingestion record to the run log.
        Emit an event if ingestion succeeded.
        """
        log_entry = {
            "run_id": self.run_id,
            "domain": self.domain,
            "source": self.source,
            "data_date": data_date,
            "ingestion_timestamp": self.ingestion_timestamp,
            "storage_path": str(storage_path),
            "record_count": record_count,
            "status": status,
            "error_message": error_message,
        }

        log_file = Path("metadata") / "run_log.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        # Emit event only on successful ingestion
        if status == "SUCCESS":
            EventDispatcher.emit(
                event_type="DATA_INGESTED",
                payload={
                    "run_id": self.run_id,
                    "domain": self.domain,
                    "storage_path": str(storage_path),
                    "record_count": record_count,
                },
            )
