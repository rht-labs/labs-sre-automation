#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import requests

"""
An ansible module to wrap the calls to GitLab using pagination.
"""

# pylint: disable=redefined-builtin,wildcard-import,unused-wildcard-import
from ansible.module_utils.basic import *


DOCUMENTATION = '''
---
module: rest_get
short_description: Perform REST Calls to get data and to better handle REST pagination
author: Øystein Bedin & Jacob See
requirements: [ ]
'''
EXAMPLES = '''
rest_get:
    url: "https://gitlab.com/api/v4/groups/1234/projects?include_subgroups=true"
    token: "123456789"
'''


def main():
    module = AnsibleModule(
        argument_spec=dict(
            url=dict(required=True),
            token=dict(required=False),
        ),
        supports_check_mode=True,
    )

    # Retrieve the parameters passed in
    url         = module.params['url']
    token       = module.params['token']

    # Initialize the output to empty list
    rest_output = []

    next_call = url

    # Loop till the 'next' element contains Null/None
    while next_call is not None:
        r = requests.get(
            next_call,
            headers={
                "Private-Token": token
            },
            verify=False
        )

        # Fetch the next URI returned by the REST call
        # TODO: better error handling when REST service returns non-200 OK
        if "X-Next-Page" in r.headers and str.isdigit(r.headers["X-Next-Page"]):
            if int(r.headers["X-Next-Page"]) <= int(r.headers["X-Total-Pages"]):
                next_call = url + "&page=" + r.headers["X-Next-Page"]
        else:
            next_call = None

        # Merge the results json to the output list of items
        rest_output = rest_output + r.json()

    module.exit_json(
      changed=False,
      rest_output=rest_output
    )


if __name__ == '__main__':
    main()
