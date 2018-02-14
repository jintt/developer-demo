import hashlib
import urllib
from cgi import FieldStorage

url_params = ""
def concat_params(params):
    pairs = []
    for key in sorted(params):
        if key == 'sig':
            continue
        val = params[key]
        if isinstance(val, unicode):
            val = urllib.quote_plus(val.encode('utf-8'))
        elif isinstance(val, str):
            val = urllib.quote_plus(val)
        if not isinstance(val, FieldStorage):
            pairs.append("{}={}".format(key, val))
        #print pairs
    return '&'.join(pairs)


def gen_sig(path_url, params, consumer_secret):
    params = concat_params(params)
    #print params
    to_hash = u'{}?{}{}'.format(
        path_url, params, consumer_secret
    ).encode('utf-8').encode('hex')

    sig = hashlib.new('sha1', to_hash).hexdigest()
    sig = path_url + "?" + params + "&sig=" + sig
    print sig
    return sig

def get_url(path_url, params, consumer_secret):
    sig = gen_sig(path_url, params, consumer_secret)
