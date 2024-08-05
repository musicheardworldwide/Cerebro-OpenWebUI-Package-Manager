function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.className = 'toast show';
        setTimeout(() => {
            toast.className = toast.className.replace('show', '');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 500);
        }, 3000);
    }, 100);
}

// Example usage
async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    if (data.token) {
        token = data.token;
        document.getElementById('login-form').style.display = 'none';
        document.getElementById('upload-form').style.display = 'block';
        document.getElementById('profile-form').style.display = 'block';
        showToast('Login successful!');
    } else {
        showToast('Login failed. Please check your credentials.');
    }
}
