from keycloak.admin import KeycloakAdminCollection, KeycloakAdminBaseElement
from keycloak.admin.clients import Client
from copy import copy

__all__ = (
    'ResourceServer',
    'Resources',
    'Resource',
    'Scopes',
    'Scope',
    'Policies',
    # 'Policy',
    'RolePolicy',
    'GroupPolicy',
    'Permissions',
    # 'Permission',
    'ScopePermission',
    'ResourcePermission',
    'AssociatedPolicies',
    'AssociatedResources',
    'AssociatedScopes',
)

class ResurcesServerSubCollection(KeycloakAdminCollection):
    _realm_name = None
    _client = None

    def __init__(self, realm_name, client, *args, **kwargs):
        self._realm_name = realm_name
        super(ResurcesServerSubCollection, self).__init__(*args, **kwargs)

        if isinstance(client, Client):
            self._client = client
        else:
            self._client = Client(admin=self._admin, realm_name=self._realm_name, id=client)

    @property
    def _client_id(self):
        return self._client.id

    def by_name(self, name):
        if isinstance(self._itemclass, tuple):
            res = self.unsorted().all(**{self._itemclass[1][None]._idents['name']: name})
            if res:
                lookupKey, mapping = self._itemclass
                itemclass = mapping.get(res[0].get(lookupKey), mapping[None])
                return itemclass(
                    # params=res[0],
                    admin=self._admin, realm_name=self._realm_name, client=self._client,
                    id=res[0][itemclass._idents['id']],)
        else:
            res = self.unsorted().all(**{self._itemclass._idents['name']: name})
            if res:
                return self._itemclass(
                    params=res[0],
                    admin=self._admin, realm_name=self._realm_name, client=self._client,
                    id=res[0][self._itemclass._idents['id']],)

    def by_id(self, id):
        if isinstance(self._itemclass, tuple):
            lookupKey, mapping = self._itemclass
            # to find correct type get the general one first
            tmpItem = mapping[None](
                admin=self._admin, realm_name=self._realm_name, client=self._client, id=id)
            itemclass = mapping.get(tmpItem().get(lookupKey))
            if itemclass:
                return itemclass(admin=self._admin, realm_name=self._realm_name, client=self._client,
                    id=id)
            else:
                return tmpItem
        else:
            return self._itemclass(admin=self._admin, realm_name=self._realm_name, client=self._client,
                id=id)

    def _url_item_params(self, data, itemclass=None):
        if itemclass is None:
            itemclass = self._itemclass
        return dict(
            admin=self._admin, realm_name=self._realm_name, client=self._client,
            id=data[itemclass._idents['id']],
        )


class ResurcesServerSubElement(KeycloakAdminBaseElement):
    # _gen_payload_full_on_update = True
    _id = None
    _realm_name = None
    _client = None
    _idents = {
        'name': 'name',
        'id': 'id',
    }
    def __init__(self, realm_name, client, id, *args, **kwargs):
        self._realm_name = realm_name
        self._id = id
        super(ResurcesServerSubElement, self).__init__(*args, **kwargs)

        if isinstance(client, Client):
            self._client = client
        else:
            self._client = Client(admin=self._admin, realm_name=self._realm_name, client=self._client, id=client)

    @property
    def _client_id(self):
        return self._client.id

    @property
    def id(self):
        return self._id


class Resource(ResurcesServerSubElement):
    _paths = {
        'single': '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server/resource/{id}'
    }
    _idents = {
        'name': 'name',
        'id': '_id',
        'display_name': 'displayName',
        'owner_managed_access': 'ownerManagedAccess',
        'owner': 'owner',
        'attributes': 'attributes',
        'uri': 'uri',
        'type': 'type',
        'scopes': 'scopes',
    }


class Resources(ResurcesServerSubCollection):
    _paths = {
        'collection': '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server/resource'
    }
    _itemclass = Resource


class Scope(ResurcesServerSubElement):
    _paths = {
        'single': '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server/scope/{id}',
    }
    _idents = {
        'name': 'name',
        'id': 'id',
    }


class Scopes(ResurcesServerSubCollection):
    _realm_name = None
    _client = None
    _paths = {
        'collection': '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server/scope'
    }
    _itemclass = Scope


class Policy(ResurcesServerSubElement):
    _paths = {
        'single': '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server/policy/{id}',
    }
    _idents = {
        'name': 'name',
        'id': 'id',
        'config': 'config',
        'decision_strategy': 'decisionStrategy',
        'logic': 'logic',
        'type': 'type',
        # 'owner': 'owner',
        # 'policies': 'policies',
        # 'resources': 'resources',
        # 'scopes': 'scopes'
    }

