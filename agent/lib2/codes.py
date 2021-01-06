class ResponseMessage:
    """
    http返回状态码
    错误代码: code
    801      参数错误
    805      数据格式错误
    810      数据已经存在
    820      数据不存在
    204      操作失败
    200      操作成功
    """
    ArgsError = 801
    DataError = 805
    DataExistsError = 810
    Success = 200
    Failed = 204
    DataNoExistsError = 820


class LogCode:
    """
    日志库操作类型
    0     登陆
    1     域名
    2     解析
    3     用户
    """
    Login = 0
    Domain = 1
    Resolve = 2
    User = 3
