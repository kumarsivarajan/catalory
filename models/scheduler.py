from gluon.scheduler import Scheduler
scheduler = Scheduler(schedulerdb, discard_results=False,)
import scan

def scan():
    import nmap
    from datetime import datetime
    ip_lst = [row.f_ip_range for row in db(db.t_range.f_scan == True).select()]
    port_lst = [str(row.f_number) for row in db(db.t_port.f_scan == True).select()]
    #Set ip_discovered to 0
    ip_discovered = 0
    #Scan All
    nm = nmap.PortScanner()
    nm.scan(' '.join(ip_lst), ','.join(port_lst), arguments='--system-dns')
    ip_discovered = list()
    ip_updated = list()
    for host in nm.all_hosts():
        if nm[host]['status']['state'] != u'down':
            if len(db(db.t_ip.f_ip_addr == host).select()) == 0:
                db.t_ip.insert(f_ip_addr=host, f_dns_name=nm[host]['hostname'], f_last_seen=datetime.now())
                ip_discovered.append(str(host))
            else:
                db(db.t_ip.f_ip_addr == host).update(f_dns_name=nm[host]['hostname'], f_last_seen=datetime.now())
                ip_updated.append(str(host))

            # Updating f_last_seen in t_ip2port 
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
    return dict(ip_discovered=ip_discovered, ip_updated=ip_updated)
