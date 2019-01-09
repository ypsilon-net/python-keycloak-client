from keycloak.admin import KeycloakAdminBase, KeycloakAdminCollection

__all__ = ('RoleMappings', 'ClientRoleMappings',)


class RoleMappings(KeycloakAdminBase, KeycloakAdminCollection):
    _realm_name = None
    _user_id = None
    _paths = {
        'collection': '/auth/admin/realms/{realm}/users/{id}/role-mappings',
    }

    def __init__(self, realm_name, user_id="not set", *args, **kwargs):
        self._realm_name = realm_name
        self._user_id = user_id
        super(RoleMappings, self).__init__(*args, **kwargs)

    def by_client_id(self, client_id):
        return ClientRoleMappings(admin=self._admin, realm_name=self._realm_name, user_id=self._user_id, client_id=client_id)

    def by_client_name(self, client_name):
        from keycloak.admin.clients import Clients
        client = Clients(admin=self._admin, realm_name=self._realm_name).by_name(client_name)
        if client:
            return self.by_client_id(client.id)

    def _url_collection_params(self):
        return {'realm': self._realm_name, 'id': self._user_id}

    def _url_item_params(self, data):
        return {} # TODO item-class & -handling has to be added first

class ClientRoleMappings(RoleMappings):
    _available = False
    _client_id = None
    _composite = False
    _paths = {
        'available': '/auth/admin/realms/{realm}/users/{id}/role-mappings/clients/{client}/available',
        'collection': '/auth/admin/realms/{realm}/users/{id}/role-mappings/clients/{client}',
        'composite': '/auth/admin/realms/{realm}/users/{id}/role-mappings/clients/{client}/composite',
    }

    def __init__(self, client_id, *args, **kwargs):
        self._client_id = client_id
        super(ClientRoleMappings, self).__init__(*args, **kwargs)

    def by_available(self): # scope
        self._available = True
        return self

    def by_composite(self): # scope
        self._composite = True
        return self

    @property
    def client_id(self):
        return self._client_id

    def create(self):
        pass

    @property
    def roles(self):
        from keycloak.admin.roles import ClientRoles
        return ClientRoles(admin=self._admin, realm_name=self._realm_name, client_id=self._client_id)

    def _url_collection_params(self):
        return {'realm': self._realm_name, 'id': self._user_id, 'client': self._client_id}

    def _url_collection_path_name(self):
        if self._available:
            return 'available'
        if self._composite:
            return 'composite'
        return super(ClientRoleMappings, self)._url_collection_path_name()

    def _url_item_params(self, data):
        return {}  # TODO item-class & -handling has to be added first
