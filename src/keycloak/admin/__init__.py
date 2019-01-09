import abc
import six
import re


__all__ = (
    'KeycloakAdmin',
    'KeycloakAdminBase',
    'KeycloakAdminBaseElement',
    'KeycloakAdminCollection',
)

PAT_VAR = re.compile('{([\_\w]+)}')

class KeycloakAdminBase(object):
    _admin = None
    _paths = None

    def __init__(self, admin, **kwargs):
        """
        :param keycloak.admin.KeycloakAdmin admin:
        """
        self._admin = admin

    def get_path(self, name, **kwargs):
        if self._paths is None:
            raise NotImplementedError()
        return self._paths[name].format(**kwargs)

    def get_path_dyn(self, name, **kwargs): # get path with dynamic path-arguments on member-vars
        if self._paths is None:
            raise NotImplementedError()

        path_args = {}
        for varname in PAT_VAR.findall(self._paths[name]):
            attr = '_%s' % varname
            if hasattr(self, attr):
                path_args[varname] = getattr(self, attr)
        path_args.update(kwargs)

        return self.get_path(name, **path_args)


class KeycloakAdminBaseElement(KeycloakAdminBase):
    _params = None
    _idents = None


    def __init__(self, params=None, *args, **kwargs):
        super(KeycloakAdminBaseElement, self).__init__(*args, **kwargs)
        self._params = params

    def __call__(self):
        if not self._params:
            self._params = self._admin.get(
                self._admin.get_full_url(self.get_path_dyn('single'))
            )
        return self._params

    def __repr__(self):
        params = [
            '%s="%s"' % (k[1:], v)
            for k, v in self.__dict__.items()
            if v and k.startswith('_') and k not in ['_params', '_paths', '_admin', '_paths', '_idents']
        ]
        if self._idents and self._params:
            for name, key in self._idents.items():
                params.append('%s="%s"' % (name, self().get(key)))

        return '<%s object %s>' % (self.__class__.__name__, " ".join(params))

    def get(self):
        res = self()
        if self._idents:
            for key, kc_key in self._idents.items():
                res[key] = res.pop(kc_key) if kc_key in res else None
        return res

class KeycloakAdmin(object):
    _realm = None
    _paths = {
        'root': '/'
    }
    _token = None

    def __init__(self, realm):
        """
        :param keycloak.realm.KeycloakRealm realm:
        """
        self._realm = realm

    def root(self):
        return self.get(
            self.get_full_url(self._paths['root'])
        )

    def get_full_url(self, *args, **kwargs):
        return self._realm.client.get_full_url(*args, **kwargs)

    def set_token(self, token):
        """
        Set token to authenticate the call or a callable which will be called
        to get the token.

        :param str | callable token:
        :rtype: KeycloakAdmin
        """
        self._token = token
        return self

    @property
    def realms(self):
        from keycloak.admin.realm import Realms
        return Realms(admin=self)

    def post(self, url, data, headers=None, **kwargs):
        return self._realm.client.post(
            url=url, data=data, headers=self._add_auth_header(headers=headers)
        )

    def put(self, url, data, headers=None, **kwargs):
        return self._realm.client.put(
            url=url, data=data, headers=self._add_auth_header(headers=headers)
        )

    def get(self, url, headers=None, **kwargs):
        return self._realm.client.get(
            url=url, headers=self._add_auth_header(headers=headers)
        )

    #
    # def delete(self, url, headers, **kwargs):
    #     return self.session.delete(url, headers=headers, **kwargs)

    def _add_auth_header(self, headers=None):
        if callable(self._token):
            token = self._token()
        else:
            token = self._token

        if token is None:
            raise Exception('No token stored in %s. You need to call %s.set_token with an valid access token/function first.' % (
                self.__class__.__name__, self.__class__.__name__
            ))

        headers = headers or {}
        headers['Authorization'] = "Bearer {}".format(token)
        headers['Content-Type'] = 'application/json'
        return headers


class KeycloakAdminCollection(KeycloakAdminBase):
    __metaclass__ = abc.ABCMeta
    _defaults_all_query = {} # default query-parameters
    _sort_col = None
    _sort_asc = True
    _itemclass = abc.ABCMeta

    def __iter__(self, *args, **kwargs):
        return self().__iter__(*args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        return self().__getitem__(*args, **kwargs)

    def __len__(self):
        return self().__len__()

    def __call__(self, **kwargs):
        return [
            self._itemclass(params=k, **self._url_item_params(k))
            for k in self.all(**kwargs)
        ]

    def __repr__(self):
        return repr([repr(k) for k in self()])

    def all(self, **kwargs):
        query = self._defaults_all_query.copy()
        query.update(kwargs)
        return self._all_sorted(self._admin.get(self._url_collection(**query)))

    def all_on(self, col, sort=True, **kwargs):
        res = self.unsorted().all(**kwargs)
        if col is not None:
            res = [u[col] for u in res]
            if sort:
                res.sort(key=lambda v: v.lower()) # case insensitive sorting
        return res

    def sorted_by(self, col, asc=True):  # scope
        self._sort_col = col
        self._sort_asc = asc
        return self

    def unsorted(self):  # scope
        self._sort_col = None
        return self

    def _all_sorted(self, res): # should be called in all-method by inherited class on request-result
        if self._sort_col:
            res.sort(key=lambda v: v[self._sort_col].lower(), reverse=not self._sort_asc) # case insensitive sorting
        return res

    def _all_reset(self):
        self._sort_col = None
        self._sort_asc = True

    def _url_collection(self, **kwargs): # TODO generalize?
        params = self._url_collection_params() or {} # path-params
        url = self._admin.get_full_url(self.get_path_dyn(self._url_collection_path_name(), **params))
        if kwargs:
            url += '?' + six.moves.urllib.parse.urlencode(kwargs)
        return url

    @abc.abstractmethod
    def _url_item_params(self, item):
        return {}

    def _url_collection_params(self): # returns path-parameters, which are neccessary on collection-request
        pass

    def _url_collection_path_name(self): # can be overwritten, if other path-names should be used
        return 'collection'
