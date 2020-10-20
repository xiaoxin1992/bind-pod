import dns.update
import dns.query
import dns.resolver
import dns.tsigkeyring
import dns.zone
import dns.rdatatype
import logging
import dns.rdata
import dns.rdataclass


class Bind:
    def __init__(self, server, key, code, domain, port=53, allow_type=None):
        self.server = server
        self.port = port
        self.domain = domain
        keyring = dns.tsigkeyring.from_text({'{}'.format(key): '{}'.format(code)})
        self.dns = dns.update.Update(domain, keyring=keyring)
        if allow_type is None:
            self.allow_type = ['AAAA', 'A', 'NS', 'CNAME', 'TXT', 'MX']
        else:
            self.allow_type = allow_type

    def add(self, name, ttl, domain_type, host):
        if domain_type not in self.allow_type:
            logging.error("{domain} not support type {type}".format(domain=self.domain, type=domain_type))
            return False
        try:
            # mx记录 name必须为空，如果记录不是本域名的则需要写全部域名  例如 'mail.test.com.'
            dns_obj = dns.rdataset.from_text("IN", domain_type, ttl, host)
            self.dns.add(name, dns_obj)
            logging.debug("{domain} create analysis {name} success!".format(domain=self.domain, name=name))
            return True
        except Exception as e:
            logging.error(
                "{domain} create analysis {name} failure error: {error}".format(domain=self.domain, name=name,
                                                                                error=str(e)))
            return False

    def replace(self, name, ttl, domain_type, *host):
        if domain_type not in self.allow_type:
            logging.error("{domain} not support type {type}".format(domain=self.domain, type=domain_type))
            return False
        try:
            # mx记录 name必须为空，如果记录不是本域名的则需要写全部域名  例如 'mail.test.com.'
            dns_obj = dns.rdataset.from_text("IN", domain_type, ttl, *host)
            self.dns.replace(name, dns_obj)
            logging.debug("{domain} create analysis {name} success!".format(domain=self.domain, name=name))
            return True
        except Exception as e:
            # 域名类型或者主机IP非法, 请检查
            logging.error(
                "{domain} create analysis {name} failure error:{error}".format(domain=self.domain, name=name,
                                                                               error=str(e)))
            return False

    def delete(self, name, domain_type, host, ttl):
        if domain_type not in self.allow_type:
            logging.error("{domain} not support type {type}".format(domain=self.domain, type=domain_type))
            return False
        try:
            # mx记录 name必须为空，如果记录不是本域名的则需要写全部域名  例如 'mail.test.com.'
            dns_obj = dns.rdataset.from_text("IN", domain_type, ttl, host)
            self.dns.delete(name, dns_obj)
            logging.debug("{domain} create analysis {name} success!".format(domain=self.domain, name=name))
            return True
        except Exception as e:
            # 域名类型或者主机IP非法, 请检查, 或域名不存在
            logging.error(
                "{domain} create analysis {name} failure error:{error}".format(domain=self.domain, name=name,
                                                                               error=str(e)))
            return False

    def save(self):
        try:
            send_result = dns.query.tcp(self.dns, self.server, timeout=10, port=self.port)
            if send_result.rcode() == 0:
                logging.debug("analysis submit {server} server success!".format(server=self.server))
                return True
            elif send_result.rcode() == 5:
                logging.error("analysis submit {server} server failure, please check key".format(server=self.server))
                return False
            elif send_result.rcode() == 9:
                logging.error("analysis submit {server} server failure, domain not exists".format(server=self.server))
                return False
            else:
                logging.error("----------ERROR INFO----------")
                logging.error(send_result)
                logging.error("----------ERROR END----------")
                logging.error("analysis submit {server} server failure".format(server=self.server))
                return False
        except Exception as e:
            # 连接服务器失败，请检查服务器是否正常
            logging.error(
                "Failed to connect to the server {server}:{port} error:{err}".format(server=self.server, port=self.port,
                                                                                     err=str(e)))
            return False


class DomainResolve:
    def __init__(self, config, domain, allow_type):
        self.config = config
        self.domain = domain
        self.allow_type = allow_type

    @property
    def resolve_list(self):
        dns_obj = dns.zone.from_file(self.config, self.domain)
        dns_domain_name_list = []
        for (name, ttl, data) in dns_obj.iterate_rdatas():
            if "{}".format(data) == "@":
                continue
            if dns.rdatatype.to_text(data.rdtype) in self.allow_type:
                dns_domain_name_list.append({
                    "name": "{}".format(name),
                    "ttl": int(ttl),
                    "type": "{}".format(dns.rdatatype.to_text(data.rdtype)),
                    "ip": "{}".format(data)
                })
        return dns_domain_name_list
