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
    // Добавляем классы для анимации (только если это реально нужно)
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.05}s`;
    });

    // Важно: НЕ делаем autofocus на каждую AJAX-перерисовку,
    // иначе после отправки комментария страница может «ломаться» UX.
    // Авто-фокус оставляем только на странице создания/редактирования,
    // где реально есть форма ввода.
    const formRoot = document.querySelector('.ajax-ticket-form');
    if (formRoot) return;

    const firstInput = document.querySelector('input:not([type=hidden]), textarea');
    if (firstInput && !firstInput.value) {
        firstInput.focus();
    }
});
