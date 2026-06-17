// Клиентская логика

// Подтверждение удаления (если нужно)
function confirmDelete(message) {
    return confirm(message || 'Вы уверены?');
}

// Авто-обновление статусов через AJAX (опционально)
async function updateTicketStatus(ticketId, newStatus) {
    try {
        const response = await fetch(`/api/tickets/${ticketId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: newStatus })
        });
        
        if (response.ok) {
            location.reload();
        } else {
            console.error('Ошибка обновления');
        }
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

// Поиск с debounce
let searchTimeout;
function debounceSearch(input) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        const searchForm = document.querySelector('form');
        if (searchForm) searchForm.submit();
    }, 500);
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    // Добавляем классы для анимации
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.05}s`;
    });
    
    // Авто-фокус на первое поле ввода
    const firstInput = document.querySelector('input:not([type=hidden]), textarea');
    if (firstInput && !firstInput.value) {
        firstInput.focus();
    }
});