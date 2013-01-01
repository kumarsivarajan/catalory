# -*- coding: utf-8 -*-
### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
### end requires
def error():
    return dict()

def get_device_ips(row):
    r = db(
      (db.t_device2ip.f_device_id==row.id) 
      & (db.t_device2ip.f_ip_id==db.t_ip.id)
      ).select(
        db.t_ip.id,db.t_ip.f_ip_addr,db.t_device2ip.f_type,
      ).as_list()
    ip_lst = list()
    for x in r:
        disp = x['t_device2ip']['f_type'][0:3] + ' ' + x['t_ip']['f_ip_addr']
        ip_lst.append(
              P(A(disp, _href=URL('default', 'ip_manage/t_ip/view/t_ip', args=[x['t_ip']['id'],], user_signature=True)))
        )
    return (ip_lst)

def check_unique_primary(form):
    if (form.vars.f_type == 'Primary' and 
            db((db.t_device2ip.f_device_id==int(form.vars.f_device_id)) & (db.t_device2ip.f_type=='Primary')).count() > 0):
        ips = db(
                (db.t_device2ip.f_device_id==int(form.vars.f_device_id))
                & (db.t_device2ip.f_type=='Primary')
                & (db.t_ip.id == db.t_device2ip.f_ip_id)
                ).select(db.t_ip.f_ip_addr).as_list()
        ip_list = [i['f_ip_addr'] for i in ips]
        form.errors.f_type = 'Primary IP existing for this device: %s' % '|'.join(ip_list),

def get_devices(row):
    r = db(
      (db.t_device2ip.f_ip_id==row.id) 
      & (db.t_device2ip.f_device_id==db.t_device.id)
      ).select(
        db.t_device.id,db.t_device.f_hostname,
      ).as_list()
    return ([P(A(x['f_hostname'], _href=URL('default', 'device_manage/t_device/view/t_device', args=[x['id'],], user_signature=True))) for x in r])

#@auth.requires(auth.is_logged_in() and ad_group(), requires_login=True)
def service_notif(row):
    ir = db((db.t_notification.f_services.contains(row.id)) 
          & (db.t_notification.f_type=='Incident Report')).count()
    maintenance = db((db.t_notification.f_services.contains(row.id)) 
          & (db.t_notification.f_type=='Maintenance Notification')).count()
    general = db((db.t_notification.f_services.contains(row.id)) 
          & (db.t_notification.f_type=='General Notification')).count()
    total = ir + maintenance + general
    return P(
          A(str(ir)+' IR', _href=URL('manage_notification', vars={'f_type': 'ir', 'sid': row.id})),' + ',
          A(str(maintenance)+' M', _href=URL('manage_notification', vars={'f_type': 'maintenance', 'sid': row.id})),' + ',
          A(str(general)+' G', _href=URL('manage_notification', vars={'f_type': 'general', 'sid': row.id})),' = ',
          A(str(total)+' N', _href=URL('manage_notification', vars={'f_type': 'all', 'sid': row.id})), 
          )

# Business Service Catalogue
def index():
    form = SQLFORM.smartgrid(
          db.t_bsc,
          onupdate=auth.archive,
          linked_tables=['t_bsc', 't_device', 't_device2ip', 't_ip', 't_ip2port', 't_port' ,],
          fields=[
            db.t_bsc.f_name,
            db.t_bsc.f_service_type,
            db.t_bsc.f_service_category,
            db.t_bsc.f_business_units,
            db.t_bsc.f_service_owner,
            db.t_bsc.f_business_priority,
            db.t_device.f_hostname,
            db.t_device.f_role,
            db.t_device.f_pci_scope,
          ],
          links={'t_bsc':[{'header':'Service Notifications', 'body':service_notif}]},
    )
    plugin=plugin_multiselect(db.t_bsc.f_supporting_svc)
    return locals()



@auth.requires(auth.is_logged_in() and ad_group(), requires_login=True)
def device_manage():
    form = SQLFORM.grid(db.t_device,
          onupdate=auth.archive,
          fields=[
                db.t_device.created_by,
                db.t_device.modified_by,
                db.t_device.f_hostname,
                db.t_device.f_role,
                db.t_device.f_location,
                db.t_device.f_pci_scope,
                db.t_device.f_os,
                db.t_device.f_backup_profile,
                db.t_device.f_owner,
                db.t_device_archive.created_by,
                db.t_device_archive.modified_by,
                db.t_device_archive.f_hostname,
                db.t_device_archive.f_role,
                db.t_device_archive.f_location,
                db.t_device_archive.f_pci_scope,
                db.t_device_archive.f_os,
                db.t_device_archive.f_backup_profile,
                db.t_device_archive.f_owner,
                db.t_device2ip.f_type,
                db.t_ip.f_dns_name,
                db.t_ip.f_ip_addr,
                ],
          deletable=True,
          paginate=100,
          maxtextlength=20,
          links=[{'header':'IP Addresses', 'body':get_device_ips},],
          #onvalidation={'t_device2ip': check_unique_primary },
          )
    return locals()
    
