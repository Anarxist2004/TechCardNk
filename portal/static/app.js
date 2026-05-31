const authPanel = document.querySelector('#authPanel');
const dashboard = document.querySelector('#dashboard');
const authForm = document.querySelector('#authForm');
const authMessage = document.querySelector('#authMessage');
const submitButton = document.querySelector('#submitButton');
const logoutButton = document.querySelector('#logoutButton');
const welcomeText = document.querySelector('#welcomeText');
const dashboardAvatar = document.querySelector('#dashboardAvatar');
const dashboardUsername = document.querySelector('#dashboardUsername');
const userMenuButton = document.querySelector('#userMenuButton');
const userMenu = document.querySelector('#userMenu');
const modeButtons = document.querySelectorAll('[data-mode]');
const registerOnlyFields = document.querySelectorAll('.register-only');

let mode = 'login';

function getInitial(username) {
  const clean = String(username || '').trim();
  return clean ? clean[0].toUpperCase() : 'U';
}

function setMode(nextMode) {
  mode = nextMode;
  const isRegister = mode === 'register';

  modeButtons.forEach((button) => {
    button.classList.toggle('active', button.dataset.mode === mode);
  });

  registerOnlyFields.forEach((field) => {
    const input = field.querySelector('input');
    field.classList.toggle('hidden', !isRegister);
    if (input) {
      input.required = isRegister;
    }
  });

  authForm.password.autocomplete = isRegister ? 'new-password' : 'current-password';
  submitButton.textContent = isRegister ? 'Создать пользователя' : 'Войти';
  authMessage.textContent = '';
}

function setUser(user) {
  const username = user?.username || 'Пользователь';
  const displayName = user?.full_name || username;
  const details = [user?.position, user?.company].filter(Boolean).join(', ');

  dashboardUsername.textContent = displayName;
  dashboardAvatar.textContent = getInitial(displayName);
  welcomeText.textContent = details
    ? `${displayName}: ${details}`
    : `Вы вошли как ${displayName}. Откройте нужный модуль через вкладки сверху.`;
}

function showDashboard(user) {
  setUser(user);
  authPanel.classList.add('hidden');
  dashboard.classList.remove('hidden');
  window.location.href = '/tech-cards/';
}

function showAuth() {
  dashboard.classList.add('hidden');
  authPanel.classList.remove('hidden');
  userMenu.classList.add('hidden');
  userMenuButton.setAttribute('aria-expanded', 'false');
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

userMenuButton.addEventListener('click', () => {
  const isOpen = !userMenu.classList.contains('hidden');
  userMenu.classList.toggle('hidden', isOpen);
  userMenuButton.setAttribute('aria-expanded', String(!isOpen));
});

document.addEventListener('click', (event) => {
  if (!event.target.closest('.nk-module-user-menu')) {
    userMenu.classList.add('hidden');
    userMenuButton.setAttribute('aria-expanded', 'false');
  }
});

authForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  authMessage.textContent = '';
  submitButton.disabled = true;

  const payload = {
    username: authForm.username.value,
    password: authForm.password.value,
  };

  if (mode === 'register') {
    payload.full_name = authForm.full_name.value;
    payload.position = authForm.position.value;
    payload.company = authForm.company.value;
  }

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

setMode(mode);
loadMe();
