const messages = document.getElementById('messages');
const form = document.getElementById('chat-form');
const questionInput = document.getElementById('question');
const sendButton = document.getElementById('send-button');
let loadingMessage = null;

function getAnswerConfidence(sources = [], provider = '') {
  if (!sources.length) {
    return provider === 'none' ? 'No support' : '';
  }

  const topScore = Math.max(...sources.map((source) => Number(source.score) || 0));
  if (topScore >= 0.45) {
    return 'Strong support';
  }
  if (topScore >= 0.25) {
    return 'Moderate support';
  }
  return '';
}

function buildFollowUps(question, sources = [], provider = '') {
  const questionText = (question || '').toLowerCase();
  const topSource = sources[0];
  const period = topSource?.reporting_period || '';
  const base = [];

  if (questionText.includes('valuation')) {
    base.push('Compare valuations to the prior quarter');
  } else if (questionText.includes('strategy')) {
    base.push('How did the strategy change year over year?');
  } else if (questionText.includes('credit facility')) {
    base.push('Summarize the credit facility usage trend');
  } else if (questionText.includes('nav')) {
    base.push('What drove the NAV change in this period?');
  } else {
    base.push('Compare this answer with the prior period');
  }

  if (period) {
    base.push(`Show other sources from ${period}`);
  }

  return base.slice(0, 3);
}

function copyText(text) {
  if (navigator.clipboard?.writeText) {
    return navigator.clipboard.writeText(text);
  }

  const fallback = document.createElement('textarea');
  fallback.value = text;
  fallback.setAttribute('readonly', 'true');
  fallback.style.position = 'absolute';
  fallback.style.left = '-9999px';
  document.body.appendChild(fallback);
  fallback.select();
  document.execCommand('copy');
  fallback.remove();
  return Promise.resolve();
}

function bindCopyButton(button, text, successLabel = 'Copied') {
  button.addEventListener('click', async () => {
    const original = button.textContent;
    try {
      await copyText(text);
      button.textContent = successLabel;
      window.setTimeout(() => {
        button.textContent = original;
      }, 1400);
    } catch (error) {
      button.textContent = 'Copy failed';
      window.setTimeout(() => {
        button.textContent = original;
      }, 1400);
    }
  });
}

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

  if (role === 'assistant') {
    const header = document.createElement('div');
    header.className = 'message-toolbar';

    const copyButton = document.createElement('button');
    copyButton.type = 'button';
    copyButton.className = 'copy-button';
    copyButton.textContent = 'Copy answer';
    copyButton.style.marginLeft = 'auto';
    bindCopyButton(copyButton, text);

    header.appendChild(copyButton);
    bubble.appendChild(header);
  }

  if (role === 'assistant' && meta?.provider) {
    const answerMeta = document.createElement('div');
    answerMeta.className = 'answer-meta';
    answerMeta.textContent = describeProvider(meta.provider);
    bubble.appendChild(answerMeta);
  }

  if (sources.length) {
    const filteredSources = sources.filter(s => (Number(s.score) || 0) >= 0.25);
    const visibleSources = filteredSources.length ? filteredSources : sources.slice(0, 1);
    
    if (visibleSources.length) {
      const citationsHeader = document.createElement('div');
      citationsHeader.className = 'citations-header';
      citationsHeader.textContent = 'Sources';
      bubble.appendChild(citationsHeader);

      const citations = document.createElement('div');
      citations.className = 'citations';

      visibleSources.forEach((source) => {
      const card = document.createElement('details');
      card.className = 'citation';
      card.innerHTML = `
        <summary class="citation-head">
          <span class="citation-label">${escapeHtml(source.citation_label || `${source.reporting_period} | ${source.source_file}`)}</span>
        </summary>
        <div class="citation-body">
          <div class="citation-meta">${escapeHtml(source.summary_file)}</div>
          <div class="citation-excerpt">${escapeHtml(source.excerpt)}</div>
          <div class="citation-actions">
            <button type="button" class="copy-button copy-citation-button">Copy citation</button>
          </div>
        </div>
      `;
      const copyCitationButton = card.querySelector('.copy-citation-button');
      if (copyCitationButton) {
        bindCopyButton(
          copyCitationButton,
          `${source.citation_label || `${source.reporting_period} | ${source.source_file}`}\n${source.summary_file}\n${source.excerpt}`,
          'Copied citation',
        );
      }
      citations.appendChild(card);
      });

      bubble.appendChild(citations);
    }
  }

  if (role === 'assistant') {
    const followUps = document.createElement('div');
    followUps.className = 'follow-up-section';
    
    const followUpLabel = document.createElement('div');
    followUpLabel.className = 'follow-up-label';
    followUpLabel.textContent = 'Suggested follow-up questions:';
    followUps.appendChild(followUpLabel);
    
    const followUpRow = document.createElement('div');
    followUpRow.className = 'follow-up-row';
    const suggestions = buildFollowUps(meta?.question || '', sources, meta?.provider);

    suggestions.forEach((suggestion) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'follow-up-chip';
      button.textContent = suggestion;
      button.addEventListener('click', () => {
        questionInput.value = suggestion;
        questionInput.focus();
      });
      followUpRow.appendChild(button);
    });
    
    followUps.appendChild(followUpRow);
    bubble.appendChild(followUps);
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
        payload.answer || 'I could not find enough support in the corpus for that question. Try narrowing the time period or asking about a specific report section.',
        payload.sources || [],
        { provider: payload.provider, question },
      );
      return;
    }

    renderMessage('assistant', payload.answer, payload.sources || [], { provider: payload.provider, question });
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