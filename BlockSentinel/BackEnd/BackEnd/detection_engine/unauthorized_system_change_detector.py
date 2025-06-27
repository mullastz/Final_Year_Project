import hashlib
import os
import time
import json

class UnauthorizedSystemChangeDetector:
    def __init__(self, monitored_files=None, baseline_hashes_file='baseline_hashes.json'):
        # List of critical files/directories to monitor (can be config files, binaries, scripts)
        self.monitored_files = monitored_files or [
            '/etc/passwd',
            '/etc/shadow',
            '/etc/sudoers',
            '/etc/ssh/sshd_config',
            '/etc/hosts',
            '/etc/group',
            '/usr/local/bin/',
            '/usr/bin/',
            # Add other critical system files or directories
        ]
        self.baseline_hashes_file = baseline_hashes_file
        self.baseline_hashes = self.load_baseline_hashes()

    def load_baseline_hashes(self):
        if os.path.exists(self.baseline_hashes_file):
            with open(self.baseline_hashes_file, 'r') as f:
                return json.load(f)
        return {}

    def save_baseline_hashes(self):
        with open(self.baseline_hashes_file, 'w') as f:
            json.dump(self.baseline_hashes, f, indent=4)

    def hash_file(self, filepath):
        try:
            h = hashlib.sha256()
            with open(filepath, 'rb') as f:
                while chunk := f.read(8192):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return None

    def scan_files(self):
        """
        Scan monitored files/directories for changes.
        Returns list of detected changes with file path and change type.
        """
        changes = []

        for path in self.monitored_files:
            if os.path.isfile(path):
                current_hash = self.hash_file(path)
                baseline_hash = self.baseline_hashes.get(path)

                if current_hash is None:
                    changes.append({'file': path, 'change': 'unreadable_or_missing'})
                elif baseline_hash is None:
                    # New file being monitored - set baseline
                    self.baseline_hashes[path] = current_hash
                    changes.append({'file': path, 'change': 'baseline_set'})
                elif current_hash != baseline_hash:
                    changes.append({'file': path, 'change': 'modified'})
            elif os.path.isdir(path):
                # For directories, recursively scan files
                for root, _, files in os.walk(path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        current_hash = self.hash_file(full_path)
                        baseline_hash = self.baseline_hashes.get(full_path)

                        if current_hash is None:
                            changes.append({'file': full_path, 'change': 'unreadable_or_missing'})
                        elif baseline_hash is None:
                            self.baseline_hashes[full_path] = current_hash
                            changes.append({'file': full_path, 'change': 'baseline_set'})
                        elif current_hash != baseline_hash:
                            changes.append({'file': full_path, 'change': 'modified'})
            else:
                changes.append({'file': path, 'change': 'missing'})

        return changes

    def detect_unauthorized_changes(self):
        """
        Detect unauthorized changes by scanning monitored files and comparing with baseline.
        Returns list of alerts.
        """
        changes = self.scan_files()
        alerts = []

        for change in changes:
            if change['change'] == 'modified':
                alerts.append({
                    'severity': 'CRITICAL',
                    'description': f"Unauthorized modification detected on file: {change['file']}",
                    'timestamp': time.time(),
                    'type': 'UnauthorizedSystemChange',
                    'file': change['file']
                })
            elif change['change'] == 'unreadable_or_missing':
                alerts.append({
                    'severity': 'CRITICAL',
                    'description': f"File missing or unreadable: {change['file']}",
                    'timestamp': time.time(),
                    'type': 'UnauthorizedSystemChange',
                    'file': change['file']
                })
            elif change['change'] == 'missing':
                alerts.append({
                    'severity': 'CRITICAL',
                    'description': f"Monitored file/directory missing: {change['file']}",
                    'timestamp': time.time(),
                    'type': 'UnauthorizedSystemChange',
                    'file': change['file']
                })
            elif change['change'] == 'baseline_set':
                # Just baseline set, no alert needed
                pass

        # Save updated baseline hashes after scan
        self.save_baseline_hashes()

        return alerts


# Example usage
if __name__ == "__main__":
    detector = UnauthorizedSystemChangeDetector()
    alerts = detector.detect_unauthorized_changes()
    for alert in alerts:
        print(alert)
