// Global variables
let userInfo = null;
let apiKey = localStorage.getItem('geminiApiKey');
let userAuthenticated = false;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuthStatus();
    observeElements();
    console.log('CodeMate AI Website loaded successfully!');
});

// Auth Modal Functions
function showAuthModal() {
    document.getElementById('authModal').style.display = 'block';
}

function closeAuthModal() {
    document.getElementById('authModal').style.display = 'none';
}

function checkAuthStatus() {
    const savedUser = localStorage.getItem('codemate_user');
    if (savedUser) {
        userInfo = JSON.parse(savedUser);
        userAuthenticated = true;
        showUserProfile();
    } else {
        userAuthenticated = false;
        showLoginButton();
    }
    updateDemoSection();
}

function showUserProfile() {
    document.getElementById('loginBtn').style.display = 'none';
    document.getElementById('userProfile').style.display = 'flex';
    document.getElementById('userName').textContent = userInfo.name || 'User';
    if (userInfo.picture) {
        document.getElementById('userAvatar').src = userInfo.picture;
    }
}

function showLoginButton() {
    document.getElementById('loginBtn').style.display = 'block';
    document.getElementById('userProfile').style.display = 'none';
}

// Google Login
function handleGoogleLogin() {
    // For production, implement proper OAuth flow
    const email = prompt('Enter your Google email:');
    if (email) {
        userInfo = {
            email: email,
            name: email.split('@')[0],
            provider: 'google',
            picture: `https://ui-avatars.com/api/?name=${email.split('@')[0]}&background=667eea&color=fff`
        };
        localStorage.setItem('codemate_user', JSON.stringify(userInfo));
        userAuthenticated = true;
        closeAuthModal();
        showUserProfile();
        updateDemoSection();
        alert(`Welcome ${userInfo.name}! You can now use the AI analyzer.`);
    }
}

// GitHub Login
function handleGithubLogin() {
    // For production, implement proper OAuth flow with GitHub
    const username = prompt('Enter your GitHub username:');
    if (username) {
        userInfo = {
            username: username,
            name: username,
            provider: 'github',
            picture: `https://github.com/${username}.png?size=100`
        };
        localStorage.setItem('codemate_user', JSON.stringify(userInfo));
        userAuthenticated = true;
        closeAuthModal();
        showUserProfile();
        updateDemoSection();
        alert(`Welcome ${username}! You can now use the AI analyzer.`);
    }
}

// Set API Key
function setApiKey() {
    const key = document.getElementById('apiKeyInput').value.trim();
    if (key) {
        apiKey = key;
        localStorage.setItem('geminiApiKey', key);
        userInfo = {
            name: 'API User',
            provider: 'api_key',
            picture: 'https://ui-avatars.com/api/?name=API+User&background=667eea&color=fff'
        };
        localStorage.setItem('codemate_user', JSON.stringify(userInfo));
        userAuthenticated = true;
        closeAuthModal();
        showUserProfile();
        updateDemoSection();
        alert('✓ API Key set successfully! You can now use the real AI analyzer.');
    } else {
        alert('Please enter a valid API key');
    }
}

function logout() {
    localStorage.removeItem('codemate_user');
    localStorage.removeItem('geminiApiKey');
    userInfo = null;
    apiKey = null;
    userAuthenticated = false;
    showLoginButton();
    updateDemoSection();
    alert('You have been logged out.');
}

function updateDemoSection() {
    const authRequired = document.getElementById('authRequired');
    const demoContainer = document.getElementById('demoContainer');
    
    if (userAuthenticated && apiKey) {
        authRequired.style.display = 'none';
        demoContainer.style.display = 'grid';
    } else {
        authRequired.style.display = 'block';
        demoContainer.style.display = 'none';
    }
}

// Real AI Analysis with Google Gemini
async function analyzeCodeWithAI() {
    if (!apiKey) {
        alert('Please set your Gemini API Key first');
        showAuthModal();
        return;
    }

    const code = document.getElementById('codeInput').value.trim();
    const language = document.getElementById('languageSelect').value;
    const task = document.getElementById('taskSelect').value;
    const outputBox = document.getElementById('demoOutput');
    const spinner = document.getElementById('loadingSpinner');
    const analyzeBtn = document.getElementById('analyzeBtn');

    if (!code) {
        outputBox.innerHTML = '<p style="color: #e53e3e;"><i class="fas fa-exclamation-circle"></i> Please enter some code first.</p>';
        return;
    }

    spinner.style.display = 'block';
    analyzeBtn.disabled = true;
    outputBox.innerHTML = '';

    try {
        const prompt = buildAIPrompt(code, language, task);
        
        // Using fetch API to call Gemini API
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${apiKey}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                contents: [
                    {
                        parts: [
                            {
                                text: prompt
                            }
                        ]
                    }
                ]
            })
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();
        const aiResponse = data.candidates[0].content.parts[0].text;
        
        displayAIAnalysis(aiResponse, task);
    } catch (error) {
        console.error('AI Analysis Error:', error);
        outputBox.innerHTML = `<p style="color: #e53e3e;"><i class="fas fa-exclamation-circle"></i> Error: ${error.message}</p>
                               <p style="color: #a0aec0; font-size: 0.9rem;">Make sure your Gemini API key is valid. Get one from: <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener">Google AI Studio</a></p>`;
    } finally {
        spinner.style.display = 'none';
        analyzeBtn.disabled = false;
    }
}

