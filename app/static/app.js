const messages = document.getElementById('messages');
const form = document.getElementById('chat-form');
const questionInput = document.getElementById('question');
const sendButton = document.getElementById('send-button');

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
      const card = document.createElement('div');
      card.className = 'citation';
      card.innerHTML = `
        <div class="citation-head">
          <span>${escapeHtml(source.reporting_period)}</span>
          <span>${escapeHtml(source.section || 'Source')}</span>
        </div>
        <div class="citation-body">
          <strong>${escapeHtml(source.summary_file)}</strong><br />
          ${escapeHtml(source.excerpt)}
        </div>
      `;
      citations.appendChild(card);
    });

    bubble.appendChild(citations);
  }

  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
}

async function ask(question) {
  const response = await fetch('/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json();
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) {
    return;
  }

  renderMessage('user', question);
  questionInput.value = '';
  sendButton.disabled = true;
  sendButton.textContent = 'Thinking...';

  try {
    const payload = await ask(question);
    console.log('API Response:', payload);
    console.log('Provider:', payload.provider);
    renderMessage('assistant', payload.answer, payload.sources || [], { provider: payload.provider });
  } catch (error) {
    renderMessage('assistant', 'Something went wrong while answering that question.');
  } finally {
    sendButton.disabled = false;
    sendButton.textContent = 'Ask';
    questionInput.focus();
  }
});

document.querySelectorAll('.chip').forEach((button) => {
  button.addEventListener('click', () => {
    questionInput.value = button.dataset.question || '';
    questionInput.focus();
  });
});