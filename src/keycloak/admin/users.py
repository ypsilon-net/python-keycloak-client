import json
from collections import OrderedDict
from keycloak.admin import KeycloakAdminCollection, KeycloakAdminBaseElement

__all__ = ('User', 'Users',)


class User(KeycloakAdminBaseElement):
    _id = None
    _realm_name = None
    _paths = {
        'single': '/auth/admin/realms/{realm_name}/users/{id}',
    }
    _idents = {
        'attributes': 'attributes',
        'credentials': 'credentials',
        'email': 'email',
        'email_verified': 'emailVerified',
        'enabled': 'enabled',
        'first_name': 'firstName',
        'last_name': 'lastName',
        'username': 'username',
    }

    @classmethod
    def gen_payload(cls, **kwargs):
        res = {}
        for key, val in kwargs.items():
            if key not in cls._idents:
                continue
            if key == 'credentials':
                val = [val]
            res[cls._idents[key]] = val
        return res

    def __init__(self, realm_name, id, *args, **kwargs):
        self._id = id
        self._realm_name = realm_name
        super(User, self).__init__(*args, **kwargs)

    @property
    def id(self):
        return self._id

    @property
    def role_mappings(self):
        from keycloak.admin.role_mappings import RoleMappings
        return RoleMappings(admin=self._admin, realm_name=self._realm_name, user=self)

    def update(self, **kwargs):
        return self._admin.put(
            url=self._admin.get_full_url(self.get_path_dyn('single')),
            data=json.dumps(self.gen_payload(**kwargs))
        )


class Users(KeycloakAdminCollection):
    _defaults_all_query = { # https://www.keycloak.org/docs-api/2.5/rest-api/index.html#_get_users_2
        'max': -1, # turns off default max (100)
    }
    _paths = {
        'collection': '/auth/admin/realms/{realm_name}/users',
        'count': '/auth/admin/realms/{realm_name}/users/count',
    }
    _realm_name = None
    _itemclass = User

    def __init__(self, realm_name, *args, **kwargs):
        self._realm_name = realm_name
        super(Users, self).__init__(*args, **kwargs)

    def by_id(self, id):
        return User(admin=self._admin, realm_name=self._realm_name, id=id)

    def by_name(self, name):
        res = self.unsorted().all(username=name)
        if res:
            return self.by_id(res[0]['id'])

    def by_email(self, email):
        res = self.unsorted().all(email=email)
        if res:
            return self.by_id(res[0]['id'])

    def create(self, **kwargs):
        """
        Create a user in Keycloak

        http://www.keycloak.org/docs-api/3.4/rest-api/index.html#_users_resource

        :param str username:
        :param object credentials: (optional)
        :param str first_name: (optional)
        :param str last_name: (optional)
        :param str email: (optional)
        :param boolean enabled: (optional)
        """

        if 'username' not in kwargs or not kwargs['username'].strip():
            raise ValueError('Username is required')

        return self._admin.post(
            url=self._url_collection(),
            data=json.dumps(User.gen_payload(**kwargs))
        )

    def _url_item_params(self, data):
        return dict(
            id=data['id'], admin=self._admin, realm_name=self._realm_name,
        )
