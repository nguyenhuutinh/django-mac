
import json
import io
import logging
from lxml import html
import requests
# from common.models import GoogleFormField

# from common.models import GoogleFormInfo

# def getFormResponse(campaign, url):
#     r = requests.get(url, allow_redirects=True)
#     if r.is_redirect:
#         print("is_redirect", r.headers["Location"])
#         r = requests.get(r.headers["Location"], allow_redirects=True)
#     # print("r", r.status_code)
#     if r.ok:
#         # print(r.content)
#         return get_file_size(campaign, url, r.content)
#     else:  # In case auto download is enable in account setting
#         return False
# def get_file_size(campaign, url, content):
#         # print("listData")
#         tree = html.fromstring(content)
#         # print(tree)
#         listData = tree.xpath('//*[@role="listitem"]/div/@data-params')
#         fields = []

#         partialResponse = tree.xpath('//input[contains(@name, "partialResponse")]/@value')[0]
#         pageHistory = tree.xpath('//input[contains(@name, "pageHistory")]/@value')[0]
#         fvv = tree.xpath('//input[contains(@name, "fvv")]/@value')[0]
#         fbzx = tree.xpath('//input[contains(@name, "fbzx")]/@value')[0]
#         actionLink = tree.xpath('//form/@action')[0]
#         # print(actionLink)
#         form = GoogleFormInfo.objects.create(link= url, num_fields= len(listData), campaign= campaign, partial_response =  partialResponse, action_link = actionLink, fbzx = fbzx, fvv= fvv, page_history= pageHistory)
#         index = 1
#         campaign.google_form_id = form.id
#         campaign.save()
#         for result in listData:
#             data = result.split(",")
#             # print(data)

#             for check in data :
#                 # print(check)
#                 if check.startswith("[["):
#                     field = check.replace("[[", "").replace("]]","")
#                     GoogleFormField.objects.create(key_name= f"entry.{field}", key_index =  index, google_form= form, campaign= campaign)
#                     fields.append(field)
#                     index = index + 1
#                     # print(index)
#                     break


#         return True
        # print(len(listData))
        # print(listData[1])
