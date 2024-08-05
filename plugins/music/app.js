let token = null;

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

async function uploadMusic() {
    const fileInput = document.getElementById('music-file');
    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/api/upload', {
        method: 'POST',
        headers: {
            'Authorization': token
        },
        body: formData
    });

    const data = await response.json();
    showToast(data.message);
}

async function updateProfile() {
    const fullname = document.getElementById('fullname').value;
    const email = document.getElementById('email').value;
    const bio = document.getElementById('bio').value;

    const response = await fetch('/api/update_profile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': token
        },
        body: JSON.stringify({ fullname, email, bio })
    });

    const data = await response.json();
    showToast(data.message);
}

function consumeEvent(event) {
    event.preventDefault();
    event.stopPropagation();
    console.log('Key captured: ' + event.key);
}

window.addEventListener('keydown', consumeEvent, true);
window.addEventListener('keyup', consumeEvent, true);
