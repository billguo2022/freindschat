from typing import Union

ERROR = 0
SUCCESS = 200
StatusUnauthorized = 401
StatusMethodNotAllowed = 405
LOCATION = 201


def result(code: int, msg: str, data: Union[object, None] = None) -> dict:
    return {
        "code": code,
        "msg": msg,
        "data": data
    }


def ok():
    return result(SUCCESS, "success")


def okWithMessage(msg: str):
    return result(SUCCESS, msg)


def okWithData(data: Union[object, None] = None):
    return result(SUCCESS, "success", data)


def okWithDetailed(msg: str, data: Union[object, None] = None):
    return result(SUCCESS, msg, data)


def fail():
    return result(ERROR, "error")


def failLocation():
    return result(LOCATION, "Couldn't get your location")


def failWithMessage(msg: str):
    return result(ERROR, msg)


def failWithDetailed(msg: str, data: Union[object, None] = None):
    return result(ERROR, msg, data)


def failTokenWithDetail(msg: str, data: Union[object, None] = None):
    return result(StatusUnauthorized, msg, data)


def failAuthApiWithDetail(msg: str, data: Union[object, None] = None):
    return result(StatusMethodNotAllowed, msg, data)
