### we prepend t_ to tablenames and f_ to fieldnames for disambiguity

########################################

########################################

db.define_table('t_bsc',
    Field('f_name', type='string',
          label=T('Service name'),
          comment=T('The name of the customer facing service as known to your customer.')),
    Field('f_service_description', type='text',
          label=T('Service description'),
          represent = lambda descr,row: MARKMIN(descr),
          comment=T('A basic description of what the service does, and what the deliverables and outcomes are.'),),
    Field('f_service_type', type='string',
          label=T('Service type'),
          requires=IS_IN_SET(('Application service', 'Technical service', 'Professional Service',))),
    Field('f_service_category', type='string',
          label=T('Service category'),
          requires=IS_IN_SET(('Business service', 'Supporting service',)),
          comment=MARKMIN('''
          **Business services** are characterized by representing a direct value to customers, like e.g. the provision of e-mailing facilities and internet access.

          **Supporting services**, in contrast, are not of direct value to customers but are needed as building blocks for business services. Providing a network infrastructure, for example, would be a supporting service which is required to offer internet access for customers. '''
          ),),
    Field('f_supporting_svc', type='list:string',
          label=T('Supporting services'),
          comment=MARKMIN('''
          **List any supporting services**
          
          A supporting service is an IT service that is **not directly used by the
          business**, but is required by the IT service provider to deliver customer-
          facing services (for example, a directory service or a backup service).
          Supporting services may also include IT services only used by the IT
          service provider.
          Also include information about the supporting service(s) relationship to
          the customer-facing services
          '''),
          requires=IS_IN_DB(db,'t_bsc.f_name','%(f_name)s',multiple=True),
          ),
    Field('f_business_owner', type='list:string',
          label=T('Business owner(s)'),
          comment=MARKMIN('''**Business Owner** is not an ITIL requirement, but in our case he(they) represent(s) the person(s) able to take decisions on the availability, proposed choices and cost of a service. He is also the main beneficiary.'''),
          ),
    Field('f_business_units', type='string',
          label=T('Business unit(s)'),
          requires=IS_IN_SET(db(db.parameter.business_units).select().first().business_units),
          comment=MARKMIN('A **business unit** is a segment of the business that has its own plans,metrics, income and costs.')

          ),
    Field('f_service_owner', type='string',
          requires=IS_IN_SET(db(db.parameter.service_owners).select().first().service_owners),
          label=T('Service Owner'),
          comment=T('The Service Owner is responsible for delivering a particular service within the agreed service levels.'),),
    Field('f_business_impact', type='text',
          label=T('Business Impact'),
          comment=MARKMIN('''
                **Should be filled by Business for Business Services**
                Describe what would be the impact of not having this service available.
                Business impact is typically based on the number of users affected, the
                duration of the downtime, the impact on each user, and the cost to the
                business (if known).
                It may be easier to describe the positive business impact of the service
                being available.'''),),
    Field('f_business_priority', type='string',
          label=T('Business priority'),
          comment=MARKMIN('''
                **Should be filled by Business for Business Services**
                ----------------------------------------------------------------------
                **Priority** | **Business impact in case of failure of more than 50%**
                ======================================================================
                Very high    |Major impact on business 
                High         |Impact on business        
                Medium       |Noticeable impact on business, limited costs 
                Low          |Minor impact, very limited cost
                Very low     |No business impact, very low cost
                ----------------------------------------------------------------------
          '''),
          requires=IS_IN_SET(('Very high', 'High', 'Medium', 'Low', 'Very low')),
          ),
    Field('f_sla', type='text',
          label=T('Service Level'),
          comment='''
This can be a hyperlink to the full SLA
An SLA is an agreement between an IT service provider and a
customer. It describes the IT service, documents service level targets,
and specifies the responsibilities of the IT service provider and the
customer. A single agreement may cover multiple IT services or multiple
customers or may be a corporate SLA covering many services and
customers.''',
          ),
    Field('f_service_hours', type='string',
          label=T('Service hours'),
          default=param.default_service_hours,
          comment='''
For example, ‘Monday–Friday 08:00 to 18:00 except public holidays’.
Defined as an agreed time period when a particular IT service should be
available. The service hours will also be defined in the service level
agreement.
          ''',),
    Field('f_howtoget',
          label=T('How to get the service')),
    Field('f_howlong', 
          label=T('Delivery time')),
    Field('f_contacts',
          type='list:string',
          label=T('Service Contacts'),
          requires=IS_LIST_OF(IS_EMAIL(error_message='invalid email!')),
          comment='''
MANDATORY : List eMails or groups that must be notified about service maintenances, issues & unavailability risks.
          ''',),
    auth.signature,
    format='%(f_name)s',
    singular='Service',
    migrate=settings.migrate)


