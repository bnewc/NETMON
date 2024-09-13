import services


class ServiceMonitor:
    """Monitor class to maintain list of checks"""

    def __init__(self):
        self._http = []
        self._https = []
        self._icmp = []
        self._dns = []
        self._ntp = []
        self._tcp = []
        self._udp = []
        self._echo_server = []
        self._checks = []
        self._services = {
            "HTTP": (self._http, services.HTTP),
            "HTTPS": (self._https, services.HTTPS),
            "ICMP": (self._icmp, services.ICMP),
            "DNS": (self._dns, services.DNS),
            "NTP": (self._ntp, services.NTP),
            "TCP": (self._tcp, services.TCP),
            "UDP": (self._udp, services.UDP),
            "Echo": (self._echo_server, services.Echo),
        }
        self._service_lookup = [service for service in self._services]
        self._config = {}

    def convert_checks_dict(self):
        """Turn self._checks into a dictionary"""
        checks_dict = {}
        for check in self._checks:
            # Add list for service type
            if check.type not in checks_dict:
                checks_dict[check.type] = []
            # Add dictionary of attributes for specific check
            checks_dict[check.type].append(check.__dict__)
        return checks_dict

    def set_checks_from_dict(self, checks_dict):
        """Unpack checks dictionary and store in checks_list"""
        for service in self._services.values():
            # Clear current list of checks for service
            service[0].clear()
        for check_type, check_list in checks_dict.items():
            # Initialize check object
            for check_dict in check_list:
                check = self._services[check_type][1]()

                # Transfer dict attr values to check object
                for attr, val in check_dict.items():
                    setattr(check, attr, val)

                # Add check to respective service list and master checks list
                self._services[check_type][0].append(check)
                self._checks.append(check)

    def get_checks(self):
        return self._checks


def main():
    pass


if __name__ == '__main__':
    main()
