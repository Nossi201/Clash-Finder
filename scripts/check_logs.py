# scripts/check_logs.py
"""
Script to analyze application logs.
"""

import sys
from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta
import re

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def parse_log_line(line):
    """Parse a log line and extract components."""
    # Pattern: [timestamp] LEVEL in module: message
    pattern = r'\[(.+?)\] (\w+) (?:in (.+?): )?(.+)'
    match = re.match(pattern, line)

    if match:
        timestamp_str, level, module, message = match.groups()
        try:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            timestamp = None

        return {
            'timestamp': timestamp,
            'level': level,
            'module': module or 'unknown',
            'message': message
        }

    return None


def analyze_logs(log_file, hours=24):
    """Analyze log file."""
    if not log_file.exists():
        print(f"Log file not found: {log_file}")
        return

    cutoff_time = datetime.now() - timedelta(hours=hours)

    # Counters
    level_counts = Counter()
    module_counts = Counter()
    recent_errors = []
    recent_warnings = []

    # Read and parse logs
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            parsed = parse_log_line(line.strip())

            if not parsed:
                continue

            # Skip old logs
            if parsed['timestamp'] and parsed['timestamp'] < cutoff_time:
                continue

            # Count by level
            level_counts[parsed['level']] += 1

            # Count by module
            module_counts[parsed['module']] += 1

            # Collect errors and warnings
            if parsed['level'] == 'ERROR':
                recent_errors.append(parsed)
            elif parsed['level'] == 'WARNING':
                recent_warnings.append(parsed)

    return {
        'level_counts': level_counts,
        'module_counts': module_counts,
        'errors': recent_errors[-10:],  # Last 10 errors
        'warnings': recent_warnings[-10:],  # Last 10 warnings
    }


def main():
    """Main function."""
    log_dir = project_root / 'logs'
    log_file = log_dir / 'app.log'

    print("=" * 60)
    print("Clash Finder - Log Analyzer")
    print("=" * 60)
    print()

    # Get time range
    hours = 24
    if len(sys.argv) > 1:
        try:
            hours = int(sys.argv[1])
        except ValueError:
            print(f"Invalid hours: {sys.argv[1]}, using default (24)")

    print(f"Analyzing logs from last {hours} hours...")
    print()

    # Analyze
    results = analyze_logs(log_file, hours)

    if not results:
        return 1

    # Display summary
    print("Log Level Summary:")
    print("-" * 60)
    for level, count in results['level_counts'].most_common():
        print(f"  {level:12s}: {count:5d}")

    print()
    print("Most Active Modules:")
    print("-" * 60)
    for module, count in results['module_counts'].most_common(10):
        print(f"  {module:30s}: {count:5d}")

    # Display errors
    if results['errors']:
        print()
        print("Recent Errors:")
        print("-" * 60)
        for error in results['errors']:
            timestamp = error['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if error['timestamp'] else 'N/A'
            print(f"  [{timestamp}] {error['module']}")
            print(f"    {error['message'][:100]}")
            print()

    # Display warnings
    if results['warnings']:
        print()
        print("Recent Warnings:")
        print("-" * 60)
        for warning in results['warnings']:
            timestamp = warning['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if warning['timestamp'] else 'N/A'
            print(f"  [{timestamp}] {warning['module']}")
            print(f"    {warning['message'][:100]}")
            print()

    print("=" * 60)

    return 0


if __name__ == '__main__':
    sys.exit(main())