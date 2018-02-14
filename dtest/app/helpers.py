#!/usr/bin/env python
# -*- coding: utf-8 -*-


class DotDict(dict):
    """
    d = dotdict({'a': 'spam', 'b': 'ham'})
    print d['a']
    >   spam
    print d.b
    >   ham
    d.c = 'python!'
    print d.c
    >   python!
    '''
    """
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__
    __delattr__ = dict.__delitem__
