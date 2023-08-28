from ..crud.base import CRUDBase
from ..models.request_log import RequestLog
from ..schemas.request_log import RequestLogCreate, RequestLogUpdate


class CRUDRequestLog(CRUDBase[RequestLog, RequestLogCreate, RequestLogUpdate]):
    pass


request_log = CRUDRequestLog(RequestLog)
