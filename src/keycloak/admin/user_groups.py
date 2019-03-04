from keycloak.admin import KeycloakAdminBaseElement, KeycloakAdminCollection
from keycloak.admin.groups import Group

__all__ = ('UserGroup', 'UserGroups',)


class UserGroup(KeycloakAdminBaseElement):
    _paths = {
        'single': '/auth/admin/realms/{realm_name}/users/{user_id}/groups/{group_id}',
    }
    _realm_name = None
    _user_id = None
    _group_id = None

    def __init__(self, realm_name, user_id, group_id, *args, **kwargs):
        self._realm_name = realm_name
        self._user_id = user_id
        self._group_id = group_id
        super(UserGroup, self).__init__(*args, **kwargs)

    def __call__(self, **kwargs): # returns group itself -> calling of one user-group is not supported by keycloak
        return Group(admin=self._admin, realm_name=self._realm_name, id=self._group_id)()

    def create(self): # create user-group on given instance-attributes
        self._admin.put(url=self._admin.get_full_url(self.get_path_dyn('single')))
        return self


class UserGroups(KeycloakAdminCollection):
    _paths = {
        'collection': '/auth/admin/realms/{realm_name}/users/{user_id}/groups',
    }
    _realm_name = None
    _user_id = None
    _itemclass = UserGroup

    def __init__(self, realm_name, user_id, *args, **kwargs):
        self._realm_name = realm_name
        self._user_id = user_id
        super(UserGroups, self).__init__(*args, **kwargs)

    def by_group_id(self, group_id):
        return UserGroup(admin=self._admin, realm_name=self._realm_name, user_id=self._user_id, group_id=group_id)

    def by_group_path(self, group_path):
        for group in self.unsorted().all():
            if group['path'] == group_path:
                return self.by_group_id(group['id'])

    def create(self, group_id, **kwargs):
        return self.by_group_id(group_id).create()

    def _url_item_params(self, item):
        return dict(admin=self._admin, realm_name=self._realm_name, user_id=self._user_id, group_id=item['id'])
