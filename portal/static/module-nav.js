(function () {
  function getInitial(username) {
    const clean = String(username || '').trim();
    return clean ? clean[0].toUpperCase() : 'U';
  }

  function createTab(label, href, isActive) {
    const link = document.createElement('a');
    link.className = `nk-module-tab${isActive ? ' is-active' : ''}`;
    link.href = href;
    link.textContent = label;
    return link;
  }

  async function loadUser() {
    const response = await fetch('/api/auth/me', { credentials: 'same-origin' });
    if (!response.ok) {
      window.location.href = '/';
      return null;
    }
    return response.json();
  }

  async function logout() {
    await fetch('/api/auth/logout', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
    }).catch(() => null);
    window.location.href = '/';
  }

  function closeMenu(menu, button) {
    menu.classList.add('hidden');
    button.setAttribute('aria-expanded', 'false');
  }

  async function renderModuleNav() {
    if (document.querySelector('.nk-module-nav')) {
      return;
    }

    const user = await loadUser();
    if (!user) {
      return;
    }

    const path = window.location.pathname;
    const nav = document.createElement('nav');
    nav.className = 'nk-module-nav';

    const tabs = document.createElement('div');
    tabs.className = 'nk-module-tabs';
    tabs.append(
      createTab('Экспертный анализ', '/expert-analysis/', path.startsWith('/expert-analysis')),
      createTab('Техкарты', '/tech-cards/', path.startsWith('/tech-cards')),
    );

    const userMenu = document.createElement('div');
    userMenu.className = 'nk-module-user-menu';

    const button = document.createElement('button');
    button.className = 'nk-module-user';
    button.type = 'button';
    button.setAttribute('aria-expanded', 'false');
    button.title = user.username || '';

    const avatar = document.createElement('span');
    avatar.className = 'nk-module-avatar';
    avatar.textContent = getInitial(user.username);

    const username = document.createElement('span');
    username.className = 'nk-module-username';
    username.textContent = user.username || 'Пользователь';

    const menu = document.createElement('div');
    menu.className = 'nk-module-menu hidden';

    const logoutButton = document.createElement('button');
    logoutButton.type = 'button';
    logoutButton.textContent = 'Выйти';

    button.append(avatar, username);
    menu.append(logoutButton);
    userMenu.append(button, menu);
    nav.append(tabs, userMenu);
    document.body.prepend(nav);

    button.addEventListener('click', () => {
      const isOpen = !menu.classList.contains('hidden');
      menu.classList.toggle('hidden', isOpen);
      button.setAttribute('aria-expanded', String(!isOpen));
    });

    logoutButton.addEventListener('click', logout);

    document.addEventListener('click', (event) => {
      if (!event.target.closest('.nk-module-user-menu')) {
        closeMenu(menu, button);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderModuleNav);
  } else {
    renderModuleNav();
  }
}());
