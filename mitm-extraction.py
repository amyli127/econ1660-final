from mitmproxy import http

def response(flow: http.HTTPFlow) -> None:
    elif flow.request.path.endswith("/brew"):
        
