# coding: utf8

ldap_available = False
if param.ldap_authentication:
    import re
    try:
        import ldap
    except ImportError:
        print('No ldap module detected. Please install python-ldap. AD search disabled.')
    else:
        ldap_available = True


class ldap_con:
    def __init__(self):
        if ldap_available:
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            ldap.set_option(ldap.OPT_REFERRALS, 0)
            self.con = ldap.initialize(param.ldap_url)
            self.con.set_option(ldap.OPT_REFERRALS, 0)
            self.con.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            self.con.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
            self.con.set_option( ldap.OPT_X_TLS_DEMAND, True )
            self.con.set_option( ldap.OPT_DEBUG_LEVEL, 255 )
            self.con.simple_bind_s(param.ldap_username, param.ldap_password)
            self.ldap_base_dn = param.ldap_base_dn

    def getListUsers(self):
        if not ldap_available:
            return "Ldap Disabled or module not available."
        result = self.con.search_ext_s(
                param.ldap_base_dn,
                ldap.SCOPE_SUBTREE,
                "(&(objectClass=person)(department=*))",
                ["sAMAccountName", "cn", "mail"],
                )
        # result[0][1]['cn'][0] represents the cn of the first user of the list.
        lst = map(lambda x: x[1], result)
        res = list()
        for x in lst:
            if type(x)==type({}):
                res.append(x['cn'])
        return res

    def getDictUsers(self, partialstr=''):
        if not ldap_available:
            return "Ldap Disabled or module not available."
        if (re.match( '^[a-zA-Z ]*$', partialstr)):
            #self.con.simple_bind_s(username, password)
            result = self.con.search_ext_s(self.ldap_base_dn, ldap.SCOPE_SUBTREE, "(&(objectClass=person)(department=*)(cn=%s*))" %  partialstr, ["sAMAccountName", "cn", "mail"])
            # result[0][1]['cn'][0] represents the cn of the first user of the list.
            lst = map(lambda x: x[1], result)
            res = dict()
            for x in lst:
                if type(x)==type({}):
                    res[x['sAMAccountName'][0]]=x['cn'][0]
            return res
        else:
            return ''

    def getGroupsOwnership(self, username_bare):
        # Followin returns a dict of list(s)
        # result[0][1]['memberOf'][0] is the first group in list.
        # self.con.simple_bind_s(username, password)
        if not ldap_available:
            return "Ldap Disabled or module not available."
        result = self.con.search_s(self.ldap_base_dn, ldap.SCOPE_SUBTREE, "(&(sAMAccountName=%s))" % (username_bare, ), ['memberOf',])[0][1]
        return tuple(result['memberOf'])

    def getManager(self, username_bare):
        """
        This function get the Manager of the userid
        """
        if not ldap_available:
            return "Ldap Disabled or module not available."
        result = self.con.search_ext_s(self.ldap_base_dn, ldap.SCOPE_SUBTREE, "(&(sAMAccountName=%s))" % (username_bare, ), ['manager',])[0][1]
        return result['manager'][0]

    def getDetails(self, username_bare):
        if not ldap_available:
            return "Ldap Disabled or module not available."
        result = self.con.search_ext_s(self.ldap_base_dn, ldap.SCOPE_SUBTREE, "(&(sAMAccountName=%s))" % (username_bare, ))[0][1]
        return result

if ldap_available:
    try:
        ldap_connection = ldap_con()
    except Exception as e:
        print('Cannot connect to LDAP : %s, or there is an error in the LDAP parameters.' % (param.ldap_url,))
        print(e)
        ldap_connection = None
        ldap_available = False
else:
    ldap_connection = None


if ldap_connection:
    from gluon.contrib.login_methods.ldap_auth import ldap_auth
    ## configure auth policy
    print('Debug : There is an ldap_connection')
    auth.settings.create_user_groups=False
    auth.settings.actions_disabled=[
            'register',
            'change_password',
            'request_reset_password',
            'retrieve_username',
            'profile',
            ]
    print('LDAP Available - So configuring for an LDAP Authentication for the ldap_base_dn: %s' % (param.ldap_base_dn,))
    auth.settings.remember_me_form = False
    auth.settings.login_methods=[ldap_auth(
                mode='ad', server=param.ldap_server,
                base_dn=param.ldap_base_dn,
                secure=True,
                )]

else:
    auth.settings.registration_requires_verification = True
#    auth.settings.registration_requires_approval = True
    auth.settings.reset_password_requires_verification = True
#    auth.settings.create_user_groups=False

if auth.user:
    # fullname="%(first_name)s %(last_name)s" % auth.user
    fullname="%(username)s" % auth.user
else:
    fullname="Unknown"

def ad_group():
    """docstring for ad_group"""
    ad_group = param.ldap_allowed_user_group
    if param.ldap_authentication:
        gr = ad_group + ',' + param.ldap_base_group
        return gr in ldap_connection.getDetails(auth.user.username)['memberOf']
    else:
        # Do not filter access based on group if ldap not used.
        return True

#session.secure()
