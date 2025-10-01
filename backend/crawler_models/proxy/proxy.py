from mitmproxy import http, ctx
from urllib.parse import parse_qs, urlsplit, SplitResult, urljoin


# 为selenium配置中间代理。方便selenium进行流量拦截和修改
class Proxy(object):
    def __init__(self,
                 url: str,  # 驱动浏览器访问的原始地址
                 ):
        self._url: str = url
        # 对完整的url地址进行解析，提取各个组件
        self._split_url: SplitResult = urlsplit(self._url)
        self._scheme = self._split_url.scheme  # 方案
        self._netloc = self._split_url.netloc  # 权威
        self._username = self._split_url.username  # 用户名
        self._password = self._split_url.password  # 用户密码
        self._hostname = self._split_url.hostname  # 域名或者IP
        self._port = self._split_url.port  # 端口号
        self._path = self._split_url.path  # 路径
        self._query = parse_qs(self._split_url.query)  # 查询(字典，值为列表，一个键可以对应多个参数)
        self._fragment = self._split_url.fragment  # 碎片（锚点）

    def request(self, flow: http.HTTPFlow) -> None:
        if self._hostname in flow.request.host:
            pass

    def response(self, flow: http.HTTPFlow) -> None:
        # 创建一个变量来储存最终的目标域名
        target_hostname = ''
        # 创建空列表来储存重定向跳转链
        location_charin = []

        # 请求成功，完成指定操作或者返回响应
        if 200<= flow.response.status_code < 300:
            # 最后一次请求成功，返回请求所用域名，该域名即为重定向的目标域名
            target_hostname = flow.request.pretty_host

        # 请求成功，被重定向
        if 300 <= flow.response.status_code < 400:
            if flow.request.headers.get('Sec-Fetch-Dest') == 'document':
                loc = flow.response.headers.get('Location', '')
                if loc:
                    location_node = urljoin(
                        flow.request.pretty_url,
                        loc,
                    )
                    location_charin.append(location_node)
            else:
                pass

        # 客户端异常
        if 400 <= flow.response.status_code < 500:
            pass

        # 服务器异常
        if 500 <= flow.response.status_code < 600:
            pass


__all__ = [
    "Proxy",
]
