
import signature
from openapi import globalsetting

def get_request_url(url, params):

    request_url = signature.gen_sig(url, params, globalsetting.consumer_scret)
    print request_url
    return request_url