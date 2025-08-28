const TONES = [
  { key: 'Confident', desc: 'Direct and assertive', emoji: '💪' },
  { key: 'Kind', desc: 'Warm and gentle', emoji: '🤗' },
  { key: 'Flirty', desc: 'Playful and charming', emoji: '😉' },
  { key: 'Professional', desc: 'Polished and courteous', emoji: '👔' },
  { key: 'Gen Z', desc: 'Cool and trendy', emoji: '✨' },
];

// DOM elements
const tonesEl = document.getElementById('tones');
const messageEl = document.getElementById('message');
const situationEl = document.getElementById('situation');
const customSituationContainer = document.getElementById('customSituationContainer');
const customSituationInput = document.getElementById('customSituation');
const resultsEl = document.getElementById('results');
const errorEl = document.getElementById('error');
const generateBtn = document.getElementById('generate');

let currentTone = 'Flirty';

// Initialize the app
function init() {
  renderTones();
  setupEventListeners();
}

// Render tone buttons
function renderTones() {
  tonesEl.innerHTML = '';
  TONES.forEach(t => {
    const btn = document.createElement('button');
    btn.className = 'tone' + (t.key === currentTone ? ' active' : '');
    btn.innerHTML = `${t.emoji} ${t.key}`; // Using innerHTML to render emoji
    btn.title = t.desc;
    btn.addEventListener('click', () => {
      currentTone = t.key;
      renderTones();
    });
    tonesEl.appendChild(btn);
  });
}

// Setup all event listeners
function setupEventListeners() {
  // Situation dropdown change
  situationEl.addEventListener('change', handleSituationChange);
  
  // Generate button click
  generateBtn.addEventListener('click', handleGenerate);
  
  // Custom situation input
  customSituationInput.addEventListener('input', handleCustomSituationInput);
  
  // Copy results on click
  resultsEl.addEventListener('click', handleResultClick);
}

// Handle situation dropdown change
function handleSituationChange() {
  const selectedValue = situationEl.value;
  if (selectedValue === 'custom') {
    customSituationContainer.style.display = 'block';
    customSituationInput.focus();
    customSituationInput.value = ''; // Clear any previous value
  } else {
    customSituationContainer.style.display = 'none';
    customSituationInput.value = '';
  }
}

// Handle custom situation input
function handleCustomSituationInput(event) {
  // Ensure the input is working
  console.log('Custom input value:', event.target.value);
}

// Handle generate button click
async function handleGenerate() {
  errorEl.textContent = '';
  resultsEl.innerHTML = '';
  
  const message = messageEl.value.trim();
  if (!message) {
    errorEl.textContent = 'Please enter a message to generate a response for.';
    return;
  }
  
  // Get the situation value
  let situation = situationEl.value;
  if (situation === 'custom') {
    situation = customSituationInput.value.trim();
    if (!situation) {
      errorEl.textContent = 'Please describe your custom situation.';
      return;
    }
  }
  
  const payload = {
    message: message,
    situation: situation,
    tone: currentTone,
  };
  
  try {
    generateBtn.disabled = true;
    generateBtn.textContent = 'Generating...';
    
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    
    const data = await res.json();
    
    if (!res.ok) {
      throw new Error(data.error || 'Request failed');
    }
    
    // Display results
    (data.options || []).slice(0, 3).forEach((text, index) => {
      const div = document.createElement('div');
      div.className = 'option';
      div.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-shrink: 0;">
          <strong>Option ${index + 1}</strong>
          <span style="color: var(--muted); font-size: 12px;">Click to copy</span>
        </div>
        <div style="flex: 1; overflow: hidden; word-wrap: break-word;">${text}</div>
      `;
      div.dataset.text = text;
      resultsEl.appendChild(div);
    });
    
  } catch (e) {
    errorEl.textContent = e.message || String(e);
  } finally {
    generateBtn.disabled = false;
    generateBtn.textContent = 'Get Response';
  }
}

// Handle result click for copying
function handleResultClick(event) {
  const option = event.target.closest('.option');
  if (option && option.dataset.text) {
    navigator.clipboard.writeText(option.dataset.text).then(() => {
      // Show feedback
      const originalText = option.innerHTML;
      option.innerHTML = `
        <div style="color: var(--primary); text-align: center; padding: 20px;">
          ✓ Copied to clipboard!
        </div>
      `;
      setTimeout(() => {
        option.innerHTML = originalText;
      }, 1500);
    }).catch(err => {
      console.error('Failed to copy:', err);
      errorEl.textContent = 'Failed to copy to clipboard. Please copy manually.';
    });
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', init);