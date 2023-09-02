from ..crud.base import CRUDBase
from ..schemas.request_log import RequestLogCreate, RequestLogUpdate
from ..models.request_log import RequestLog


class CRUDRequestLog(CRUDBase[RequestLog, RequestLogCreate, RequestLogUpdate]):
    pass


request_log = CRUDRequestLog(RequestLog)
