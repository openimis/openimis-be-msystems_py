import re
from datetime import datetime as py_datetime

from core import datetime

class SoapDatetime(datetime.datetime):
    def isoformat(self):
        return re.sub(r"[+-]00:?00$", "Z", self.strftime("%Y-%m-%dT%H:%M:%S%z"))

    @classmethod
    def from_ad_date(cls, value):
        if value is None:
            return None
        return SoapDatetime(value.year, value.month, value.day, 0, 0, 0, 0, py_datetime.now().astimezone().tzinfo)

    @classmethod
    def from_ad_datetime(cls, value):
        if value is None:
            return None
        return SoapDatetime(value.year, value.month, value.day,
                          value.hour, value.minute, value.second, value.microsecond,
                          value.tzinfo or py_datetime.now().astimezone().tzinfo)