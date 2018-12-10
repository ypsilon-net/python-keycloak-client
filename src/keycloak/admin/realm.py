from keycloak.admin import KeycloakAdminBase

__all__ = ('Realm', 'Realms',)


class Realms(KeycloakAdminBase):
    _paths = {
        'collection': '/auth/admin/realms'
    }

    def __init__(self, *args, **kwargs):
        super(Realms, self).__init__(*args, **kwargs)

    def all(self):
        return self._client.get(
            self._client.get_full_url(
                self.get_path('collection')
            )
        )

    def all_names(self):
        return [r['realm'] for r in self.all()]

    def by_name(self, name):
        return Realm(name=name, client=self._client)


class Realm(KeycloakAdminBase):
    _name = None

    def __init__(self, name, *args, **kwargs):
        self._name = name
        super(Realm, self).__init__(*args, **kwargs)

    @property
    def clients(self):
        from keycloak.admin.clients import Clients
        return Clients(realm_name=self._name, client=self._client)

    @property
    def users(self):
        from keycloak.admin.users import Users
        return Users(realm_name=self._name, client=self._client)