@auth.requires(auth.is_logged_in() and ad_group(), requires_login=True)
def device2ip_manage():
    if request.vars.preselectedipid:
        db.t_device2ip.f_ip_id.default=request.vars.preselectedipid


    form = SQLFORM.smartgrid(
            db.t_device2ip,
            onupdate=auth.archive,
            onvalidation=check_unique_primary,
            user_signature=False,
            )
    return locals()

@auth.requires(auth.is_logged_in() and ad_group(), requires_login=True)
def ip_manage():
    form = SQLFORM.smartgrid(
      db.t_ip,onupdate=auth.archive,
      links=[{'header':'Belongs to', 'body': get_devices},],
      linked_tables=['t_bsc', 't_device', 't_device2ip', 't_ip', 't_ip2port', 't_port' ,],
      paginate=100,
      onvalidation=check_unique_primary,
    )
    return locals()

@auth.requires(auth.is_logged_in() and ad_group(), requires_login=True)
def ip2port_manage():
    form = SQLFORM.smartgrid(db.t_ip2port,onupdate=auth.archive,
    maxtextlengths={'t_ip2port.f_ip_id':50},)
    return locals()

@auth.requires(auth.is_logged_in() and ad_group(), requires_login=True)
def port_manage():
    form = SQLFORM.smartgrid(db.t_port,onupdate=auth.archive)
    return locals()

def notification_validate(form):
    if form.vars.f_status=='To be sent on submit':
        # Gathering informations to send email:
        # List of emails, and list of services to
        # make the subject
        recipients = list()
        services = list()
        for s in form.vars.f_services:
            res = db(db.t_bsc.id==s).select().first()
            recipients += res.f_contacts
            services.append(res.f_name)
        if mail.send(to=recipients,
                subject='[' + form.vars.f_type + '] for the services: ' + ','.join(services),
                message=form.vars.f_message):
            #message=MARKMIN(form.vars.f_message))
            form.vars.f_status='Sent'
        else:
            form.vars.f_status='Error sending notification'
        # Still missing a way to do this:
        #response.flash = 'Sending eMail from here'
        #I must ask support in forum.

@auth.requires(auth.is_logged_in() and ad_group(), requires_login=True)
def manage_notification():
    if (bool(request.vars.f_type) & bool(request.vars.sid)):
        if request.vars.f_type=='all':
            form = SQLFORM.grid(
                  (db.t_notification.f_services.contains(request.vars.sid)),
                  onvalidation=notification_validate,
                  fields=[db.t_notification.f_type, db.t_notification.f_time, db.t_notification.f_duration, db.t_notification.f_services, db.t_notification.f_status],
                  )
        elif request.vars.f_type=='maintenance':
            form = SQLFORM.grid(
                  ((db.t_notification.f_type=='Maintenance Notification') & (db.t_notification.f_services.contains(request.vars.sid))),
                  onvalidation=notification_validate,
                  fields=[db.t_notification.f_type, db.t_notification.f_time, db.t_notification.f_duration, db.t_notification.f_services, db.t_notification.f_status],
                  )
        elif request.vars.f_type=='ir':
            form = SQLFORM.grid(
                  ((db.t_notification.f_type=='Incident Report') & (db.t_notification.f_services.contains(request.vars.sid))),
                  onvalidation=notification_validate,
                  fields=[db.t_notification.f_type, db.t_notification.f_time, db.t_notification.f_duration, db.t_notification.f_services, db.t_notification.f_status],
                  )
    else:
        form = SQLFORM.grid(
              db.t_notification,
              onvalidation=notification_validate,
              fields=[db.t_notification.f_type, db.t_notification.f_time, db.t_notification.f_duration, db.t_notification.f_services, db.t_notification.f_status],
              )
    return locals()


def help():
    """ this controller returns a dictionary rendered by the view
        it lists all wiki pages
    >>> index().has_key('pages')
    True
    """
    response.generic_patterns = ['html', 'pdf', 'json']
    pages = db().select(db.page.id,db.page.title,db.page.body,
        orderby=db.page.position)
    return dict(pages=pages)

@auth.requires(auth.is_logged_in() and ad_group(), requires_login=True)
def create():
    "creates a new empty wiki page"
    response.generic_patterns = ['html']
    form = crud.create(db.page, next=URL('help'))
    return dict(form=form)

@auth.requires(auth.is_logged_in() and ad_group(), requires_login=True)
def edit():
    "edit an existing wiki page"
    response.generic_patterns = ['html']
    this_page = db.page(request.args(0)) or redirect(URL('help'))
    form = crud.update(db.page, this_page,
              next=URL('help'))
    return dict(form=form)

