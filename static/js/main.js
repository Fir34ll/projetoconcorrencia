const socket = io();
let reservationTimer;
let selectionTimer;
let currentEventId;

socket.on('connect', () => {
    console.log('Conectado ao servidor');
});

socket.on('update_state', (data) => {
    updateEventCards(data.events);
    updateQueue(data.queue);
    updateOnlineCount(data.online_users);
    updateUserStatus(data.active_users);
});

socket.on('reservation_response', (data) => {
    if (data.success) {
        showReservationModal();
        startReservationTimer();
    } else {
        alert(data.message);
    }
});

socket.on('confirmation_response', (data) => {
    if (data.success) {
        hideReservationModal();
        alert('Reserva confirmada com sucesso!');
    } else {
        alert(data.message);
        hideReservationModal();
    }
});

document.querySelectorAll('.reserve-btn').forEach(button => {
    button.addEventListener('click', (e) => {
        const eventCard = e.target.closest('.event-card');
        currentEventId = eventCard.dataset.eventId;
        socket.emit('reserve_event', { event_id: currentEventId });
    });
});

document.getElementById('reservation-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const userData = {
        name: formData.get('name'),
        phone: formData.get('phone')
    };
    socket.emit('confirm_reservation', { user_data: userData });
});

function updateEventCards(events) {
    Object.values(events).forEach(event => {
        const card = document.querySelector(`[data-event-id="${event.id}"]`);
        if (card) {
            const slotsElement = card.querySelector('.available-slots');
            slotsElement.textContent = event.available_slots;
            
            const button = card.querySelector('.reserve-btn');
            button.disabled = event.available_slots <= 0;
        }
    });
}

function updateQueue(queue) {
    const queueElement = document.getElementById('waiting-queue');
    queueElement.innerHTML = queue.map(userId => 
        `<li>Usuário ${userId.substring(0, 6)}...</li>`
    ).join('');
}

function updateOnlineCount(count) {
    document.getElementById('online-count').textContent = count;
}

function updateUserStatus(activeUsers) {
    const userId = document.cookie.split(';')
        .find(cookie => cookie.trim().startsWith('session='))
        ?.split('=')[1];
    
    const statusElement = document.getElementById('user-status');
    const timerContainer = document.getElementById('timer-container');
    
    if (activeUsers.includes(userId)) {
        statusElement.textContent = 'Ativo';
        timerContainer.style.display = 'block';
        startSelectionTimer();
    } else {
        statusElement.textContent = 'Na fila de espera';
        timerContainer.style.display = 'none';
        if (selectionTimer) {
            clearInterval(selectionTimer);
        }
    }
}

function showReservationModal() {
    document.getElementById('reservation-modal').style.display = 'block';
}

function hideReservationModal() {
    document.getElementById('reservation-modal').style.display = 'none';
    if (reservationTimer) {
        clearInterval(reservationTimer);
    }
}

function startReservationTimer() {
    let timeLeft = 120;
    const timerElement = document.getElementById('confirmation-timer');
    
    if (reservationTimer) {
        clearInterval(reservationTimer);
    }
    
    reservationTimer = setInterval(() => {
        timeLeft--;
        timerElement.textContent = timeLeft;
        
        if (timeLeft <= 0) {
            clearInterval(reservationTimer);
            hideReservationModal();
            alert('Tempo de reserva expirado!');
        }
    }, 1000);
}

function startSelectionTimer() {
    let timeLeft = 30;
    const timerElement = document.getElementById('timer');
    
    if (selectionTimer) {
        clearInterval(selectionTimer);
    }
    
    timerElement.textContent = timeLeft;
    selectionTimer = setInterval(() => {
        timeLeft--;
        timerElement.textContent = timeLeft;
        
        if (timeLeft <= 0) {
            clearInterval(selectionTimer);
        }
    }, 1000);
} 