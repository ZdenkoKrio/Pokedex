function getCookie(name) {
  const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return m ? m.pop() : '';
}

export async function toggleCompare(pokeapiId) {
  const res = await fetch(`/pokedex/compare/toggle/${pokeapiId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'Accept': 'application/json',
    },
  });
  const data = await res.json();
  if (data && data.ok) {
    const badge = document.getElementById('cmp-badge');
    if (badge) badge.textContent = data.count;
  }
  return data;
}