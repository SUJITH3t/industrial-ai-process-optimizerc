const loginForm = document.getElementById('loginForm');
const message = document.getElementById('message');

loginForm.addEventListener('submit', async function (event) {
    event.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();

    if (!username || !password) {
        message.textContent = 'Please enter both username and password.';
        message.style.color = '#b91c1c';
        return;
    }

    try {
        const response = await fetch('http://127.0.0.1:5001/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            message.textContent = data.message || 'Invalid username or password.';
            message.style.color = '#b91c1c';
            return;
        }

        message.textContent = `Welcome, ${username}! Login successful.`;
        message.style.color = '#0f766e';
        window.location.href = 'dashboard.html';
    } catch (error) {
        message.textContent = 'Unable to connect to the server. Please start the backend.';
        message.style.color = '#b91c1c';
        console.error(error);
    }
});
