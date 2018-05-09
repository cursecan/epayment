import requests
import json
import re

def news(bot, base_url, v):
    url = base_url+'api/manager/user/'
    r = requests.get(url, headers={'Content-Type':'application/json'})
    rson = r.json()
    msg = '*~Bot Information~*\n'

    for t in rson['results'] :
        telid = t['telegram']
        try :
            bot.sendMessage(telid, msg+v, parse_mode='Markdown')
        except:
            pass