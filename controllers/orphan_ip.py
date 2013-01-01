# -*- coding: utf-8 -*-
### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
### end requires

def autocomplete_input(id):
    input_form = '''
          <input autocomplete="off" class="string" 
          id="t_device2ip_f_device_id" name="''' + str(id) + '''" 
          onblur="jQuery(&#x27;#_autocomplete_t_device_f_hostname_div&#x27;).delay(1000).fadeOut(&#x27;slow&#x27;);" 
          onkeyup="jQuery(&#x27;#_autocomplete_t_device_f_hostname_auto&#x27;).val(&#x27;&#x27;);
          var e=event.which?event.which:event.keyCode; function F_autocomplete_t_device_f_hostname(){jQuery(&#x27;
          #t_device2ip_f_device_id&#x27;).val(jQuery(&#x27;#_autocomplete_t_device_f_hostname :selected&#x27;).text());
          jQuery(&#x27;#_autocomplete_t_device_f_hostname_auto&#x27;).val(jQuery(&#x27;#_autocomplete_t_device_f_hostname&#x27;).val())};
          if(e==39) F_autocomplete_t_device_f_hostname();
          else if(e==40)
          {
            if(jQuery(&#x27;#_autocomplete_t_device_f_hostname option:selected&#x27;).next().length)jQuery(&#x27;#_autocomplete_t_device_f_hostname option:selected&#x27;).attr(&#x27;selected&#x27;,null).next().attr(&#x27;selected&#x27;,&#x27;selected&#x27;);
            F_autocomplete_t_device_f_hostname();
          } else if(e==38)
          {
            if(jQuery(&#x27;#_autocomplete_t_device_f_hostname option:selected&#x27;).prev().length)jQuery(&#x27;#_autocomplete_t_device_f_hostname option:selected&#x27;).attr(&#x27;selected&#x27;,null).prev().attr(&#x27;selected&#x27;,&#x27;selected&#x27;); 
            F_autocomplete_t_device_f_hostname();
          } else if(jQuery(&#x27;#t_device2ip_f_device_id&#x27;).val().length&gt;=2) jQuery.get(&#x27;/sinventory/default/device2ip_manage/t_device2ip/new/t_device2ip?_autocomplete_t_device_f_hostname=&#x27;+escape(jQuery(&#x27;#t_device2ip_f_device_id&#x27;).val()),function(data){if(data==&#x27;&#x27;)jQuery(&#x27;#_autocomplete_t_device_f_hostname_auto&#x27;).val(&#x27;&#x27;);else{jQuery(&#x27;#t_device2ip_f_device_id&#x27;).next(&#x27;.error&#x27;).hide();jQuery(&#x27;#_autocomplete_t_device_f_hostname_div&#x27;).html(data).show().focus();jQuery(&#x27;#_autocomplete_t_device_f_hostname_div select&#x27;).css(&#x27;width&#x27;,jQuery(&#x27;#t_device2ip_f_device_id&#x27;).css(&#x27;width&#x27;));jQuery(&#x27;#_autocomplete_t_device_f_hostname_auto&#x27;).val(jQuery(&#x27;#_autocomplete_t_device_f_hostname&#x27;).val());
          jQuery(&#x27;#_autocomplete_t_device_f_hostname&#x27;).change(F_autocomplete_t_device_f_hostname);jQuery(&#x27;#_autocomplete_t_device_f_hostname&#x27;).click(F_autocomplete_t_device_f_hostname);};}); 
          else jQuery(&#x27;#_autocomplete_t_device_f_hostname_div&#x27;).fadeOut(&#x27;slow&#x27;);" type="text" />
          <input id="_autocomplete_t_device_f_hostname_auto" name="f_device_id_''' + str(id) + '''" type="hidden" value="" />
          <div id="_autocomplete_t_device_f_hostname_div" style="position:absolute;"></div>'''
    return input_form

def index():
    ips_with_device=db(db.t_ip.id==db.t_device2ip.f_ip_id)._select(db.t_ip.id)
    rows = db(
              ~db.t_ip.id.belongs(ips_with_device)
          ).select(db.t_ip.id, db.t_ip.f_ip_addr, db.t_ip.f_dns_name)
    formlst = list()
    for row in rows:
        ip = '%s (%s)' % (row.f_ip_addr, row.f_dns_name)
        #formlst.append(TR(TD(ip), TD(INPUT(_name=row.id))))
        formlst.append(TR(TD(ip), TD(XML(autocomplete_input(row.id)))))
    formlst.append(TR(TD(' '), TD(INPUT(_type='submit'))))
    form = FORM(TABLE(formlst))
    results = ''
    if form.accepts(request,session):
        response.flash = 'form accepted'
        results=request.post_vars
    elif form.errors:
        response.flash = 'form has errors'
    return dict(form=form, results=results)
