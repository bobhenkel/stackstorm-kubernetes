from lib import k8s

from st2common.runners.base_action import Action


class listRbacAuthorizationV1alpha1RoleForAllNamespaces(Action):

    def run(
            self,
            config_override=None,
            fieldSelector=None,
            labelSelector=None,
            pretty=None,
            resourceVersion=None,
            timeoutSeconds=None,
            watch=None):

        myk8s = k8s.K8sClient(self.config)

        rc = False

        args = {}
        if config_override is not None:
            args['config_override'] = config_override
        if fieldSelector is not None:
            args['fieldSelector'] = fieldSelector
        if labelSelector is not None:
            args['labelSelector'] = labelSelector
        if pretty is not None:
            args['pretty'] = pretty
        if resourceVersion is not None:
            args['resourceVersion'] = resourceVersion
        if timeoutSeconds is not None:
            args['timeoutSeconds'] = timeoutSeconds
        if watch is not None:
            args['watch'] = watch
        resp = myk8s.runAction(
            'listRbacAuthorizationV1alpha1RoleForAllNamespaces',
            **args)

        if resp['status'] >= 200 and resp['status'] <= 299:
            rc = True

        return (rc, resp)
