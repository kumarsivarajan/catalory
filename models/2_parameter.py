# coding: utf8
# Parameter table
db.define_table('parameter',
        Field('profile_name',
            comment='Profile name, also displayed in the profile selection list.'),
        Field('allowed_admins', type='list:string',
              comment='DO NOT remove yourself!',
              default=''),
        Field('session_expiration', type='integer',
            default=900,
            comment=T('PCI requests 900s or less on produciton systems')),
        Field('email_sender', default='catalory@mydomain.com'),
        Field('email_server', default='smtp'),
        Field('email_port', type='integer', default=25),
        Field('ldap_authentication', type='boolean',
            comment='Enable if you want to use LDAP authentication'),
        Field('ldap_url', default='ldap://dc:389',
            comment='Example : ldaps://myldapserver:636'),
        Field('ldap_server', default='dc',
            comment='Server used for authentication (group is checked with the ldap_url)'),
        Field('ldap_username',
            comment=T('Username to connect to LDAP in order to browse groups.')),
        Field('ldap_password', type='password',
            comment=T('Password to connect to LDAP in order to browse groups.')),
        Field('ldap_base_dn',
            comment=T('Used both for authentication & group check')),
        Field('ldap_base_group',
            comment=T('Base group for all groups of the organization')),
        Field('ldap_allowed_user_group',
            comment=T('It\'s concatenated with the Ldap Base Group to have the full group DN')),
        Field('business_units', type='list:string', comment=T('A logical element or segment of a company (such as accounting, production, marketing) representing a specific business function, and a definite place on the organizational chart, under the domain of a manager. Also called department, division, or a functional area.'),
            default=['All', 'Accounting', 'Marketing', 'Production',]),
        Field('service_owners', type='list:string', comment=T('The Service Owner is responsible for delivering a particular service within the agreed service levels.'),
            default=['Unknown', 'IT - Win & Comm', 'IT - Unix & Network', 'IT - Service Desk', 'IT - Database Administration', 'IT - Core business application1 Support'],),
        Field('default_service_hours', default='Monday–Friday 08:00 to 18:00 except public holidays',),
        Field('device_roles', type='list:string', comment=T('Available roles for devices'),
            default=['Unknown', 'Server', 'Laptop', 'Firewall', 'Router', 'Switch', 'Switch/Router', 'FC Switch', 'Storage', 'Virtualization Host', 'Management Module', 'Desktop PC', 'Thin client', 'Phone', 'Backup', 'Printer', 'Security Cam', 'Adapter', 'Other', 'Unknown'],),
        Field('device_locations', type='list:string', comment=T('Available locations for devices'), default=['Main IT Room',]),
        Field('device_backup_profiles',
            type='list:string',
            default=['Daily', 'Weekly', 'Monthly', 'Image on change'],
            comment=T('Available backup profiles for devices')),
        Field('device_os',
            type='list:string',
            default=['Windows 2008 R2', 'Windows', 'Linux Debian/Ubuntu', 'Linux RedHat/Oracle/CentOS', 'Linux Other', 'Linux Embeded', 'Unknown', 'Other'],
            comment=T('Available operating systems for devices')),
        auth.signature,
        )
        
db.define_table('parameter_archive',
        db.parameter,Field(
            'current_record',
            'reference parameter',
            readable=False,
            writable=False,
            )
        )

if session.profile_id:
    try:
        param = Storage(db(db.parameter.id==session.profile_id).select().first())
    except TypeError:
        # Can happen if the parameter profile you're using has been deleted.
        session.flash=T('Invalid profile - switch back to first available.')
        try:
            param = Storage(db(db.parameter).select().first())
        except TypeError:
            db.parameter.insert(profile_name='default')
            param = Storage(db(db.parameter).select().first())
else:
    try:
    	param = Storage(db(db.parameter).select().first())
    except TypeError:
        # Enter an empty profile :
        db.parameter.insert(profile_name='default')
    	param = Storage(db(db.parameter).select().first())

session.profile_id = param.id


db.parameter.profile_name.requires = IS_LENGTH(15)

mail.settings.server = param.email_server
mail.settings.sender = param.email_sender
mail.settings.login = settings.email_login
mail.settings.tls = False