db.define_table('t_device',
    Field('f_hostname', type='string',
          label=T('Hostname')),
    Field('f_role', type='string',
          requires=IS_IN_SET(db(db.parameter.device_roles).select().first().device_roles),
          label=T('Role')),
    Field('f_service_id', type='reference t_bsc',
          label=T('Service member')),
    Field('f_description', type='string',
          label=T('Description')),
    Field('f_location', type='string',
          requires=IS_IN_SET(db(db.parameter.device_locations).select().first().device_locations),
          label=T('Location'),
          comment=T('Physical Hardware Location')),
    Field('f_pci_scope', type='boolean',
          label=T('Pci')),
    Field('f_confidential_data', type='boolean',
          label=T('Confidential Data'),
          comment=T('Stores & contains confidential data (Check PCI & CSSF)')),
    Field('f_operational_status', type='string', 
          requires=IS_IN_SET(('Production', 'Test', 'Development', 'Backup', 'Decomissioned')),
          label=T('Operational Status')),
    Field('f_backup_profile', type='string',
          requires=IS_IN_SET(db(db.parameter.device_backup_profiles).select().first().device_backup_profiles),
          label=T('Backup')),
    Field('f_os', type='string',
          label=T('Os'),
          requires=IS_IN_SET(db(db.parameter.device_os).select().first().device_os),
          comment=T('Operating System')),
#    Field('f_serial_nr', type='string',
#          label=T('Serial Nr'),
#          comment=T('Hardware Serial Number')),
#    Field('f_product_nr', type='string',
#          label=T('Product Nr'),
#          comment=T('Hardware Product Number')),
    Field('f_owner', type='string',
          label=T('Owner'),
          comment=T('The device owner is responsible of the management of the server & installed software.'),),
    Field('f_install_dte', type='date',
          label=T('Install Date'),
          comment=T('System installation date')),
          
    Field('f_maint_expiry', type='date',
          label=T('Maint Expiry'),
          comment=T('Hardware Warranty Expiration Date')),
    Field('f_comment', type='text',
          label=T('Comment')),
    auth.signature,
    format=lambda x: A(str(x.f_hostname), _href=URL('device_manage/t_device/view/t_device/%s' % x.id)),
    singular='Device',
    migrate=settings.migrate)

db.define_table('t_device_archive',db.t_device,
        Field('current_record','reference t_device',readable=False,writable=False),
        Field('modified_by', readable=True),
        Field('created_by', readable=True),
        singular='Device Archive')

########################################
db.define_table('t_ip',
    Field('f_dns_name', type='string',
          label=T('DNS Name')),
    Field('f_ip_addr', type='string',
          requires=IS_IPV4(),
          unique=True,
          label=T('IP Address'),
          ),
    Field('f_mac_addr', type='string',
          label=T('MAC Address')),
    Field('f_last_seen', type='datetime',
          label=T('Last Seen')),
    auth.signature,
    format=lambda x: A(str(x.f_ip_addr), _href=URL('ip_manage/t_ip/view/t_ip/%s' % x.id)),
    singular = 'IP',
    plural = 'IP',
    migrate=settings.migrate)

db.define_table('t_ip_archive',db.t_ip,Field('current_record','reference t_ip',
      readable=False,writable=False), singular='IP Archive')

########################################       
db.define_table('t_device2ip',
    Field('f_device_id', type='reference t_device',
          label=T('Device'),
          comment='Type the first 3 letters, and it will search in the device list'),
    Field('f_ip_id', type='reference t_ip',
          label=T('IP')),
    Field('f_type', type='string',
          requires=IS_IN_SET(('Primary', 'Secondary', 'HA', 'DNAT', 'Management', 'Unknown', 'Other')),
          label=T('Type')),
    Field('f_interface', type='string',
          label=T('Interface')),
    auth.signature,
#    format='%(f_)s',
    singular = 'Device-IP',
    plural = 'Device-IP',
    migrate=settings.migrate)
