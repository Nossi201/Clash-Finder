# resource_manager.py
from flask import Blueprint, jsonify
from auto_updater import LoLAutoUpdater, force_update, check_version
import threading

resource_manager = Blueprint('resource_manager', __name__)

def start_background_updater():
    """Start the auto-updater in a separate daemon thread."""
    from auto_updater import start_auto_updater
    thread = threading.Thread(target=start_auto_updater, daemon=True)
    thread.start()

@resource_manager.route('/api/resources/update', methods=['POST'])
def update_resources():
    """API endpoint to manually trigger a resource update"""
    try:
        updated = LoLAutoUpdater().update_resources()
        return jsonify({'status': 'success', 'updated': updated})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@resource_manager.route('/api/resources/force-update', methods=['POST'])
def force_update_resources():
    """API endpoint to force an immediate resource update"""
    try:
        force_update()
        return jsonify({'status': 'success', 'message': 'Resources updated successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

