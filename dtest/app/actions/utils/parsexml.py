#!/usr/bin/python
# -*- coding: UTF-8 -*-

from xml.dom.minidom import parse
from xml.dom import Node
import xml.dom.minidom
import os

apisdic = {}
def loadxml():
    # 使用minidom解析器打开 XML 文档
    path = os.path.dirname(os.path.abspath("paramlist.xml"))
    DOMTree = xml.dom.minidom.parse(path + "/app/docs/paramlist.xml")
    root = DOMTree.documentElement

    apis = root.getElementsByTagName("api")
    paramdic = {}
    for api in apis:
        paramlist = []

        params = api.getElementsByTagName("param")
        for param in params:
            paramdic.clear()

            child = param.getElementsByTagName("paramname")[0]
            paramdic["paramname"] = child.childNodes[0].data

            child = param.getElementsByTagName("defaultvalue")[0]
            if len(child.childNodes) > 0:
                paramdic["defaultvalue"] = child.childNodes[0].data

            paramlist.append(paramdic.copy())
        apisdic[api.getAttribute("name")] = paramlist
    print apisdic[api.getAttribute("name")]


def getapiparams(apiname):
    loadxml()
    return apisdic[apiname]



if __name__=='__main__':
    apiparams = getapiparams("opensite_launch")
