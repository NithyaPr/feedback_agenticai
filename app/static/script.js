const PRESETS = {
    'default-light': {
        theme: 'light',
        primary: '#6366f1',
        bg: '#f5f7fa',
        surface: '#ffffff',
        text: '#1f2937',
        userBubble: '#6366f1',
        botBubble: '#e5e7eb'
    },
    'default-dark': {
        theme: 'dark',
        primary: '#818cf8',
        bg: '#1a1a2e',
        surface: '#16213e',
        text: '#e5e7eb',
        userBubble: '#818cf8',
        botBubble: '#374151'
    },
    'ocean': {
        theme: 'ocean',
        primary: '#60a5fa',
        bg: '#1e3a5f',
        surface: '#2d5a87',
        text: '#f1f5f9',
        userBubble: '#60a5fa',
        botBubble: '#1e40af'
    },
    'forest': {
        theme: 'forest',
        primary: '#4ade80',
        bg: '#1a2f1a',
        surface: '#2d4a2d',
        text: '#f1f5f9',
        userBubble: '#4ade80',
        botBubble: '#14532d'
    }
};

let currentTheme = JSON.parse(localStorage.getItem('themeSettings')) || {
    mode: 'light',
    primary: '#6366f1',
    bg: '#f5f7fa',
    surface: '#ffffff',
    text: '#1f2937',
    userBubble: '#6366f1',
    botBubble: '#e5e7eb'
};

function applyTheme() {
    const root = document.documentElement;
    if (currentTheme.mode === 'dark') {
        root.setAttribute('data-theme', 'dark');
    } else if (currentTheme.mode === 'ocean') {
        root.setAttribute('data-theme', 'ocean');
    } else if (currentTheme.mode === 'forest') {
        root.setAttribute('data-theme', 'forest');
    } else {
        root.removeAttribute('data-theme');
    }

    root.style.setProperty('--primary-color', currentTheme.primary);
    root.style.setProperty('--bg-color', currentTheme.bg);
    root.style.setProperty('--surface-color', currentTheme.surface);
    root.style.setProperty('--text-primary', currentTheme.text);
    root.style.setProperty('--user-bubble', currentTheme.userBubble);
    root.style.setProperty('--bot-bubble', currentTheme.botBubble);

    document.getElementById('primaryColor').value = currentTheme.primary;
    document.getElementById('bgColor').value = currentTheme.bg;
    document.getElementById('surfaceColor').value = currentTheme.surface;
    document.getElementById('textColor').value = currentTheme.text;
    document.getElementById('userBubbleColor').value = currentTheme.userBubble;
    document.getElementById('botBubbleColor').value = currentTheme.botBubble;

    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === currentTheme.mode);
    });
}

function saveTheme() {
    localStorage.setItem('themeSettings', JSON.stringify(currentTheme));
}

function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            const targetId = `${tab.dataset.tab}-section`;
            document.getElementById(targetId).classList.add('active');
        });
    });
}

function initNpsSlider() {
    const npsSlider = document.getElementById('npsScore');
    const npsValueDisplay = document.getElementById('npsValue');

    npsSlider.addEventListener('input', () => {
        npsValueDisplay.textContent = npsSlider.value;
    });
}

function initFeedbackForm() {
    const form = document.getElementById('feedbackForm');
    const responseBox = document.getElementById('feedbackResponse');
    const responseText = document.getElementById('responseText');
    const responseCategories = document.getElementById('responseCategories');
    const categoryTags = document.getElementById('categoryTags');
    const responseNps = document.getElementById('responseNps');
    const npsScoreDisplay = document.getElementById('npsScoreDisplay');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const npsScore = parseInt(document.getElementById('npsScore').value);

        const formData = {
            product: document.getElementById('product').value,
            feedback_text: document.getElementById('feedbackText').value,
            nps_score: npsScore,
            user_id: document.getElementById('userId').value || null
        };

        responseBox.classList.remove('hidden', 'success', 'error');
        responseBox.style.display = 'block';
        responseText.textContent = 'Submitting feedback...';
        responseCategories.classList.add('hidden');
        responseNps.classList.add('hidden');

        try {
            const response = await fetch('/api/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.success) {
                responseBox.classList.add('success');
                responseText.innerHTML = `<strong>Thank you for your feedback!</strong><br><br>${result.llm_response}`;

                if (result.categories && result.categories.length > 0) {
                    categoryTags.innerHTML = result.categories.map(cat =>
                        `<span class="category-tag">${cat}</span>`
                    ).join('');
                    responseCategories.classList.remove('hidden');
                }

                npsScoreDisplay.textContent = result.nps_score;
                responseNps.classList.remove('hidden');

                form.reset();
                document.getElementById('npsScore').value = 5;
                document.getElementById('npsValue').textContent = '5';
            } else {
                responseBox.classList.add('error');
                responseText.textContent = `Error: ${result.message}`;
            }
        } catch (error) {
            responseBox.classList.add('error');
            responseText.textContent = `Error: ${error.message}`;
        }
    });
}

