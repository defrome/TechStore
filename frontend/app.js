const API_BASE_URL = 'http://127.0.0.1:8000';

async function loadItems() {
    const resultDiv = document.getElementById('result');
    const button = document.querySelector('#loadItemsBtn'); // Используем конкретную кнопку

    try {
        button.disabled = true;
        button.textContent = 'Загрузка...';
        resultDiv.innerHTML = '<div class="loading">Загружаем товары из базы данных...</div>';

        const response = await fetch(`${API_BASE_URL}/get_item`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`Ошибка HTTP: ${response.status}`);
        }

        const data = await response.json();
        displayItems(data.items);

    } catch (error) {
        console.error('Ошибка:', error);
        resultDiv.innerHTML = `
            <div class="error">
                <h3>Ошибка при загрузке данных</h3>
                <p>${error.message}</p>
            </div>
        `;
    } finally {
        button.disabled = false;
        button.textContent = 'Загрузить товары';
    }
}

async function loadUsers() {
    const resultDiv = document.getElementById('result_users');
    const button = document.querySelector('#loadUsersBtn'); // Отдельная кнопка для пользователей

    try {
        button.disabled = true;
        button.textContent = 'Загрузка...';
        resultDiv.innerHTML = '<div class="loading">Загружаем пользователей из базы данных...</div>';

        const response = await fetch(`${API_BASE_URL}/get_users`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`Ошибка HTTP: ${response.status}`);
        }

        const data = await response.json();
        displayUsers(data.users); // Исправлено: передаем users, а не items

    } catch (error) {
        console.error('Ошибка:', error);
        resultDiv.innerHTML = `
            <div class="error">
                <h3>Ошибка при загрузке данных</h3>
                <p>${error.message}</p>
            </div>
        `;
    } finally {
        button.disabled = false;
        button.textContent = 'Загрузить пользователей';
    }
}

function displayItems(items) {
    const resultDiv = document.getElementById('result');

    if (!items || items.length === 0) {
        resultDiv.innerHTML = '<div class="loading">Товары не найдены</div>';
        return;
    }

    let html = `
        <h2>Найдено товаров: ${items.length}</h2>
        <div class="items-grid">
    `;

    items.forEach(item => {
        const statusClass = item.availability_status ? 'status-available' : 'status-unavailable';
        const statusText = item.availability_status ? 'В наличии' : 'Нет в наличии';

        const categoriesHtml = item.categories && item.categories.length > 0
            ? item.categories.map(cat =>
                `<span class="category">${cat.name}</span>`
              ).join('')
            : '<span class="category">Без категории</span>';

        html += `
            <div class="item-card">
                ${item.image ? `<img src="${item.image}" alt="${item.name}" class="item-image" onerror="this.style.display='none'">` : ''}
                <h3>${item.name}</h3>
                <p>${item.description || 'Описание отсутствует'}</p>
                <p class="price">${formatPrice(item.price)} руб.</p>
                <p class="${statusClass}">${statusText}</p>
                <p><strong>Производитель:</strong> ${item.manufacturer || 'Не указан'}</p>
                <p><strong>Количество:</strong> ${item.quantity} шт.</p>
                <div><strong>Категории:</strong> ${categoriesHtml}</div>
            </div>
        `;
    });

    html += '</div>';
    resultDiv.innerHTML = html;
}

function displayUsers(users) { // Исправлено: параметр users вместо items
    const resultDiv = document.getElementById('result_users');

    if (!users || users.length === 0) {
        resultDiv.innerHTML = '<div class="loading">Пользователи не найдены</div>';
        return;
    }

    let html = `
        <h2>Найдено пользователей: ${users.length}</h2>
        <div class="users-grid">
    `;

    users.forEach(user => { // Исправлено: user вместо item
        const premiumClass = user.is_premium ? 'premium-user' : 'regular-user';
        const premiumText = user.is_premium ? 'Премиум' : 'Обычный';
        const statusText = user.status || 'Не указан';

        html += `
            <div class="user-card">
                <h3>${user.first_name} ${user.surname}</h3>
                <p><strong>ID:</strong> ${user.id}</p>
                <p><strong>Статус:</strong> ${statusText}</p>
                <p class="balance">Баланс: ${formatPrice(user.balance)} руб.</p>
                <p class="${premiumClass}">${premiumText}</p>
                <p><strong>Количество заказов:</strong> ${user.number_of_orders}</p>
            </div>
        `;
    });

    html += '</div>';
    resultDiv.innerHTML = html;
}

function formatPrice(price) {
    return new Intl.NumberFormat('ru-RU').format(price);
}

// Загружаем товары при загрузке страницы
document.addEventListener('DOMContentLoaded', loadItems);
document.addEventListener('DOMContentLoaded', loadUsers);