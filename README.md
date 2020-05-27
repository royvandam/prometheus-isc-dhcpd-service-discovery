# Prometheus DHCP service discovery

Generate Prometheus scrape configurations for multiple targets and jobs by parsing the ISC DHCP lease file. Supports lease filtering on hostname and MAC address.

```
usage: dhcpd-service-discovery.py [-h] [-j {name:port} [{name:port} ...]] [-l PATH] [-o PATH] [-m MAC [MAC ...]]
                                  [-n HOSTNAME [HOSTNAME ...]] [-p]

optional arguments:
  -h, --help            show this help message and exit
  -j {name:port} [{name:port} ...], --job {name:port} [{name:port} ...]
                        Jobs to configure, accepts multiple values (e.g. node:9100)
  -l PATH, --leases PATH
                        Path to dhcpd.leases file (default: /var/lib/dhcp/dhcpd.leases)
  -o PATH, --output PATH
                        Path to targets file (default: /etc/prometheus/targets.json)(- for stdout)
  -m MAC [MAC ...], --mac MAC [MAC ...]
                        Whitelist MAC address (note: accepts regex)
  -n HOSTNAME [HOSTNAME ...], --hostname HOSTNAME [HOSTNAME ...]
                        Whitelist hostname (note: accepts regex)
  -p, --print           Print active DHCP leases and quit.
```

## Dependencies

https://github.com/MartijnBraam/python-isc-dhcp-leases