function buildAIPrompt(code, language, task) {
    const prompts = {
        analyze: `Analyze this ${language} code and provide:
1. Code quality assessment
2. Complexity analysis
3. Best practices feedback
4. Potential improvements

Code:\n\`\`\`${language}\n${code}\n\`\`\``,
        
        debug: `Find bugs and issues in this ${language} code. List each issue with:
1. Issue description
2. Severity level (High/Medium/Low)
3. Suggested fix

Code:\n\`\`\`${language}\n${code}\n\`\`\``,
        
        refactor: `Suggest refactoring improvements for this ${language} code:
1. Current structure issues
2. Proposed improvements
3. Refactored code example

Code:\n\`\`\`${language}\n${code}\n\`\`\``,
        
        optimize: `Optimize this ${language} code for performance. Provide:
1. Performance bottlenecks
2. Time complexity analysis
3. Optimized version
4. Performance improvement estimates

Code:\n\`\`\`${language}\n${code}\n\`\`\``,
        
        document: `Add comprehensive documentation to this ${language} code. Include:
1. Function/class descriptions
2. Parameter documentation
3. Return value documentation
4. Usage examples

Code:\n\`\`\`${language}\n${code}\n\`\`\``,
        
        test: `Generate unit tests for this ${language} code. Create:
1. Test cases covering main functionality
2. Edge case tests
3. Error handling tests
4. Example test code

Code:\n\`\`\`${language}\n${code}\n\`\`\``
    };

    return prompts[task] || prompts.analyze;
}

function displayAIAnalysis(response, task) {
    const outputBox = document.getElementById('demoOutput');
    const taskIcons = {
        analyze: '🔍',
        debug: '🐛',
        refactor: '♻️',
        optimize: '⚡',
        document: '📝',
        test: '✅'
    };

    const icon = taskIcons[task] || '✓';
    outputBox.innerHTML = `
        <div style="animation: fadeInUp 0.5s ease-out;">
            <h4 style="color: #4299e1; margin-bottom: 1rem;"><i class="fas fa-check-circle"></i> ${icon} AI Analysis Complete</h4>
            <div style="text-align: left; font-size: 0.95rem; line-height: 1.8; white-space: pre-wrap; word-wrap: break-word; color: #68d391;">
                ${response.split('\n').map(line => `<div>${line}</div>`).join('')}
            </div>
            <p style="margin-top: 1rem; color: #a0aec0; font-size: 0.85rem;"><em>Powered by Google Gemini AI</em></p>
        </div>
    `;
}

// Form Submissions
function handleFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = {
        name: form.querySelector('input[type="text"]').value,
        email: form.querySelector('input[type="email"]').value,
        subject: form.querySelectorAll('input[type="text"]')[1].value,
        message: form.querySelector('textarea').value
    };
    
    console.log('Form submitted:', formData);
    
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = '✓ Message Sent Successfully!';
    submitBtn.style.background = '#48bb78';
    submitBtn.disabled = true;
    
    form.reset();
    
    setTimeout(() => {
        submitBtn.textContent = originalText;
        submitBtn.style.background = '';
        submitBtn.disabled = false;
    }, 3000);
}

function handleNewsletterSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const email = form.querySelector('input[type="email"]').value;
    
    console.log('Newsletter signup:', { email });
    
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = '✓ Subscribed!';
    
    form.reset();
    
    setTimeout(() => {
        submitBtn.textContent = originalText;
    }, 2000);
}

// Utility Functions
function scrollTo(selector) {
    const element = document.querySelector(selector);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

function observeElements() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.feature-card, .pricing-card, .stat-card, .footer-section').forEach(el => {
        el.style.opacity = '0';
        observer.observe(el);
    });
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('authModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
};

// Navbar shadow on scroll
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 0) {
        navbar.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.2)';
    } else {
        navbar.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.1)';
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === '?') {
        console.log(`
        🎹 Keyboard Shortcuts:
        ─────────────────────
        # - Jump to Home
        f - Jump to Features
        d - Jump to Demo
        p - Jump to Pricing
        c - Jump to Contact
        `);
    }
});