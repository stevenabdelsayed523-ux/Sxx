// Smooth scrolling helper
function scrollTo(selector) {
    const element = document.querySelector(selector);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

// Navigation scroll animations
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Demo - Analyze code functionality
function analyzeCode() {
    const codeInput = document.getElementById('codeInput').value;
    const outputBox = document.getElementById('demoOutput');
    
    if (!codeInput.trim()) {
        outputBox.innerHTML = '<p style="color: #e53e3e;">Please enter some code first.</p>';
        return;
    }

    // Simulate AI analysis
    outputBox.innerHTML = `
        <div style="animation: fadeInUp 0.5s ease-out;">
            <h4 style="color: #4299e1; margin-bottom: 1rem;">✓ AI Analysis Complete</h4>
            <div style="text-align: left; font-size: 0.85rem;">
                <p style="margin-bottom: 1rem;"><strong>Suggestions:</strong></p>
                <ul style="margin-left: 1.5rem; color: #68d391;">
                    <li>✓ Function complexity is low (good!)</li>
                    <li>✓ Variable naming is clear</li>
                    <li>✓ Consider adding JSDoc comments</li>
                    <li>✓ Performance: O(1) time complexity</li>
                    <li>✓ Consider adding input validation</li>
                </ul>
                <p style="margin-top: 1rem; color: #a0aec0;"><em>Confidence: 94%</em></p>
            </div>
        </div>
    `;
}

// Form submission handling
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
    
    // Show success message
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = '✓ Message Sent Successfully!';
    submitBtn.style.background = '#48bb78';
    submitBtn.disabled = true;
    
    // Reset form
    form.reset();
    
    // Restore button after 3 seconds
    setTimeout(() => {
        submitBtn.textContent = originalText;
        submitBtn.style.background = '';
        submitBtn.disabled = false;
    }, 3000);
}

// Newsletter form submission
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

// Add scroll animation for elements
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

    // Observe all cards
    document.querySelectorAll('.feature-card, .pricing-card, .stat-card, .footer-section').forEach(el => {
        el.style.opacity = '0';
        observer.observe(el);
    });
}

// Mobile menu toggle (placeholder for future expansion)
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');

if (hamburger) {
    hamburger.addEventListener('click', () => {
        navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
    });
}

// Navbar shadow on scroll
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 0) {
        navbar.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.2)';
    } else {
        navbar.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.1)';
    }
});

// Initialize animations when page loads
document.addEventListener('DOMContentLoaded', () => {
    observeElements();
    console.log('CodeMate AI Website loaded successfully!');
});

// Keyboard navigation for accessibility
document.addEventListener('keydown', (e) => {
    // Press '?' to show keyboard shortcuts
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
    
    // Quick navigation shortcuts
    if (e.ctrlKey || e.metaKey) {
        switch(e.key) {
            case '#':
                scrollTo('#home');
                break;
            case 'f':
                scrollTo('#features');
                break;
            case 'd':
                scrollTo('#demo');
                break;
            case 'p':
                scrollTo('#pricing');
                break;
            case 'c':
                scrollTo('#contact');
                break;
        }
    }
});

// Performance monitoring
if (window.performance) {
    window.addEventListener('load', () => {
        const perfData = window.performance.timing;
        const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
        console.log(`Page loaded in ${pageLoadTime}ms`);
    });
}