@auth.requires(auth.is_logged_in() and ad_group(), requires_login=True)
def manage_parameters():
    crud.settings.update_deletable = False
    if ((auth.user.username=='pivert') | (auth.user.username in param.allowed_admins)):
        form = crud.update(db.parameter, 1)
    else:
        form = crud.read(db.parameter, 1)
    return locals()

#@auth.requires(auth.is_logged_in() and 
#        auth.user.username in param.allowed_admins, 
#        requires_login=True)
#@auth.requires(auth.is_logged_in() and ad_group(), requires_login=True)
#def duplicate():
#    """docstring for Duplicate"""
#    row=db(db.parameter.id==request.args[0]).select().as_list()
#    del(row[0]['id'])
#    if re.search('\d$', row[0]['profile_name']):
#        row[0]['profile_name'] = row[0]['profile_name'][:-1] + \
#                str(int(row[0]['profile_name'][-1]) + 1)
#    else:
#        row[0]['profile_name'] += '1'
#    db.parameter.bulk_insert(row)
#    session.flash=T('Paramters duplicated')
#    redirect(URL('manage_parameters'))


@auth.requires(auth.is_logged_in() and ad_group(), requires_login=True)
def orphan_ip():
    ips_with_device=db(db.t_ip.id==db.t_device2ip.f_ip_id)._select(db.t_ip.id)
    rows = db(
              ~db.t_ip.id.belongs(ips_with_device)
          ).select(db.t_ip.id, db.t_ip.f_ip_addr, db.t_ip.f_dns_name)
    ip_lst= list()
    ip_lst.append(TR(TH('IP Address'), TH('DNS Name')))
    for row in rows:
        ip_lst.append(TR(
            TD(row.f_ip_addr),
            TD(row.f_dns_name),
            TD(A('Link to a device', _href=URL('default','device2ip_manage/t_device2ip/new/t_device2ip', vars={'preselectedipid': row.id,}))),
            ))
    form = TABLE(ip_lst)
    return dict(form=form)

#@auth.requires(auth.is_logged_in() and ad_group(), requires_login=True)
#def ip_range():
#    form = SQLFORM.smartgrid(db.t_range,onupdate=auth.archive)
#    return locals()

@auth.requires(auth.is_logged_in() and ad_group(), requires_login=True)
def network_discovery(): 
    if schedulerdb(schedulerdb.scheduler_worker.status=='ACTIVE').count()<1:
        response.flash('Warning, there is no active Worker')
        warning = MARKMIN('''
                ## No Worker
                There is no active Worker.
                This means that you can queue new scan jobs, but they will never be ran 
                as long as there is no active worker.

                In order to fix that, please run in the web2py folder:
                <code>
                python web2py.py -K catallory
                </code>
                (if catallory is the name of installed app)
        ''')
    ip_range_form = SQLFORM.grid(db.t_range,onupdate=auth.archive, csv=False)
    newscanform = FORM(
            INPUT(_type='submit', _value='Start a new scan for the selected ranges'),
            hidden=dict(rangelist='192.168.232.0/24'),
            )
    if newscanform.process(message_onsuccess='New scans queued').accepted:
        scheduler.queue_task('scan',)

    queue = schedulerdb((schedulerdb.scheduler_task.status=='QUEUED') | (schedulerdb.scheduler_task.status=='ASSIGNED')).select(schedulerdb.scheduler_task.id).as_dict().keys()
    job_queued = 'There are %s jobs in Queue: %s' % (len(queue),' '.join([str(i) for i in queue]),)
    return locals()

@auth.requires(auth.is_logged_in() and ad_group(), requires_login=True)
def scan_history():
    import gluon.contrib.simplejson as sj
    def scan_new_ips(row):
        try:
            s = schedulerdb(schedulerdb.scheduler_run.id==row.id).select(schedulerdb.scheduler_run.result).first().result
            return len(sj.loads(s)[u'ip_discovered'])
        except TypeError:
            return 'NA'

    def scan_updated_ips(row):
        try:
            s = schedulerdb(schedulerdb.scheduler_run.id==row.id).select(schedulerdb.scheduler_run.result).first().result
            return len(sj.loads(s)[u'ip_updated'])
        except TypeError:
            return 'NA'

    scan_history = SQLFORM.grid(schedulerdb.scheduler_run,
            fields=[
                schedulerdb.scheduler_run.id, schedulerdb.scheduler_run.start_time, schedulerdb.scheduler_run.stop_time, schedulerdb.scheduler_run.status, ],
            headers={'scheduler_run.id': 'Job ID'},
            orderby=[~schedulerdb.scheduler_run.id],
            paginate=6,
            deletable=False,
            editable=False,
            formname='scheduler_grid',
            csv=False,
            create=False,
            searchable=False,
            links=[{'header':'New IPs', 'body':scan_new_ips}, {'header':'Updated IPs', 'body': scan_updated_ips}],
            )
    return locals()
