// =============================================
// blog.js — Comentarios, Reacciones y Suscripción
// Math & Beer Games
// =============================================

const userId = localStorage.getItem('userId');

// ─── Utilidades ───────────────────────────────────────────────
function formatDate(isoStr) {
  const d = new Date(isoStr);
  return d.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function getUserNickname() {
  return localStorage.getItem('nickname') || null;
}

// ─── Renderizado de comentarios ────────────────────────────────
function renderComment(c, container) {
  const div = document.createElement('div');
  div.className = 'blog-comment';
  div.innerHTML = `
    <div class="blog-comment-header">
      <span class="blog-nick"><i class="fa-solid fa-user-astronaut me-1"></i>${c.nickname}</span>
      <span class="blog-time">${formatDate(c.created_at)}</span>
    </div>
    <p class="blog-comment-text">${c.content}</p>
  `;
  container.appendChild(div);
}

// ─── Carga de comentarios ──────────────────────────────────────
async function loadComments(eventId, container) {
  container.innerHTML = '<p class="blog-loading">Cargando comentarios...</p>';
  try {
    const res = await fetch(`/api/comments/${eventId}`);
    const data = await res.json();
    container.innerHTML = '';
    if (data.comments.length === 0) {
      container.innerHTML = '<p class="blog-empty">Sé el primero en comentar 🍻</p>';
    } else {
      data.comments.forEach(c => renderComment(c, container));
    }
  } catch {
    container.innerHTML = '<p class="blog-empty text-danger">Error al cargar comentarios</p>';
  }
}

// ─── Carga de reacciones ───────────────────────────────────────
async function loadReactions(eventId, btn) {
  try {
    const url = userId ? `/api/reactions/${eventId}?userid=${userId}` : `/api/reactions/${eventId}`;
    const res = await fetch(url);
    const data = await res.json();
    btn.dataset.reacted = data.reacted ? '1' : '0';
    btn.querySelector('.blog-react-count').textContent = data.total;
    btn.classList.toggle('blog-reacted', data.reacted);
  } catch { /* silencioso */ }
}

// ─── Toggle Reacción ──────────────────────────────────────────
async function toggleReaction(eventId, btn) {
  if (!userId) {
    showBlogToast('Crea un Nickname primero para reaccionar 🍺');
    return;
  }
  try {
    const res = await fetch('/api/reactions/toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userid: userId, event_id: eventId })
    });
    const data = await res.json();
    if (data.success) {
      btn.dataset.reacted = data.reacted ? '1' : '0';
      btn.querySelector('.blog-react-count').textContent = data.total;
      btn.classList.toggle('blog-reacted', data.reacted);
      // animación breve
      btn.classList.add('blog-react-pop');
      setTimeout(() => btn.classList.remove('blog-react-pop'), 400);
    }
  } catch { /* silencioso */ }
}

// ─── Enviar comentario ─────────────────────────────────────────
async function submitComment(eventId, textarea, container) {
  const content = textarea.value.trim();
  if (!content) return;
  if (!userId) {
    showBlogToast('Crea un Nickname primero para comentar 🍺');
    return;
  }

  textarea.disabled = true;
  try {
    const res = await fetch('/api/comments/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userid: userId, event_id: eventId, content })
    });
    const data = await res.json();
    if (data.success) {
      // Limpiar "vacío" si era el primer comentario
      const emptyMsg = container.querySelector('.blog-empty');
      if (emptyMsg) emptyMsg.remove();
      renderComment(data, container);
      textarea.value = '';
      container.scrollTop = container.scrollHeight;
    } else {
      showBlogToast(data.message || 'Error al comentar');
    }
  } catch {
    showBlogToast('Error de conexión');
  } finally {
    textarea.disabled = false;
    textarea.focus();
  }
}

// ─── Suscripción ───────────────────────────────────────────────
async function handleSubscribe(form) {
  const emailInput = form.querySelector('#subscribe-email');
  const nameInput = form.querySelector('#subscribe-name');
  const btn = form.querySelector('#subscribe-btn');
  const email = emailInput.value.trim();
  const name = nameInput ? nameInput.value.trim() : '';

  if (!email) { showBlogToast('Ingresa tu correo 📧'); return; }

  btn.disabled = true;
  btn.textContent = 'Suscribiendo...';
  try {
    const res = await fetch('/api/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, name })
    });
    const data = await res.json();
    if (data.success) {
      form.innerHTML = `<p class="blog-subscribe-ok"><i class="fa-solid fa-circle-check me-2"></i>¡Ya estás suscrito/a! Te notificaremos sobre los próximos eventos 🎉</p>`;
    } else {
      showBlogToast(data.message || 'Error al suscribirse');
      btn.disabled = false;
      btn.textContent = '¡Suscribirme!';
    }
  } catch {
    showBlogToast('Error de conexión');
    btn.disabled = false;
    btn.textContent = '¡Suscribirme!';
  }
}

// ─── Toast ─────────────────────────────────────────────────────
function showBlogToast(msg) {
  let toast = document.getElementById('blog-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'blog-toast';
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.classList.add('show');
  clearTimeout(toast._timeout);
  toast._timeout = setTimeout(() => toast.classList.remove('show'), 3000);
}

// ─── Init: adjuntar listeners cuando se abre cada modal ────────
document.addEventListener('DOMContentLoaded', () => {

  // Suscripción
  const subForm = document.getElementById('subscribe-form');
  if (subForm) {
    subForm.addEventListener('submit', e => { e.preventDefault(); handleSubscribe(subForm); });
  }

  // Modales de charlas
  document.querySelectorAll('[data-event-id]').forEach(modalEl => {
    const eventId = parseInt(modalEl.dataset.eventId);

    // Reacción
    const reactBtn = modalEl.querySelector('.blog-react-btn');
    if (reactBtn) {
      loadReactions(eventId, reactBtn);
      reactBtn.addEventListener('click', () => toggleReaction(eventId, reactBtn));
    }

    // Comentarios: cargar al abrir el modal
    const commentsContainer = modalEl.querySelector('.blog-comments-list');
    const textarea = modalEl.querySelector('.blog-comment-input');
    const sendBtn = modalEl.querySelector('.blog-send-btn');

    modalEl.addEventListener('shown.bs.modal', () => {
      if (commentsContainer) loadComments(eventId, commentsContainer);
    });

    if (sendBtn && textarea && commentsContainer) {
      sendBtn.addEventListener('click', () => submitComment(eventId, textarea, commentsContainer));
      textarea.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          submitComment(eventId, textarea, commentsContainer);
        }
      });
    }
  });
});
