import json

from lib.k8s import K8sClient


class patchRbacAuthorizationV1alpha1ClusterRole(K8sClient):

    def run(
            self,
            body,
            name,
            pretty=None,
            config_override=None):

        rc = False

        args = {}
        args['config_override'] = {}
        args['pretty'] = ''

        if config_override is not None:
            args['config_override'] = config_override

        if body is not None:
            args['body'] = body
        else:
            return (False, "body is a required parameter")
        if name is not None:
            args['name'] = name
        else:
            return (False, "name is a required parameter")
        if pretty is not None:
            args['pretty'] = pretty
        if 'body' in args:
            args['data'] = args['body']
        args['headers'] = {'Content-type': u'application/json-patch+json, application/merge-patch+json, application/strategic-merge-patch+json', 'Accept': u'application/json, application/yaml, application/vnd.kubernetes.protobuf'}  # pylint: disable=line-too-long
        args['url'] = "apis/rbac.authorization.k8s.io/v1alpha1/clusterroles/{name}".format(body=body, name=name )
        args['method'] = "patch"

        self.addArgs(**args)
        self.makeRequest()

        myresp = {}
        myresp['status_code'] = self.resp.status_code
        myresp['data'] = json.loads(self.resp.content.rstrip())

        if myresp['status_code'] >= 200 and myresp['status_code'] <= 299:
            rc = True

        return (rc, myresp)