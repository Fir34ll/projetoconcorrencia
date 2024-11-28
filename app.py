from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit
from cache import cache
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
socketio = SocketIO(app)

@app.before_first_request
def initialize():
    cache.initialize_events()

@app.route('/')
def index():
    if 'user_id' not in session:
        session['user_id'] = secrets.token_hex(8)
    return render_template('index.html', events=cache.events)

@app.route('/admin')
def admin():
    return render_template('admin.html', events=cache.events, settings=cache.admin_settings)

@socketio.on('connect')
def handle_connect():
    user_id = session.get('user_id')
    cache.add_user(user_id)
    emit('update_state', {
        'events': cache.events,
        'queue': cache.waiting_queue,
        'active_users': list(cache.active_users),
        'online_users': len(cache.users_online)
    }, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    user_id = session.get('user_id')
    cache.remove_user(user_id)
    emit('update_state', {
        'events': cache.events,
        'queue': cache.waiting_queue,
        'active_users': list(cache.active_users),
        'online_users': len(cache.users_online)
    }, broadcast=True)

@socketio.on('reserve_event')
def handle_reservation(data):
    user_id = session.get('user_id')
    event_id = int(data['event_id'])
    success, message = cache.create_temp_reservation(user_id, event_id)
    
    emit('reservation_response', {
        'success': success,
        'message': message
    }, room=request.sid)
    
    emit('update_state', {
        'events': cache.events,
        'queue': cache.waiting_queue,
        'active_users': list(cache.active_users),
        'online_users': len(cache.users_online)
    }, broadcast=True)

@socketio.on('confirm_reservation')
def handle_confirmation(data):
    user_id = session.get('user_id')
    success, message = cache.confirm_reservation(user_id, data['user_data'])
    
    emit('confirmation_response', {
        'success': success,
        'message': message
    }, room=request.sid)
    
    emit('update_state', {
        'events': cache.events,
        'queue': cache.waiting_queue,
        'active_users': list(cache.active_users),
        'online_users': len(cache.users_online)
    }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True) 