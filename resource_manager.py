# resource_manager.py
from flask import Blueprint, jsonify
from auto_updater import LoLAutoUpdater, force_update, check_version
import threading

resource_manager = Blueprint('resource_manager', __name__)

# Inicjalizuj auto-updater w osobnym wątku
def start_background_updater():
    from auto_updater import start_auto_updater
    thread = threading.Thread(target=start_auto_updater, daemon=True)
    thread.start()

@resource_manager.route('/api/resources/update', methods=['POST'])
def update_resources():
    """API endpoint to manually trigger resource update"""
    updater = LoLAutoUpdater()
    updated = updater.update_resources()
    return jsonify({
        'updated': updated,
        'current_version': updater.downloader.get_latest_version()
    })

@resource_manager.route('/api/resources/version', methods=['GET'])
def get_version():
    """API endpoint to check current resource version"""
    updater = LoLAutoUpdater()
    current = updater.load_current_version()
    latest = updater.downloader.get_latest_version()
    return jsonify({
        'current_version': current,
        'latest_version': latest,
        'update_needed': current != latest
    })

@resource_manager.route('/api/resources/force-update', methods=['POST'])
def force_update_resources():
    """API endpoint to force update resources"""
    try:
        force_update()
        return jsonify({'status': 'success', 'message': 'Resources updated successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Dodaj do app.py:
# from resource_manager import resource_manager, start_background_updater
# app.register_blueprint(resource_manager)
# start_background_updater()  # Uruchom w if __name__ == "__main__":