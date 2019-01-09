from keycloak.admin import KeycloakAdminBase, KeycloakAdminCollection
from keycloak.admin.roles import RealmRole, ClientRole, ClientRoles

__all__ = ('RoleMappings', 'ClientRoleMappings',)


class RoleMappings(KeycloakAdminBase, KeycloakAdminCollection):
    _realm_name = None
    _user_id = None
    _paths = {
        'collection': '/auth/admin/realms/{realm_name}/users/{user_id}/role-mappings',
    }
    # _itemclass = {'realmMappings': RealmRole, 'clientMappings': ClientRoleMappings}
    #, 'clientMappings': ClientRole}


    def __init__(self, realm_name, user_id, *args, **kwargs):
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
        return {'realm_name': self._realm_name, 'user_id': self._user_id}

    def _url_item_params(self, pos, data):
        if pos == 'realmMappings':
            return dict(
                role_name=data['name'], admin=self._admin, realm_name=self._realm_name
            )
        elif pos == 'clientMappings':
            print (data)
            return dict(
                client=data['id'], admin=self._admin, realm_name=self._realm_name, user_id=self._user_id
            )

class ClientRoleMappings(RoleMappings):
    _available = False
    _client = None
    _composite = False
    _paths = {
        'available': '/auth/admin/realms/{realm_name}/users/{user_id}/role-mappings/clients/{client_id}/available',
        'collection': '/auth/admin/realms/{realm_name}/users/{user_id}/role-mappings/clients/{client_id}',
        'composite': '/auth/admin/realms/{realm_name}/users/{user_id}/role-mappings/clients/{client_id}/composite',
    }
    _itemclass = ClientRole

    def __init__(self, client, *args, **kwargs):
        super(ClientRoleMappings, self).__init__(*args, **kwargs)

        from keycloak.admin.clients import Client
        if isinstance(client, Client):
            self._client = client
        else:
            self._client = Client(admin=self._admin, realm_name=self._realm_name, id=client)

    @property
    def _client_id(self):
        return self._client.id


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
        return ClientRoles(admin=self._admin, realm_name=self._realm_name, client=self._client_id)

    def _url_collection_params(self):
        return {'realm_name': self._realm_name, 'user_id': self._user_id, 'client_id': self._client_id}

    def _url_collection_path_name(self):
        if self._available:
            return 'available'
        if self._composite:
            return 'composite'
        return super(ClientRoleMappings, self)._url_collection_path_name()

    def _url_item_params(self, data):
        return dict(
            role_name=data['name'], admin=self._admin, realm_name=self._realm_name, client=self._client
        )


RoleMappings._itemclass = {'realmMappings': RealmRole, 'clientMappings': ClientRoleMappings}

