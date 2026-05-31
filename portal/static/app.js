const authPanel = document.querySelector('#authPanel');
const dashboard = document.querySelector('#dashboard');
const authForm = document.querySelector('#authForm');
const authMessage = document.querySelector('#authMessage');
const submitButton = document.querySelector('#submitButton');
const logoutButton = document.querySelector('#logoutButton');
const welcomeText = document.querySelector('#welcomeText');
const modeButtons = document.querySelectorAll('[data-mode]');

let mode = 'login';

function setMode(nextMode) {
  mode = nextMode;
  modeButtons.forEach((button) => {
    button.classList.toggle('active', button.dataset.mode === mode);
  });
  submitButton.textContent = mode === 'login' ? 'Войти' : 'Создать пользователя';
  authMessage.textContent = '';
}

function showDashboard(user) {
  authPanel.classList.add('hidden');
  dashboard.classList.remove('hidden');
  welcomeText.textContent = `Вы вошли как ${user.username}.`;
}

function showAuth() {
  dashboard.classList.add('hidden');
  authPanel.classList.remove('hidden');
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    credentials: 'same-origin',
    ...options,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || 'Ошибка запроса');
  }
  return data;
}

async function loadMe() {
  try {
    const user = await requestJson('/api/auth/me');
    showDashboard(user);
  } catch {
    showAuth();
  }
}

modeButtons.forEach((button) => {
  button.addEventListener('click', () => setMode(button.dataset.mode));
});

authForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  authMessage.textContent = '';
  submitButton.disabled = true;

  const payload = {
    username: authForm.username.value,
    password: authForm.password.value,
  };

  try {
    const user = await requestJson(`/api/auth/${mode}`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    authForm.reset();
    showDashboard(user);
  } catch (error) {
    authMessage.textContent = error.message;
  } finally {
    submitButton.disabled = false;
  }
});

logoutButton.addEventListener('click', async () => {
  await requestJson('/api/auth/logout', { method: 'POST' }).catch(() => null);
  showAuth();
});

loadMe();
