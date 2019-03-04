from keycloak.admin import KeycloakAdminCollection, KeycloakAdminBaseElement
from keycloak.admin.users import User

__all__ = ('Group', 'Groups',)


class Group(KeycloakAdminBaseElement):
    _id = None
    _realm_name = None
    _paths = {
        'single': '/auth/admin/realms/{realm_name}/groups/{id}',
        'subs': '/auth/admin/realms/{realm_name}/groups/{id}/children',
    }
    _idents = {
        'name': 'name',
        'path': 'path',
        'subs': 'subGroups',
    }

    def __init__(self, realm_name, id, *args, **kwargs):
        self._id = id
        self._realm_name = realm_name
        super(Group, self).__init__(*args, **kwargs)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self().get('name')

    @property
    def path(self):
        return self().get('path')

    @property
    def subs(self):
        return [
            Group(params=sg, admin=self._admin, realm_name=self._realm_name, id=sg['id'])
            for sg in self().get('subGroups')
        ]

    @property
    def members(self):
        return GroupMembers(admin=self._admin, realm_name=self._realm_name, group_id=self._id)

    def create_sub(self, name, **kwargs):
        kwargs['name'] = name
        return self.create(self._admin,
                           self._admin.get_full_url(self.get_path_dyn('subs')),
                           **kwargs)

    def sub_by_path(self, path):
        for sub in self().get('subGroups'):
            if sub['path'] == path:
                return Group(admin=self._admin, realm_name=self._realm_name, id=sub['id'])


class Groups(KeycloakAdminCollection):
    _defaults_all_query = { # https://www.keycloak.org/docs-api/2.5/rest-api/index.html#_get_users_2
        'max': -1, # turns off default max (100)
    }
    _paths = {
        'collection': '/auth/admin/realms/{realm_name}/groups',
        'count': '/auth/admin/realms/{realm_name}/groups/count',
    }
    _realm_name = None
    _itemclass = Group

    def __init__(self, realm_name, *args, **kwargs):
        self._realm_name = realm_name
        super(Groups, self).__init__(*args, **kwargs)

    def __len__(self):
        return self.count()

    def by_id(self, group_id):
        return Group(admin=self._admin, realm_name=self._realm_name, id=group_id)

    def by_name(self, name):
        groups = self.unsorted().all(search=name)
        return self._by_name(name, groups)

    def by_path(self, path):
        groups = self.unsorted().all(search=path.split('/')[-1])
        return self._by_path(path, groups)

    def count(self):
        return super(Groups, self).count()['count']

    def create(self, name, **kwargs):
        kwargs['name'] = name
        return super(Groups, self).create(**kwargs)

    def create_path(self, path, **kwargs):
        names = path.strip('/').split('/')
        group = None
        for idx, name in enumerate(names):
            path = '/' + '/'.join(names[:idx + 1])
            if group:
                group = group.sub_by_path(path) or group.create_sub(name)
            else: # set root
                group = self.by_path(path) or self.create(name)
        return group

    def _by_name(self, name, groups): # recursive; called by by_name
        res = []
        for group in groups:
            if group['name'] == name:
                res.append(Group(admin=self._admin, realm_name=self._realm_name, id=group['id']))
            res += self._by_name(name, group['subGroups'])
        return res

    def _by_path(self, path, groups, path_idx=0): # recursive; called by by_path
        path_search = '/' + '/'.join(path.strip('/').split('/')[:path_idx+1])
        for group in groups:
            if group['path'] == path:
                return self.by_id(group['id'])
            if path != path_search and group['path'] == path_search:
                return self._by_path(path, group['subGroups'], path_idx + 1)

    def _url_item_params(self, data):
        return dict(
            id=data['id'], admin=self._admin, realm_name=self._realm_name,
        )


class GroupMembers(KeycloakAdminCollection):
    _defaults_all_query = { # https://www.keycloak.org/docs-api/2.5/rest-api/index.html#_get_users_2
        'max': -1, # turns off default max (100)
    }
    _group_id = None
    _itemclass = User
    _paths = {
        'collection': '/auth/admin/realms/{realm_name}/groups/{group_id}/members',
        # 'count': '/auth/admin/realms/{realm_name}/users/count',
    }
    _realm_name = None

    def __init__(self, realm_name, group_id, *args, **kwargs):
        self._realm_name = realm_name
        self._group_id = group_id
        super(GroupMembers, self).__init__(*args, **kwargs)

    def _url_item_params(self, data):
        return dict(
            id=data['id'], admin=self._admin, realm_name=self._realm_name,
        )
