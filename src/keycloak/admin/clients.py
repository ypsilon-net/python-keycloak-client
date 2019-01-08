from keycloak.admin import KeycloakAdminBase, KeycloakAdminCollection, KeycloakAdminBaseElement

__all__ = ('Client', 'Clients',)


class Client(KeycloakAdminBaseElement):
    _id = None
    _realm_name = None
    _paths = {
        'self': '/auth/admin/realms/{_realm_name}/clients/{_id}',
    }


    def __init__(self, realm_name, id, *args, **kwargs):
        self._id = id
        self._realm_name = realm_name
        super(Client, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<%s object realm="%s" id="%s" clientId="%s">' % (
            self.__class__.__name__, self._realm_name, self._id, self()['clientId'])

    @property
    def id(self):
        return self._id

    @property
    def roles(self):
        from keycloak.admin.roles import ClientRoles
        return ClientRoles(admin=self._admin, realm_name=self._realm_name, client_id=self._id)


class Clients(KeycloakAdminBase, KeycloakAdminCollection):
    _realm_name = None
    _paths = {
        'collection': '/auth/admin/realms/{realm}/clients'
    }
    _itemclass = Client

    def __init__(self, realm_name, *args, **kwargs):
        self._realm_name = realm_name
        super(Clients, self).__init__(*args, **kwargs)

    def by_id(self, id):
        return Client(admin=self._admin, realm_name=self._realm_name, id=id)

    def by_name(self, name):
        res = self.unsorted().all(clientId=name)
        if res:
            return self.by_id(res[0]['id'])

    def _url_collection_params(self):
        return {'realm': self._realm_name}

    def _url_item_params(self, data):
        return dict(
            id=data['id'], admin=self._admin, realm_name=self._realm_name
        )


