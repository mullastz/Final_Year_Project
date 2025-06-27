import datetime
import ipaddress
from collections import defaultdict
from geolite2 import geolite2  
import math

class UnusualLoginDetector:
    def __init__(self, user_ip_whitelist=None, blacklisted_ips=None):
        # user_ip_whitelist = {'username1': ['192.168.1.0/24', '10.0.0.0/8'], ...}
        self.user_ip_whitelist = user_ip_whitelist or {}
        self.blacklisted_ips = set(blacklisted_ips or [])
        self.geo_reader = geolite2.reader()
        self.login_history = defaultdict(list)  # {username: [(timestamp, ip), ...]}
        self.failed_attempts = defaultdict(int)  # {username: count}

    def is_ip_allowed(self, username, ip):
        try:
            ip_obj = ipaddress.ip_address(ip)
            allowed_ranges = self.user_ip_whitelist.get(username, [])
            for cidr in allowed_ranges:
                if ip_obj in ipaddress.ip_network(cidr):
                    return True
            return False
        except ValueError:
            return False

    def is_ip_blacklisted(self, ip):
        return ip in self.blacklisted_ips

    def get_geo_location(self, ip):
        try:
            geo = self.geo_reader.get(ip)
            if geo:
                return geo.get('country', {}).get('names', {}).get('en', 'Unknown')
            return 'Unknown'
        except Exception:
            return 'Unknown'

    def impossible_travel(self, last_time, last_ip, current_time, current_ip, max_speed_kmph=500):
        # Rough check: calculate distance between last_ip and current_ip
        # and check if travel time is feasible
        from geopy.distance import geodesic  

        try:
            last_geo = self.geo_reader.get(last_ip)
            curr_geo = self.geo_reader.get(current_ip)
            if not last_geo or not curr_geo:
                return False

            last_coords = (last_geo['location']['latitude'], last_geo['location']['longitude'])
            curr_coords = (curr_geo['location']['latitude'], curr_geo['location']['longitude'])
            dist_km = geodesic(last_coords, curr_coords).kilometers

            time_diff_hours = (current_time - last_time).total_seconds() / 3600
            if time_diff_hours == 0:
                return True  # zero time difference impossible

            speed = dist_km / time_diff_hours
            return speed > max_speed_kmph
        except Exception:
            return False

    def is_login_time_unusual(self, login_time, allowed_hours=(7, 22)):
        # allowed_hours = tuple(start_hour, end_hour) in 24h format
        hour = login_time.hour
        return not (allowed_hours[0] <= hour < allowed_hours[1])

    def record_failed_attempt(self, username):
        self.failed_attempts[username] += 1

    def reset_failed_attempts(self, username):
        self.failed_attempts[username] = 0

    def detect(self, username, ip, login_time, success=True):
        alert = {
            'unusual_login': False,
            'reasons': []
        }

        if self.is_ip_blacklisted(ip):
            alert['unusual_login'] = True
            alert['reasons'].append('Login from blacklisted IP')

        if not self.is_ip_allowed(username, ip):
            alert['unusual_login'] = True
            alert['reasons'].append('Login from unrecognized IP')

        if self.is_login_time_unusual(login_time):
            alert['unusual_login'] = True
            alert['reasons'].append(f'Login at unusual hour: {login_time.hour}:00')

        history = self.login_history.get(username, [])
        if history:
            last_time, last_ip = history[-1]
            if self.impossible_travel(last_time, last_ip, login_time, ip):
                alert['unusual_login'] = True
                alert['reasons'].append('Impossible travel between IPs detected')

        if not success:
            self.record_failed_attempt(username)
            if self.failed_attempts[username] > 5:
                alert['unusual_login'] = True
                alert['reasons'].append('Multiple failed login attempts')
        else:
            self.reset_failed_attempts(username)
            self.login_history[username].append((login_time, ip))

        # Optionally detect spikes in login frequency
        recent_logins = [t for t, _ in self.login_history[username] if (login_time - t).total_seconds() < 3600]
        if len(recent_logins) > 10:
            alert['unusual_login'] = True
            alert['reasons'].append('High login frequency detected')

        return alert
