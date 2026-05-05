const messages = document.getElementById('messages');
const form = document.getElementById('chat-form');
const questionInput = document.getElementById('question');
const sendButton = document.getElementById('send-button');
let loadingMessage = null;

function setComposerState(isBusy, label = 'Ask') {
  sendButton.disabled = isBusy;
  sendButton.textContent = isBusy ? 'Thinking...' : label;
  questionInput.disabled = isBusy;
  form.setAttribute('aria-busy', String(isBusy));
}

function describeProvider(provider) {
  if (provider === 'openai') {
    const model = window.OPENAI_MODEL ? ` (${window.OPENAI_MODEL})` : '';
    return `Answered by OpenAI${model}`;
  }

  if (provider === 'extractive') {
    return 'Answered from retrieved sources';
  }

  if (provider === 'none') {
    return 'No relevant corpus match';
  }

  return provider ? `Answered by ${provider}` : '';
}

function escapeHtml(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function renderMessage(role, text, sources = [], meta = null) {
  const article = document.createElement('article');
  article.className = `message ${role}`;

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = escapeHtml(text).replaceAll('\n', '<br />');

  article.appendChild(bubble);

  if (role === 'assistant' && meta?.provider) {
    const answerMeta = document.createElement('div');
    answerMeta.className = 'answer-meta';
    answerMeta.textContent = describeProvider(meta.provider);
    bubble.appendChild(answerMeta);
  }

  if (sources.length) {
    const citations = document.createElement('div');
    citations.className = 'citations';

    sources.forEach((source) => {
      const card = document.createElement('details');
      card.className = 'citation';
      card.innerHTML = `
        <summary class="citation-head">
          <span class="citation-label">${escapeHtml(source.citation_label || `${source.reporting_period} | ${source.source_file}`)}</span>
          <span class="citation-file">Open source</span>
        </summary>
        <div class="citation-body">
          <div class="citation-meta">${escapeHtml(source.summary_file)}</div>
          <div class="citation-excerpt">${escapeHtml(source.excerpt)}</div>
          <div class="citation-actions">
            <a class="citation-link" href="/preview/${encodeURIComponent(source.document_id)}" target="_blank" rel="noreferrer">Open read-only preview</a>
          </div>
        </div>
      `;
      citations.appendChild(card);
    });

    bubble.appendChild(citations);
  }

  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;

  return article;
}

function renderLoadingMessage() {
  const article = document.createElement('article');
  article.className = 'message assistant loading';
  article.setAttribute('role', 'status');
  article.setAttribute('aria-live', 'polite');

  const bubble = document.createElement('div');
  bubble.className = 'bubble loading-bubble';
  bubble.innerHTML = `
    <span class="loading-label">Searching the corpus</span>
    <span class="loading-dots" aria-hidden="true">
      <span></span><span></span><span></span>
    </span>
  `;

  article.appendChild(bubble);
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;

  return article;
}

function clearLoadingMessage() {
  if (loadingMessage) {
    loadingMessage.remove();
    loadingMessage = null;
  }
}

function renderFailureMessage(message, detail = '') {
  const article = document.createElement('article');
  article.className = 'message assistant error-message';

  const bubble = document.createElement('div');
  bubble.className = 'bubble error-bubble';
  bubble.innerHTML = `
    <div class="error-title">${escapeHtml(message)}</div>
    ${detail ? `<div class="error-detail">${escapeHtml(detail)}</div>` : ''}
    <div class="error-actions">
      <button type="button" class="retry-button">Try again</button>
    </div>
  `;

  article.appendChild(bubble);
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;

  bubble.querySelector('.retry-button')?.addEventListener('click', () => {
    article.remove();
    questionInput.focus();
  });

  return article;
}

async function ask(question) {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), 30000);

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
      signal: controller.signal,
    });

    if (!response.ok) {
      const error = new Error(`Request failed with status ${response.status}`);
      error.status = response.status;
      throw error;
    }

    return response.json();
  } finally {
    window.clearTimeout(timeoutId);
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) {
    return;
  }

  renderMessage('user', question);
  const draft = questionInput.value;
  questionInput.value = '';
  loadingMessage = renderLoadingMessage();
  setComposerState(true);

  try {
    const payload = await ask(question);
    clearLoadingMessage();

    if (payload.out_of_scope) {
      renderMessage(
        'assistant',
        'I could not find enough support in the corpus for that question. Try narrowing the time period or asking about a specific report section.',
        payload.sources || [],
        { provider: payload.provider },
      );
      return;
    }

    renderMessage('assistant', payload.answer, payload.sources || [], { provider: payload.provider });
  } catch (error) {
    clearLoadingMessage();

    const isTimeout = error?.name === 'AbortError';
    const status = error?.status;
    const message = isTimeout
      ? 'That request timed out before the app could finish searching the corpus.'
      : status === 422
        ? 'That question was rejected before it reached the retriever.'
        : status && status >= 500
          ? 'The server hit an error while answering that question.'
          : 'Something went wrong while answering that question.';

    renderFailureMessage(message, 'Your question has been kept in the box so you can edit and retry it.');
    questionInput.value = draft;
  } finally {
    setComposerState(false);
    questionInput.focus();
  }
});

document.querySelectorAll('.chip').forEach((button) => {
  button.addEventListener('click', () => {
    questionInput.value = button.dataset.question || '';
    questionInput.focus();
  });
});