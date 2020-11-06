from mitmproxy import http
import json


def response(flow: http.HTTPFlow) -> None:
    with open("friend-gifts.txt", "a") as ofile:
        # if not flow.request.pretty_url.startswith("https://api-prod-pvt.snackpass.co/api/v4/gifts?friendsOnly=true"):
        #     return
        ofile.write(flow.request.pretty_url)
        
        if flow.response.content:
            # resp = str(flow.response.content)
            resp = flow.response.content
            jsonResp = json.loads(resp)
            respFormatted = json.dumps(jsonResp, indent=4, separators=(". ", " = "))
            ofile.write(respFormatted)

        # Add other separators etc. however you want
        ofile.write("-------")

# def request(flow: http.HTTPFlow) -> None:
#     if flow.request.pretty_url.startswith("https://api-prod-pvt.snackpass.co/api/v4/gifts?friendsOnly=true"):
#         flow.request.query["count"] = "1"
