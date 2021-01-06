import dns.update
import dns.query
import dns.resolver
import dns.tsigkeyring
import dns.zone
import dns.rdatatype
import logging
import dns.rdata
import dns.rdataclass
from dns.tsig import HMAC_MD5


class Dns:
    def __init__(self, server, key, code, domain, port=53, allow_type=None):
        if allow_type is None:
            allow_type = ('AAAA', 'A', 'NS', 'CNAME', 'TXT', 'MX')
        self.server = server
        self.port = port
        self.domain = domain
        secret = dns.tsigkeyring.from_text({"{}".format(key): "{}".format(code)})
        self.dns = dns.update.Update(domain, keyring=secret, keyalgorithm=HMAC_MD5)
        self.allow_type = allow_type

    def __dns_handle(self, *host, name, ttl, domain_type, action_type):
        if domain_type not in self.allow_type:
            logging.error("{domain} not support type {type}".format(domain=self.domain, type=domain_type))
            return False
        try:
            # mx记录 name必须为空，如果记录不是本域名的则需要写全部域名  例如 'mail.test.com.'
            dns_obj = dns.rdataset.from_text("IN", domain_type, ttl, *host)
            if action_type == "create":
                self.dns.add(name, dns_obj)
            elif action_type == "replace":
                self.dns.replace(name, dns_obj)
            elif action_type == "delete":
                self.dns.delete(name, dns_obj)
            else:
                logging.debug("action error [create, replace, delete]")
                return False
            logging.debug(
                "{domain} {action} analysis {name} success!".format(domain=self.domain, action=action_type, name=name))
            return True
        except Exception as e:
            # 域名类型或者主机IP非法, 请检查, 删除操作可能记录不存在
            logging.error("{domain} {action} analysis {name} failure error: {error}".format(
                domain=self.domain, action=action_type, name=name, error=str(e)))
        return False

    def add(self, name, ttl, domain_type, host, mx=0):
        if domain_type.upper() in "MX":
            host = "{mx} {address}".format(address=host, mx=mx)
        if self.__dns_handle(host, name=name, ttl=ttl, domain_type=domain_type, action_type="create"):
            return self.__save()
        return False

    def replace(self, name, ttl, domain_type, *host):
        if self.__dns_handle(*host, name=name, ttl=ttl, domain_type=domain_type, action_type="replace"):
            return self.__save()
        return False

    def delete(self, name, domain_type, host, ttl=0):
        if self.__dns_handle(host, name=name, ttl=ttl, domain_type=domain_type, action_type="delete"):
            return self.__save()
        return False

    def __save(self):
        try:
            send_result = dns.query.tcp(self.dns, self.server, timeout=10, port=53)
            if send_result.rcode() == 0:
                logging.debug("analysis submit {server} server success!".format(server=self.server))
                return True
            elif send_result.rcode() == 5 and send_result.rcode() == 9:
                logging.error("analysis submit {server} server failure, key error or domain not exists".format(
                    server=self.server))
                return False
            else:
                logging.error("----------ERROR INFO----------")
                logging.error(send_result)
                logging.error("----------ERROR END----------")
                logging.error("analysis submit {server} server failure".format(server=self.server))
                return False
        except Exception as e:
            # 连接服务器失败，请检查服务器是否正常
            logging.error("Failed to connect to the server {server}:{port} error:{err}".format(
                server=self.server, port=self.port, err=str(e)))
            return False


class Zone:
    @classmethod
    def read(cls, config, domain):
        dns_domain_name_list = []
        try:
            dns_obj = dns.zone.from_file(config, domain)
        except (dns.zone.NoSOA, FileNotFoundError, PermissionError) as err:
            logging.error(str(err))
            return dns_domain_name_list
        for (name, ttl, data) in dns_obj.iterate_rdatas():
            allow_type = ('AAAA', 'A', 'NS', 'CNAME', 'TXT', 'MX')
            mx = 0
            host = "{}".format(data)
            if "{name}".format(name=data) == "@" or dns.rdatatype.to_text(data.rdtype) not in allow_type:
                continue
            if dns.rdatatype.to_text(data.rdtype) == "MX":
                mx, host = host.strip().split()
            dns_domain_name_list.append({
                "name": "{}".format(name),
                "ttl": int(ttl),
                "mx": mx,
                "type": "{}".format(dns.rdatatype.to_text(data.rdtype)),
                "ip": host
            })
        return dns_domain_name_list


if __name__ == '__main__':
    # a = Dns("127.0.0.1", "davidddns", "hpvLkDRozTdGSPRPB9s5/A==", domain="xiaoxin.com", port=53)
    # a.delete("test1000", "A", "10.10.10.30")
    z = Zone.read("/var/named/xiaohai.com.zone", "xiaohai.com")
