import ast
import json
import sys

import requests
from requests.auth import HTTPBasicAuth

from st2reactor.sensor.base import Sensor


class SensorBase(Sensor):

    def __init__(self, sensor_service, extension, trigger_ref, config=None):
        super(
            SensorBase,
            self).__init__(
            sensor_service=sensor_service,
            config=config)
        self._log = self._sensor_service.get_logger(__name__)
        self.TRIGGER_REF = trigger_ref
        self.extension = extension
        self.client = None

    def setup(self):
        try:
            extension = self.extension
            KUBERNETES_API_URL = self._config['kubernetes_api_url'] + extension
            user = self._config['user']
            password = self._config['password']
            verify = self._config['verify']
        except KeyError:
            self._log.exception(
                'Configuration file does not contain required fields.')
            raise
        self._log.debug(
            'Connecting to Kubernetes endpoint %s via api_client.' %
            KUBERNETES_API_URL)
        self.client = requests.get(
            KUBERNETES_API_URL, auth=HTTPBasicAuth(
                user, password), verify=verify, stream=True)

    def run(self):
        self._log.debug('Watch %s for new information.' % self.extension)
        r = self.client
        lines = r.iter_lines()
        # Save the first line for later or just skip it
        # first_line = next(lines)

        for line in lines:
            try:
                trigger_payload = self._get_trigger_payload_from_line(line)
            except:
                msg = (
                    'Failed generating trigger payload from line %s. Aborting sensor!!!' %
                    line)
                self._log.exception(msg)
                sys.exit(1)
            else:
                if trigger_payload == 0:
                    pass
                else:
                    self._log.debug('Triggering Dispatch Now')
                    self._sensor_service.dispatch(
                        trigger=self.TRIGGER_REF, payload=trigger_payload)

    def _get_trigger_payload_from_line(self, line):
        k8s_object = self._fix_utf8_enconding_and_eval(line)
        self._log.debug(
            'Incoming k8s object (from API response): %s',
            k8s_object)
        payload = self._k8s_object_to_st2_trigger(k8s_object)
        return payload

    def _fix_utf8_enconding_and_eval(self, line):
        # need to perform a json dump due to uft8 error prior to performing a
        # json.load
        io = json.dumps(line)
        n = json.loads(io)
        line = ast.literal_eval(n)
        return line

    def _k8s_object_to_st2_trigger(self, k8s_object):
        # Define some variables
        try:
            resource_type = k8s_object['type']
            object_kind = k8s_object['object']['kind']
            name = k8s_object['object']['metadata']['name']
            if 'namespace' in k8s_object['object']['metadata']:
                namespace = k8s_object['object']['metadata']['namespace']
            else:
                namespace = 'None'
            uid = k8s_object['object']['metadata']['uid']
            if 'labels' in k8s_object['object']['metadata']:
                labels_data = k8s_object['object']['metadata']['labels']
            else:
                labels_data = 'None'
        except KeyError:
            msg = 'One of "type", "kind", "name" or "uid" or "labels" ' + \
                  'do not exist in the object. Incoming object=%s' % k8s_object
            self._log.exception(msg)
            # raise
            return 0
        else:
            if name in ['default', 'kube-system']:
                self._log.info('Name: %s.' % name)
                return 0
            else:
                payload = self._build_a_trigger(
                    resource_type=resource_type,
                    name=name,
                    labels=labels_data,
                    namespace=namespace,
                    object_kind=object_kind,
                    uid=uid)
                self._log.debug('Trigger payload: %s.' % payload)
                #self._log.info('Trigger payload: %s.' % payload)
                return payload

    def _build_a_trigger(
            self,
            resource_type,
            name,
            labels,
            namespace,
            object_kind,
            uid):
        payload = {
            'resource': resource_type,
            'name': name,
            'namespace': namespace,
            'labels': labels,
            'object_kind': object_kind,
            'uid': uid
        }

        return payload

    def cleanup(self):
        pass

    def add_trigger(self, trigger):
        pass

    def update_trigger(self, trigger):
        pass

    def remove_trigger(self, trigger):
        pass
