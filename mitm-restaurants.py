from mitmproxy import http
import json


def response(flow: http.HTTPFlow) -> None:
    with open("restaurants7.txt", "a") as ofile:
        if flow.request.pretty_url.startswith("https://api-prod-pvt.snackpass.co/api/v4/stores") and flow.request.pretty_url.endswith("products"):
            if flow.response.content:
                ofile.write(flow.request.pretty_url)
                resp = flow.response.content
                jsonResp = json.loads(resp)
                respFormatted = json.dumps(jsonResp, indent=4, separators=(". ", " = "))
                ofile.write(respFormatted)
                ofile.write('\n')

            # Add other separators etc. however you want

# def request(flow: http.HTTPFlow) -> None:
#     if flow.request.pretty_url.startswith("https://api/v4/stores/nearby?"):
#         flow.request.query["count"] = 10000
