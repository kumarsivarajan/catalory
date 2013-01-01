#!/usr/bin/env python
def scan(db):
    import nmap
    from datetime import datetime
    #Define IP list and Port List
    ip_lst = [row.f_ip_range for row in db(db.t_range.f_scan == True).select()]
    port_lst = [str(row.f_number) for row in db(db.t_port.f_scan == True).select()]
    #Set ip_discovered to 0
    ip_discovered = 0
    #Scan All
    nm = nmap.PortScanner()
    print(' '.join(ip_lst), ','.join(port_lst))
    nm.scan(' '.join(ip_lst), ','.join(port_lst), arguments='--system-dns')
    #Print
    print('Analysing data')
    for host in nm.all_hosts():
        if nm[host]['status']['state'] != u'down':
            if len(db(db.t_ip.f_ip_addr == host).select()) == 0:
                print('Discovered Host : %s Details : %s' % (host, nm[host]))
                db.t_ip.insert(f_ip_addr=host, f_dns_name=nm[host]['hostname'], f_last_seen=datetime.now())
                ip_discovered += 1
            else:
                print('Updating last seen for host : %s Details : %s' % (host, nm[host]))
                db(db.t_ip.f_ip_addr == host).update(f_last_seen=datetime.now())

            for port in nm[host]['tcp']:
                if nm[host]['tcp'][port]['state'] != u'closed':
                    port_id = db(db.t_port.f_number == port).select().first().id
                    ip_id = db(db.t_ip.f_ip_addr == host).select().first().id
                    if db(
                          (db.t_ip2port.f_ip_id == ip_id) & 
                          (db.t_ip2port.f_port_id == port_id)
                          ).count() == 0:
                          db.t_ip2port.insert(f_ip_id = ip_id, 
                                              f_port_id = port_id, 
                                              f_last_seen = datetime.now())
                    else:
                        db(
                          (db.t_ip2port.f_ip_id == ip_id) & 
                          (db.t_ip2port.f_port_id == port_id)
                          ).update(f_last_seen = datetime.now())

    db.t_scan_history.insert(f_ip_range=' '.join(ip_lst), f_ip_discovered=ip_discovered, f_datetime=datetime.now())