db.t_device2ip.f_device_id.widget = SQLFORM.widgets.autocomplete(
     request, db.t_device.f_hostname, id_field=db.t_device.id, orderby=db.t_device.f_hostname)
db.define_table('t_device2ip_archive',db.t_device2ip,Field('current_record','reference t_device2ip',readable=False,writable=False))
########################################       

db.define_table('t_port',
    Field('f_number', type='integer',
          comment='i.e. 80',
          label=T('Port Number')),
    Field('f_service', type='string',
          comment='i.e. http',
          label=T('Service Associated')),
    Field('f_secure', type='boolean',
          label=T('Secure'),
          comment=T('Check this if the service that use this port is secure')),
    Field('f_scan', type='boolean',
          default=True,
          label=T('Scan'),
          comment=T('Check to include in scan')),
    auth.signature,
    format='%(f_number)s',
    singular = 'Port',
    migrate=settings.migrate)
          
db.define_table('t_port_archive',db.t_port,Field('current_record','reference t_port',readable=False,writable=False))

########################################       
db.define_table('t_ip2port',
    Field('f_ip_id', type='reference t_ip',
          label=T('IP')),
    Field('f_port_id', type='reference t_port',
          label=T('Port')),
    Field('f_last_seen',
          type='datetime',
          label='Last seen',),
    auth.signature,
    singular = 'IP-Port',
    migrate=settings.migrate)

db.define_table('t_ip2port_archive',db.t_ip2port,Field('current_record','reference t_ip2port',readable=False,writable=False))

########################################       
db.define_table('t_range',
    Field('f_ip_range', type='string',
          requires=IS_MATCH('^([0-2]?[0-9]{1,2}\.){3}[0-2]?[0-9]{1,2}(\/[0-3]?[0-9])?$', error_message='Please enter a valid IP range'),
          label=T('IP Range')),
    Field('f_scan', type='boolean',
          default=True,
          label=T('Scan')),
    auth.signature,
    migrate=settings.migrate)
   
########################################  

db.define_table('t_notification',
    Field('f_subject', readable=False, writable=False),
    Field('f_type', 
          label='Type',
          requires=IS_IN_SET(('Maintenance Notification', 'General Notification', 'Incident Report'))),
    Field('f_time', type='datetime',
          label='Date & Time',
          comment='Date & Time of the start of the incident or planned maintenance'),
    Field('f_duration', type='integer',
          label='Duration [minutes]',
          comment='Duration (in minutes) of the incident or planned duration of the service perturbations during maintenance'),
    Field('f_message', type='text', label='Message',
          comment='You can use the MARKMIN Syntax',
          represent = lambda msg,row: MARKMIN(msg),),
    Field('f_services', type='list:reference t_bsc',
          label='Services'),
    Field('f_status', 
          requires=IS_IN_SET(('Draft', 'To be sent on submit', 'Sent')),
          default='Draft',
          label='Status',
          ),)
########################################  
#
#db.define_table('t_service2notification',
#    Field('f_service_id',
#          type='reference t_service',
#          label='Service'),
#    Field('f_notification_id',
#          type='reference t_notification',
#          label='Notification'))

########################################  
db.define_table('t_scan_history',
    Field('f_ip_range', type='string',
          comment='i.e. 192.168.0.0/24',
          label=T('IP Range')),
    Field('f_datetime', type='datetime',
          label=T('Date Time')),
    Field('f_ip_discovered', type='integer',
          label=T('IP Discovered')),
    auth.signature,
    singular = 'Scan',
    migrate=settings.migrate)
         
########################################
db.define_table('page',
    Field('title'),
    Field('body', 'text'),
    Field('position', 'integer', readable=False, default=100),
    Field('created_on', 'datetime', default=request.now),
    Field('created_by', db.auth_user, default=auth.user_id),
    format='%(title)s')
db.page.title.requires = IS_NOT_IN_DB(db, 'page.title')
db.page.body.requires = IS_NOT_EMPTY()
db.page.created_by.readable = db.page.created_by.writable = False
db.page.created_on.readable = db.page.created_on.writable = False
