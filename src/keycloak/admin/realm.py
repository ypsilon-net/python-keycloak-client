from keycloak.admin import KeycloakAdminBase, KeycloakAdminCollection

__all__ = ('Realm', 'Realms',)


class Realms(KeycloakAdminBase, KeycloakAdminCollection):
    _paths = {
        'collection': '/auth/admin/realms'
    }

    def __init__(self, *args, **kwargs):
        super(Realms, self).__init__(*args, **kwargs)

    def by_name(self, name):
        return Realm(name=name, admin=self._admin)

    def _url_collection_params(self):
        pass


class Realm(KeycloakAdminBase):
    _name = None

    def __init__(self, name, *args, **kwargs):
        self._name = name
        super(Realm, self).__init__(*args, **kwargs)

    @property
    def clients(self):
        from keycloak.admin.clients import Clients
        return Clients(realm_name=self._name, admin=self._admin)

    @property
    def users(self):
        from keycloak.admin.users import Users
        return Users(realm_name=self._name, admin=self._admin)
