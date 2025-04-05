// Theme toggle functionality
const themeToggle = document.getElementById('themeToggle');
const html = document.documentElement;

// Check for saved theme preference
const currentTheme = localStorage.getItem('theme') || 'light';
html.setAttribute('data-theme', currentTheme);

themeToggle.addEventListener('click', () => {
    const newTheme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon();
});

function updateThemeIcon() {
    const icon = themeToggle.querySelector('i');
    if (html.getAttribute('data-theme') === 'dark') {
        icon.classList.replace('fa-moon', 'fa-sun');
    } else {
        icon.classList.replace('fa-sun', 'fa-moon');
    }
}

// Chat functionality
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const chatContainer = document.getElementById('chat-container');
const voiceBtn = document.getElementById('voice-btn');
const quickReplies = document.querySelectorAll('.quick-reply');
const imageUploadSection = document.getElementById('image-upload-section');
const uploadBtn = document.getElementById('upload-btn');

// Handle sending messages
async function sendMessage() {
    const message = chatInput.value.trim();
    if (message) {
        addMessageToChat(message, 'user');
        chatInput.value = '';
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });
            
            if (response.ok) {
                const data = await response.json();
                addMessageToChat(data.response, 'bot');
            } else {
                throw new Error('Failed to get response');
            }
        } catch (error) {
            addMessageToChat("Sorry, I'm having trouble responding. Please try again.", 'bot');
            console.error('Chat error:', error);
        }
    }
}

// Add message to chat container
function addMessageToChat(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message fade-in`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = sender === 'user' 
        ? 'bg-blue-500 text-white rounded-lg p-3 inline-block' 
        : 'bg-blue-100 dark:bg-gray-700 rounded-lg p-3 inline-block';
    contentDiv.textContent = message;
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Event listeners
sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Voice recognition
if ('webkitSpeechRecognition' in window) {
    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    
    voiceBtn.addEventListener('click', () => {
        recognition.start();
        voiceBtn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
    });
    
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        chatInput.value = transcript;
        voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
    };
    
    recognition.onerror = () => {
        voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
    };
} else {
    voiceBtn.style.display = 'none';
}

// Quick replies
quickReplies.forEach(button => {
    button.addEventListener('click', () => {
        const action = button.textContent;
        addMessageToChat(action, 'user');
        
        // Handle different quick reply actions
        if (action === 'Upload Image') {
            imageUploadSection.classList.remove('d-none');
        } else {
            // Simulate response
            setTimeout(() => {
                addMessageToChat(`You selected: ${action}. How can I help with this?`, 'bot');
            }, 800);
        }
    });
});

// Image upload handling
uploadBtn.addEventListener('click', async () => {
    const fileInput = document.getElementById('injury-image');
    if (fileInput.files.length > 0) {
        const formData = new FormData();
        formData.append('image', fileInput.files[0]);
        
        addMessageToChat("Analyzing your injury image...", 'user');
        
        try {
            const response = await fetch('/api/analyze-image', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                addMessageToChat(`I detect a ${data.injury_type}. ${data.first_aid}`, 'bot');
            } else {
                throw new Error('Failed to analyze image');
            }
        } catch (error) {
            addMessageToChat("Sorry, I couldn't analyze the image. Please try again.", 'bot');
            console.error('Image analysis error:', error);
        }
        
        imageUploadSection.classList.add('d-none');
    }
});

// Register Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/js/sw.js')
      .then(registration => {
        console.log('ServiceWorker registered with scope:', registration.scope);
      })
      .catch(err => {
        console.log('ServiceWorker registration failed:', err);
      });
  });
}

// Initialize theme icon
updateThemeIcon();
