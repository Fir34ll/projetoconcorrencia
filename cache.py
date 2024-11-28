from threading import Lock
from datetime import datetime, timedelta

class EventCache:
    def __init__(self):
        self.lock = Lock()
        self.events = {}
        self.temp_reservations = {}
        self.users_online = set()
        self.waiting_queue = []
        self.active_users = set()
        self.admin_settings = {
            'max_active_users': 3,
            'selection_timeout': 30,
            'reservation_timeout': 120
        }

    def initialize_events(self):
        default_events = [
            {"id": 1, "name": "Conferência Tech", "total_slots": 50, "available_slots": 50},
            {"id": 2, "name": "Workshop Python", "total_slots": 30, "available_slots": 30},
            {"id": 3, "name": "Hackathon 2024", "total_slots": 100, "available_slots": 100},
            {"id": 4, "name": "Meetup AI", "total_slots": 40, "available_slots": 40},
            {"id": 5, "name": "Dev Summit", "total_slots": 60, "available_slots": 60}
        ]
        with self.lock:
            self.events = {event["id"]: event for event in default_events}

    def add_user(self, user_id):
        with self.lock:
            self.users_online.add(user_id)
            if len(self.active_users) < self.admin_settings['max_active_users']:
                self.active_users.add(user_id)
            else:
                self.waiting_queue.append(user_id)

    def remove_user(self, user_id):
        with self.lock:
            self.users_online.discard(user_id)
            self.active_users.discard(user_id)
            if user_id in self.waiting_queue:
                self.waiting_queue.remove(user_id)
            self._process_queue()

    def create_temp_reservation(self, user_id, event_id):
        with self.lock:
            if user_id not in self.active_users:
                return False, "Usuário não está ativo"
            
            event = self.events.get(event_id)
            if not event or event["available_slots"] <= 0:
                return False, "Evento indisponível"

            self.temp_reservations[user_id] = {
                "event_id": event_id,
                "timestamp": datetime.now(),
                "confirmed": False
            }
            self.events[event_id]["available_slots"] -= 1
            return True, "Reserva temporária criada"

    def confirm_reservation(self, user_id, user_data):
        with self.lock:
            reservation = self.temp_reservations.get(user_id)
            if not reservation:
                return False, "Reserva temporária não encontrada"

            if datetime.now() - reservation["timestamp"] > timedelta(seconds=self.admin_settings['reservation_timeout']):
                self._cancel_reservation(user_id)
                return False, "Tempo de reserva expirado"

            reservation["confirmed"] = True
            reservation["user_data"] = user_data
            return True, "Reserva confirmada com sucesso"

    def _cancel_reservation(self, user_id):
        with self.lock:
            if user_id in self.temp_reservations:
                event_id = self.temp_reservations[user_id]["event_id"]
                self.events[event_id]["available_slots"] += 1
                del self.temp_reservations[user_id]

    def _process_queue(self):
        with self.lock:
            while len(self.active_users) < self.admin_settings['max_active_users'] and self.waiting_queue:
                next_user = self.waiting_queue.pop(0)
                if next_user in self.users_online:
                    self.active_users.add(next_user)

cache = EventCache() 