import requests as r
import base64
import re

# caution ! the access_token is outdated

appid = '17009796'
apikey = 'A49w3L72Di0S8Cg9PZkXFOK4'
secret_key = 'zMjA4rctVM0I9bHMFGa2FRY86s2wS69m'
access_token = '24.c26d50139fb633e963bb0455698d2801.2592000.1572183791.282335-17009796'

# outdated on 2019/9/12
url = 'https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic'
url1 = 'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic'
# feifei
url2 = 'http://pred.fateadm.com/api/capreg'
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'user_id': '116095'

}
# NOT ENDED but the Baidu recognition is too weak.

def get_captcha(image_src, use_accurate):
    if not re.search('/', image_src):
        # this is the default path of image if no path and only name is defined
        image_src = '/Users/yang_sijie/downloads/'+image_src
    if use_accurate:
        u = url
    else:
        u = url1
    with open(image_src, 'rb') as f:
        image = base64.b64encode(f.read())
        data = {
            'image': image
        }
    ret = r.post(url=u+'?access_token='+access_token, headers=headers, data=data)
    match = re.match('.*"words": "(.*)".*', ret.text)
    try:
        return match.group(1)
    except AttributeError:
        return "failed recognition (mostly due to file attribute)"


print(get_captcha("/Users/yang_sijie/Downloads/Num0.jpg", False))

"""
Result of Testing(Baidu):
general_basic: 1/6   number 1 cannot be recognized
accurate_basic: 1/6
"""