function initChat() {
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendChat');
    const chatMessages = document.getElementById('chatMessages');
    const productFilter = document.getElementById('chatProductFilter');
    const minNps = document.getElementById('minNps');
    const maxNps = document.getElementById('maxNps');
    const categoryFilter = document.getElementById('categoryFilter');

    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        addMessage(message, 'user');
        chatInput.value = '';

        const typingIndicator = addTypingIndicator();

        const chatRequest = {
            message: message,
            product_filter: productFilter.value || null
        };

        if (minNps.value) {
            chatRequest.min_nps = parseInt(minNps.value);
        }
        if (maxNps.value) {
            chatRequest.max_nps = parseInt(maxNps.value);
        }
        if (categoryFilter.value) {
            chatRequest.categories = [categoryFilter.value];
        }

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(chatRequest)
            });

            const result = await response.json();
            typingIndicator.remove();

            if (result.success) {
                addMessage(result.response, 'bot');
            } else {
                addMessage(`Error: ${result.response}`, 'bot');
            }
        } catch (error) {
            typingIndicator.remove();
            addMessage(`Error: ${error.message}`, 'bot');
        }
    }

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.innerHTML = `<div class="message-content">${text}</div>`;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addTypingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        messageDiv.id = 'typingIndicator';
        messageDiv.innerHTML = `<div class="typing-indicator"><span></span><span></span><span></span></div>`;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return messageDiv;
    }

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

function initSettings() {
    const modal = document.getElementById('settingsModal');
    const openBtn = document.getElementById('settingsBtn');
    const closeBtn = document.getElementById('closeSettings');
    const resetBtn = document.getElementById('resetTheme');

    openBtn.addEventListener('click', () => {
        modal.classList.remove('hidden');
    });

    closeBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.add('hidden');
        }
    });

    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            currentTheme.mode = btn.dataset.mode;
            applyTheme();
            saveTheme();
        });
    });

    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const preset = PRESETS[btn.dataset.preset];
            currentTheme = {
                ...currentTheme,
                mode: preset.theme,
                primary: preset.primary,
                bg: preset.bg,
                surface: preset.surface,
                text: preset.text,
                userBubble: preset.userBubble,
                botBubble: preset.botBubble
            };
            applyTheme();
            saveTheme();
        });
    });

    const colorInputs = ['primaryColor', 'bgColor', 'surfaceColor', 'textColor', 'userBubbleColor', 'botBubbleColor'];
    const themeKeys = ['primary', 'bg', 'surface', 'text', 'userBubble', 'botBubble'];

    colorInputs.forEach((inputId, index) => {
        document.getElementById(inputId).addEventListener('input', (e) => {
            currentTheme[themeKeys[index]] = e.target.value;
            applyTheme();
            saveTheme();
        });
    });

    resetBtn.addEventListener('click', () => {
        currentTheme = {
            mode: 'light',
            primary: '#6366f1',
            bg: '#f5f7fa',
            surface: '#ffffff',
            text: '#1f2937',
            userBubble: '#6366f1',
            botBubble: '#e5e7eb'
        };
        applyTheme();
        saveTheme();
    });
}

function initProviderSettings() {
    const llmProvider = document.getElementById('llmProvider');
    const embeddingProvider = document.getElementById('embeddingProvider');
    const llmProviderInfo = document.getElementById('llmProviderInfo');
    const embeddingProviderInfo = document.getElementById('embeddingProviderInfo');
    const providerStatus = document.getElementById('providerStatus');

    const providerModels = {
        'ollama': {
            'llm': 'llama3.2:1b',
            'embedding': 'nomic-embed-text'
        },
        'openai': {
            'llm': 'gpt-4o-mini',
            'embedding': 'text-embedding-3-small'
        },
        'google': {
            'llm': 'gemini-2.0-flash',
            'embedding': 'text-embedding-004'
        }
    };

    function updateProviderInfo() {
        const llm = llmProvider.value;
        const embedding = embeddingProvider.value;

        llmProviderInfo.textContent = `Model: ${providerModels[llm].llm}`;
        embeddingProviderInfo.textContent = `Model: ${providerModels[embedding].embedding}`;
    }

    function validateProviders() {
        let messages = [];

        if (llmProvider.value === 'ollama') {
            messages.push('Chat: Using Ollama (local). Ensure Ollama server is running.');
        } else if (llmProvider.value === 'openai') {
            messages.push('Chat: Using OpenAI (cloud).');
        } else if (llmProvider.value === 'google') {
            messages.push('Chat: Using Google Gemini (cloud).');
        }

        if (embeddingProvider.value === 'ollama') {
            messages.push('Embedding: Using Ollama (local).');
        } else if (embeddingProvider.value === 'openai') {
            messages.push('Embedding: Using OpenAI (cloud).');
        } else if (embeddingProvider.value === 'google') {
            messages.push('Embedding: Using Google (cloud).');
        }

        if (llmProvider.value === 'ollama' || embeddingProvider.value === 'ollama') {
            providerStatus.className = 'provider-status warning';
            providerStatus.textContent = '⚠️ Ollama selected. Please ensure Ollama server is running at http://localhost:11434';
        } else {
            providerStatus.className = 'provider-status success';
            providerStatus.textContent = '✓ Using cloud providers. Configuration OK.';
        }
    }

    llmProvider.addEventListener('change', () => {
        updateProviderInfo();
        validateProviders();
    });

    embeddingProvider.addEventListener('change', () => {
        updateProviderInfo();
        validateProviders();
    });

    updateProviderInfo();
    validateProviders();
}

document.addEventListener('DOMContentLoaded', () => {
    applyTheme();
    initTabs();
    initNpsSlider();
    initFeedbackForm();
    initChat();
    initSettings();
    initProviderSettings();
});