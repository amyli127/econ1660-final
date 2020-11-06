from mitmproxy import http
import json

count = 0

def response(flow: http.HTTPFlow) -> None:
    with open("friend-gifts.txt", "a") as ofile:
        ofile.write(flow.request.pretty_url)

        # if flow.request.content:
        #     ofile.write(flow.request.content)

        if flow.response.content:
            # resp = str(flow.response.content)
            resp = flow.response.content
            jsonResp = json.loads(resp)
            respFormatted = json.dumps(jsonResp, indent=4, separators=(". ", " = "))
            ofile.write(respFormatted)

        # Add other separators etc. however you want
        ofile.write("-------")
