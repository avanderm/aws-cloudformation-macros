"""
Custom JSON logger for CloudWatch.
"""
import decimal
import json
import logging
import os
from six import string_types


def json_formatter(obj):
    """
    Geocoder exceptions get JSON formatted.
    """
    if isinstance(obj, decimal.Decimal):
        if abs(obj) % 1 > 0:
            return float(obj)
        else:
            return int(obj)
    else:
        return str(obj)


class JsonFormatter(logging.Formatter):
    """
    Logger formatter to format logs in JSON format.
    """
    def __init__(self, **kwargs):
        super(JsonFormatter, self).__init__()
        self.format_dict = {
            'timestamp': '%(asctime)s',
            'level': '%(levelname)s',
            'name': '%(name)s'
        }
        self.format_dict.update(kwargs)
        self.default_json_formatter = kwargs.pop('json_default', json_formatter)

    def format(self, record):
        record_dict = record.__dict__.copy()
        record_dict['asctime'] = self.formatTime(record)

        # fill in values
        log_dict = {
            k: v % record_dict
            for k, v in self.format_dict.items()
            if v
        }

        if isinstance(record_dict['msg'], dict):
            log_dict['message'] = record_dict['msg']
        else:
            if isinstance(record_dict['msg'], string_types):
                # json string
                log_dict['message'] = record.getMessage()
            else:
                # serialize object
                log_dict['message'] = json.dumps(
                    record_dict['msg'],
                    default=self.default_json_formatter
                )

            try:
                log_dict['message'] = json.loads(
                    log_dict['message']
                )
            except (TypeError, ValueError):
                pass

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            log_dict['exception'] = record.exc_text

        json_record = json.dumps(log_dict, default=self.default_json_formatter)

        if hasattr(json_record, 'decode'):
            json_record = json_record.decode('utf-8')

        return json_record


# Logging (CloudWatch)
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
for handler in logging.root.handlers:
    handler.setFormatter(JsonFormatter())

if not os.getenv('ENVIRONMENT'):
    # avoid double logging when testing locally
    HANDLER = logging.StreamHandler()
    HANDLER.setFormatter(JsonFormatter())
    LOGGER.addHandler(HANDLER)
    LOGGER.setLevel(logging.DEBUG)


def log_message(level, message, *args):
    LOGGER.log(level, message, *args)

def log_exception(exception):
    LOGGER.exception(exception)
