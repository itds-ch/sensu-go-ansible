#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Paul Arthur <paul.arthur@flowerysong.com>
# Copyright: (c) 2019, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["stableinterface"],
    "supported_by": "certified",
}

DOCUMENTATION = '''
module: silence
author:
  - Paul Arthur (@flowerysong)
  - Aljaz Kosir (@aljazkosir)
  - Manca Bizjak (@mancabizjak)
  - Tadej Borovsak (@tadeboro)
short_description: Manage Sensu silences
description:
  - Create, update or delete Sensu silence.
  - For more information, refer to the Sensu documentation at
    U(https://docs.sensu.io/sensu-go/latest/reference/silencing/).
version_added: 1.0.0
extends_documentation_fragment:
  - sensu.sensu_go.auth
  - sensu.sensu_go.namespace
  - sensu.sensu_go.state
  - sensu.sensu_go.labels
  - sensu.sensu_go.annotations
seealso:
  - module: sensu.sensu_go.silence_info
options:
  subscription:
    description:
      - The name of the subscription the entry should match. If left empty a silencing entry will
        contain an asterisk in the subscription position. This indicates that any event with a
        matching check name will be marked as silenced, regardless of the originating entities
        subscriptions. Specific entity can also be targeted by taking advantage of per-entity
        subscription (entity:<entity_name>)
      - This parameter is required if the I(check) parameter is absent.
    type: str
  check:
    description:
     - The name of the check the entry should match. If left empty a silencing entry will contain an
       asterisk in the check position. This indicates that any event where the originating entities
       subscriptions match the subscription specified in the entry will be marked as silenced,
       regardless of the check name.
      - This parameter is required if the I(subscription) parameter is absent.
    type: str
  begin:
    description:
      - UNIX time at which silence entry goes into effect.
    type: int
  expire:
    description:
      - Number of seconds until the silence expires.
    type: int
  expire_on_resolve:
    description:
      - If the entry should be deleted when a check begins return OK status (resolves).
    type: bool
  reason:
    description:
      - Reason for silencing.
    type: str
'''

EXAMPLES = '''
- name: Silence a specific check
  sensu.sensu_go.silence:
    subscription: proxy
    check: check-disk

- name: Silence specific check regardless of the originating entities subscription
  sensu.sensu_go.silence:
    check: check-cpu

- name: Silence all checks on a specific entity
  sensu.sensu_go.silence:
    subscription: entity:important-entity
    expire: 120
    reason: rebooting the world

- name: Delete a silencing entry
  sensu.sensu_go.silence:
    subscription: entity:important-entity
    state: absent
'''

RETURN = '''
object:
  description: object representing Sensu silence
  returned: success
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors, utils


def main():
    required_one_of = [
        ['subscription', 'check']
    ]
    module = AnsibleModule(
        supports_check_mode=True,
        required_one_of=required_one_of,
        argument_spec=dict(
            arguments.get_spec(
                'auth', 'state', 'labels', 'annotations', 'namespace',
            ),
            subscription=dict(),
            check=dict(),
            begin=dict(
                type='int',
            ),
            expire=dict(
                type='int',
            ),
            expire_on_resolve=dict(
                type='bool'
            ),
            reason=dict()
        ),
    )
    name = '{0}:{1}'.format(module.params['subscription'] or '*', module.params['check'] or '*')

    client = arguments.get_sensu_client(module.params['auth'])
    path = utils.build_core_v2_path(
        module.params['namespace'], 'silenced', name,
    )
    # We add name parameter because it is actually required and must match the name that is
    # autogenerated on the API
    module.params['name'] = name
    payload = arguments.get_mutation_payload(
        module.params, 'subscription', 'check', 'begin', 'expire', 'expire_on_resolve', 'reason'
    )
    try:
        changed, silence = utils.sync(
            module.params['state'], client, path, payload, module.check_mode,
        )
        module.exit_json(changed=changed, object=silence)
    except errors.Error as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
