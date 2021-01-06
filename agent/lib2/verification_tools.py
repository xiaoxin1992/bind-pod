import re
from IPy import IP


class Verification:
    @classmethod
    def is_domain(cls, domain):
        match = re.compile(r'^(?=^.{3,255}$)[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+$')
        return False if match.match(domain) is None else True

    @classmethod
    def is_ip(cls, ip, version=4):
        try:
            return True if IP(ip).version() == version else False
        except ValueError:
            return False

    @classmethod
    def is_full_domain(cls, domain):
        match = re.compile(
            r'^(([a-zA-Z])|([a-zA-Z][a-zA-Z])|'
            r'([a-zA-Z][0-9])|([0-9][a-zA-Z])|'
            r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
            r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})\.$'
        )
        return False if match.match(domain) is None else True