class RolePolicy(Policy):
    _paths = {
        'single': '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server/policy/role/{id}',

    }
    _idents = {
        'name': 'name',
        'id': 'id',
        'decision_strategy': 'decisionStrategy',
        'logic': 'logic',
        'type': 'type',
        'description': 'description',

        'roles': 'roles',
    }

class GroupPolicy(Policy):
    _paths = {
        'single': '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server/policy/group/{id}',

    }
    _idents = {
        'name': 'name',
        'id': 'id',
        'decision_strategy': 'decisionStrategy',
        'logic': 'logic',
        'type': 'type',

        'groups': 'groups',
        'groups_claim': 'groupsClaim',
    }




class Policies(ResurcesServerSubCollection):
    _paths = {
        'collection': '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server/policy',
        RolePolicy: '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server/policy/role/',
        GroupPolicy: '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server/policy/group/',
    }
    _itemclass = ('type', {
        None: Policy,
        'role': RolePolicy,
        'group': GroupPolicy,
    })

class AssociatedBase(KeycloakAdminCollection):
    _permission = None

    def __init__(self, permission, *args, **kwargs):
        self._permission = permission
        super(AssociatedBase, self).__init__(*args, **kwargs)

    @property
    def _permission_id(self):
        return self._permission.id


class AssociatedPolicies(Policies, AssociatedBase):
    _paths = {
        'collection': '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server/policy/{permission_id}/associatedPolicies',
    }

class AssociatedResources(Resources, AssociatedBase):
    _paths = {
        'collection': '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server/policy/{permission_id}/resources',
    }

class AssociatedScopes(Scopes, AssociatedBase):
    _paths = {
        'collection': '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server/policy/{permission_id}/scopes',
    }


class Permission(ResurcesServerSubElement):
    _paths = {
        'single': '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server/permission/{id}',
    }
    _idents = {
        'name': 'name',
        'id': 'id',
        'type': 'type',
        'decision_strategy': 'decisionStrategy',
        'logic': 'logic',
        'type': 'type',
        'resources': 'resources',
        'policies': 'policies',
        #'scopes': 'scopes'
    }
    # def __init__(self, *args, **kwargs):
    #     super(Permission, self).__init__(*args, **kwargs)

    @property
    def policies(self):
        return AssociatedPolicies(admin=self._admin, realm_name=self._realm_name, client=self._client, permission=self)

    @property
    def resources(self):
        return AssociatedResources(admin=self._admin, realm_name=self._realm_name, client=self._client, permission=self)


class ResourcePermission(Permission):
    _paths = {
        'single': '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server/permission/resource/{id}',
    }
    _idents = copy(Permission._idents)
    _idents.update({
        'resource_type': 'resourceType',
    })


class ScopePermission(Permission):
    _paths = {
        'single': '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server/permission/scope/{id}',
    }
    _idents = copy(Permission._idents)
    _idents.update({
        'scopes': 'scopes',
    })

    @property
    def scopes(self):
        return AssociatedScopes(admin=self._admin, realm_name=self._realm_name, client=self._client, permission=self)


class Permissions(ResurcesServerSubCollection):
    _paths = {
        'collection': '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server/permission',
        ResourcePermission: '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server/permission/resource/',
        ScopePermission: '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server/permission/scope/',
    }
    _itemclass = ('type', {
        'resource': ResourcePermission,
        'scope': ScopePermission,
        None: Permission,
    })


class ResourceServer(KeycloakAdminBaseElement):
    _id = None
    _realm_name = None
    _paths = {
        'single': '/auth/admin/realms/{realm_name}/clients/{client_id}/authz/resource-server',
    }
    _idents = {
        'name': 'name',
        'allow_remote_resource_management': 'allowRemoteResourceManagement',
        'id': 'id',
        'client_id': 'clientId',
        'policy_enforcement_mode': 'policyEnforcementMode',
    }

    def __init__(self, realm_name, client, *args, **kwargs):
        self._realm_name = realm_name
        super(ResourceServer, self).__init__(*args, **kwargs)

        if isinstance(client, Client):
            self._client = client
        else:
            self._client = Client(admin=self._admin, realm_name=self._realm_name, id=client)

    @property
    def _client_id(self):
        return self._client.id

    @property
    def scopes(self):
        return Scopes(admin=self._admin, realm_name=self._realm_name, client=self._client)

    @property
    def resources(self):
        return Resources(admin=self._admin, realm_name=self._realm_name, client=self._client)

    @property
    def policies(self):
        return Policies(admin=self._admin, realm_name=self._realm_name, client=self._client)

    @property
    def permissions(self):
        return Permissions(admin=self._admin, realm_name=self._realm_name, client=self._client)




