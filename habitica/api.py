#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Phil Adams http://philadams.net

Python wrapper around the Habitica (http://habitica.com) API
http://github.com/philadams/habitica
"""


import json
from typing import Tuple, Dict

import requests

API_URI_BASE = 'api/v3'
API_CONTENT_TYPE = 'application/json'


class Habitica(object):
    """
    A minimalist Habitica API class.
    """

    def __init__(self, auth:Dict=None, resource:str=None, aspect:str=None) -> None:
        self.auth = auth
        self.resource = resource
        self.aspect = aspect
        self.headers = auth if auth else {}  # type: Dict
        self.headers.update({'content-type': API_CONTENT_TYPE})

    def __getattr__(self, m: str) -> 'Habitica':
        try:
            return object.__getattr__(self, m)  # type: ignore
        except AttributeError:
            if not self.resource:
                return Habitica(auth=self.auth, resource=m)
            else:
                return Habitica(auth=self.auth, resource=self.resource,
                                aspect=m)

    def _build_uri(self, **kwargs) -> Tuple[str, Dict]:
        # build up URL... Habitica's api is the *teeniest* bit annoying
        # so either i need to find a cleaner way here, or i should
        # get involved in the API itself and... help it.
        aspect_id = kwargs.pop('_id', None)
        direction = kwargs.pop('_direction', None)
        uri = '%s/%s' % (self.auth['url'], API_URI_BASE)
        if self.aspect:
            if aspect_id is not None:
                uri_template = "{0}/{self.aspect}/{aspect_id}"
            elif self.aspect == 'tasks':
                uri_template = "{0}/{self.aspect}/{self.resource}"
            else:
                uri_template = "{0}/{self.resource}/{self.aspect}"
            if direction is not None:
                uri_template += "/score/{direction}"
        else:
            uri_template = '{0}/{self.resource}'
        # for strange urls
        _uri_template = kwargs.pop('_uri_template', None)
        if _uri_template:
            uri_template = _uri_template
        uri = uri_template.format(
              uri, self=self, aspect_id=aspect_id, direction=direction)
        return uri, kwargs

    def __call__(self, **kwargs) -> Dict:
        method = kwargs.pop('_method', 'get')

        uri, kwargs = self._build_uri( **kwargs)

        # actually make the request of the API
        if method in ['put', 'post', 'delete']:
            res = getattr(requests, method)(uri, headers=self.headers,
                                            data=json.dumps(kwargs))
        else:
            res = getattr(requests, method)(uri, headers=self.headers,
                                            params=kwargs)

        # print(res.url)  # debug...
        if res.status_code not in [requests.codes.ok, requests.codes.created]:
            res.raise_for_status()
        return res.json()["data"]
