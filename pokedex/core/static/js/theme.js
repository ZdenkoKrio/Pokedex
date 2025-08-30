(function () {
  const COOKIE = 'theme';
  const getCookie = (name) =>
    document.cookie.split('; ').find(r => r.startsWith(name + '='))?.split('=')[1];
  const setCookie = (name, value, days = 365) => {
    const d = new Date();
    d.setTime(d.getTime() + days*24*60*60*1000);
    document.cookie = `${name}=${encodeURIComponent(value)}; expires=${d.toUTCString()}; path=/; SameSite=Lax`;
  };

  // expose toggle
  window.__toggleTheme = function () {
    const cur = document.documentElement.getAttribute('data-theme') || 'light';
    const next = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    setCookie(COOKIE, next);
    try {
      const btn = document.getElementById('theme-toggle');
      if (btn) btn.innerText = (next === 'dark' ? '🌞 Light' : '🌓 Dark') + ' Theme';
    } catch(e){}
  };

  // set initial button label after load
  document.addEventListener('DOMContentLoaded', () => {
    const cur = document.documentElement.getAttribute('data-theme') || 'light';
    const btn = document.getElementById('theme-toggle');
    if (btn) btn.innerText = (cur === 'dark' ? '🌞 Light' : '🌓 Dark') + ' Theme';
  });
})();