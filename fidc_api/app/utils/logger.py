import logging
import sys
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "time": self.formatTime(record, self.datefmt),
            "name": record.name,
            "message": record.getMessage(),
        }
        # Adiciona job_id ou operation_id se estiverem presentes no extra
        if hasattr(record, "job_id"):
            log_record["job_id"] = record.job_id
        if hasattr(record, "operation_id"):
            log_record["operation_id"] = record.operation_id
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger