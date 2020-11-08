from mitmproxy import http
import json


def response(flow: http.HTTPFlow) -> None:
    with open("all_19th.txt", "a") as ofile:
        if flow.request.pretty_url.startswith("https://api-prod-pvt.snackpass.co/api/v4/gifts?friendsOnly=false"):
            ofile.write(flow.request.pretty_url)
            
            if flow.response.content:
                resp = flow.response.content
                jsonResp = json.loads(resp)
                respFormatted = json.dumps(jsonResp, indent=4, separators=(". ", " = "))
                ofile.write(respFormatted)

            # Add other separators etc. however you want

# def request(flow: http.HTTPFlow) -> None:
#     if flow.request.pretty_url.startswith("https://api-prod-pvt.snackpass.co/api/v4/gifts?friendsOnly=false"):
#         flow.request.query["count"] = 100000


# def request(flow: http.HTTPFlow) -> None:
#     if flow.request.pretty_url.startswith("https://api-prod-pvt.snackpass.co/api/v4/gifts?friendsOnly=false") and "before" in flow.request.pretty_url:
#         flow.request.query["count"] = 100000
#         flow.request.query["before"] = "2017-06-04T19:30:02.279Z"