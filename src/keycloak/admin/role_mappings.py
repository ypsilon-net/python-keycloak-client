from keycloak.admin import KeycloakAdminBase, KeycloakAdminCollection
from keycloak.admin.clients import Clients, Client

__all__ = ('RoleMappings', 'RoleMappingClients', 'RoleMappingClient',)


class RoleMappings(KeycloakAdminBase, KeycloakAdminCollection):
    _client = None
    _realm_name = None
    _user_id = None
    _paths = {
        'collection': '/auth/admin/realms/{realm}/users/{id}/role-mappings',
    }

    def __init__(self, realm_name, user_id, *args, **kwargs):
        self._realm_name = realm_name
        self._user_id = user_id
        super(RoleMappings, self).__init__(*args, **kwargs)

    @property
    def clients(self):
        return RoleMappingClients(admin=self._admin, realm_name=self._realm_name, user_id=self._user_id)

    def _url_collection_params(self):
        return {'realm': self._realm_name, 'id': self._user_id}

class RoleMappingClients(Clients):
    _user_id = None

    def __init__(self, user_id, *args, **kwargs):
        self._user_id = user_id
        super(RoleMappingClients, self).__init__(*args, **kwargs)

    def by_id(self, id):
        return RoleMappingClient(admin=self._admin, realm_name=self._realm_name, id=id, user_id=self._user_id)


class RoleMappingClient(Client, KeycloakAdminCollection):
    _available = False
    _composite = False
    _paths = {
        'collection': '/auth/admin/realms/{realm}/users/{id}/role-mappings/clients/{client}',
        'available': '/auth/admin/realms/{realm}/users/{id}/role-mappings/clients/{client}/available',
        'composite': '/auth/admin/realms/{realm}/users/{id}/role-mappings/clients/{client}/composite',
    }
    _user_id = None

    def __init__(self, user_id,  *args, **kwargs):
        self._user_id = user_id
        super(RoleMappingClient, self).__init__(*args, **kwargs)

    def by_available(self): # scope
        self._available = True
        return self

    def by_composite(self): # scope
        self._composite = True
        return self

    @property
    def id(self):
        return self._id

    def _url_collection_params(self):
        return {'realm': self._realm_name, 'id': self._user_id, 'client': self._id}

    def _url_collection_path_name(self):
        if self._available:
            return 'available'
        if self._composite:
            return 'composite'
        return super(RoleMappingClient, self)._url_collection_path_name()
