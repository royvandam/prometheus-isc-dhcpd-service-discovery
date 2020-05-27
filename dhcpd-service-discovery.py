#!/usr/bin/env python3
 
import sys, re
from isc_dhcp_leases import IscDhcpLeases

def whitelist(value, whitelist=[]):
    if not isinstance(whitelist, list):
        return True

    for allowed in whitelist:
       if not re.match(allowed, value):
           return False
    return True

def parse_arg_list(args):
    return args[0] if args else []

def parse_job_args(job_args):
    jobs = {}
    if not job_args:
        sys.stderr.write("expected at least one job\n")
        sys.exit(1)
    for job in job_args[0]:
        try:
            name, port = job.split(':')

            if not port.isnumeric():
                sys.stderr.write("port '%s' for job '%s' is not a number\n" % (port, name))
                sys.exit(1)

            jobs[name] = port
        except ValueError:
            sys.stderr.write("invalid job definition '%s', expected {name}:{port}\n" % job)
            sys.exit(1)
    return jobs

def parse_leases(leases, accepted_macs=[], accepted_hostnames=[]):
    targets = []
    for mac, lease in leases.items():
        if not whitelist(mac, accepted_macs):
            continue

        if not whitelist(lease.hostname, accepted_hostnames):
            continue

        targets.append(lease.ip)
    return targets

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Generate Prometheus scrape configuration based on ISC DHCP lease file")
    parser.add_argument('-j', '--job', action='append', nargs='+', metavar='{name:port}',
        help="Jobs to configure, accepts multiple values (e.g. node:9100)")
    parser.add_argument('-l', '--leases', metavar='PATH',
        help="Path to dhcpd.leases file (default: /var/lib/dhcp/dhcpd.leases)",
        default="/var/lib/dhcp/dhcpd.leases")
    parser.add_argument('-o', '--output', metavar='PATH',
        help="Path to targets file (default: /etc/prometheus/targets.json)(- for stdout)",
        default="/etc/prometheus/targets.json")
    parser.add_argument('-m', '--mac', action='append', nargs='+',
        help="Whitelist MAC address (note: accepts regex)")
    parser.add_argument('-n', '--hostname', action='append', nargs='+',
        help="Whitelist hostname (note: accepts regex)")
    parser.add_argument('-p', '--print', action='store_true',
        help="Print active DHCP leases and quit.")
    args = parser.parse_args()

    leases = IscDhcpLeases(args.leases).get_current()

    if args.print:
        for mac, lease in leases.items():
            print(mac, lease.ip, lease.hostname)
        sys.exit(0)

    accepted_macs = parse_arg_list(args.mac)
    accepted_hostnames = parse_arg_list(args.hostname)
    targets = parse_leases(leases, accepted_macs, accepted_hostnames)

    jobs = parse_job_args(args.job)

    config = []
    for job, port in jobs.items():
        config.append({
            'labels': {
                'job': job
            },
            'targets': [
                target + ':' + port for target in targets
            ]
        })
    
    if args.output == '-':
        fp = sys.stdout
    else:
        try:
            fp = open(args.output, 'w')
        except Exception as e:
            sys.stderr.write("Unable to open target file for writing:\n")
            sys.stderr.write(str(e) + "\n")
            sys.exit(1)

    import json
    json.dump(config, fp, sort_keys=True, indent=2)
    fp.flush()

    sys.exit(0)