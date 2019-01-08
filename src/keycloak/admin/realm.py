from keycloak.admin import KeycloakAdminBase, KeycloakAdminCollection, KeycloakAdminBaseElement

__all__ = ('Realm', 'Realms',)


class Realm(KeycloakAdminBaseElement):
    _name = None
    _paths = {
        'self': '/auth/admin/realms/{_name}',
    }

    def __init__(self, name, *args, **kwargs):
        self._name = name
        super(Realm, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<%s object name="%s">' % (
            self.__class__.__name__, self._name,)

    def _url_collection_params(self):
        return {'realm': self._name}

    @property
    def clients(self):
        from keycloak.admin.clients import Clients
        return Clients(realm_name=self._name, admin=self._admin)

    @property
    def users(self):
        from keycloak.admin.users import Users
        return Users(realm_name=self._name, admin=self._admin)


class Realms(KeycloakAdminBase, KeycloakAdminCollection):
    _paths = {
        'collection': '/auth/admin/realms'
    }
    _itemclass = Realm

    def __init__(self, *args, **kwargs):
        super(Realms, self).__init__(*args, **kwargs)

    def by_name(self, name):
        return Realm(name=name, admin=self._admin)

    def _url_collection_params(self):
        pass

    def _url_item_params(self, data):
        return dict(name=data['realm'], admin=self._admin)


