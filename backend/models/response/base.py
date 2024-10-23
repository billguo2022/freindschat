import datetime

import pytz


class BaseInfo:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.created_at = self.changeDatetime(kwargs.get("created_at", None))
        self.updated_at = self.changeDatetime(kwargs.get("updated_at", None))
        self.deleted_at = kwargs.get("deleted_at", None)

    @staticmethod
    def changeDatetime(time: str):
        print("time===========", time)
        if time is None:
            return ""
        time_obj = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        utc_time = pytz.utc.localize(time_obj)
        # 将UTC时间转换为美国加州太平洋时区的时间
        pacific = pytz.timezone('America/Los_Angeles')
        pacific_time = utc_time.astimezone(pacific)
        return pacific_time.strftime('%Y-%m-%d %H:%M:%S')
