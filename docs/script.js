/* ═══════════════════════════════════════════════════════════════
   AY Automate — Documentation Scripts
   ═══════════════════════════════════════════════════════════════ */

// ── Copy to Clipboard ──────────────────────────────────────────
function copyCode(button) {
    const codeBlock = button.closest('.code-block');
    const code = codeBlock.querySelector('code').textContent;

    navigator.clipboard.writeText(code).then(() => {
        const original = button.textContent;
        button.textContent = '✓ Copied!';
        button.style.borderColor = '#6c5ce7';
        button.style.color = '#6c5ce7';

        setTimeout(() => {
            button.textContent = original;
            button.style.borderColor = '';
            button.style.color = '';
        }, 2000);
    }).catch(() => {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = code;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        button.textContent = '✓ Copied!';
        setTimeout(() => { button.textContent = '📋 Copy'; }, 2000);
    });
}

// ── Mobile Navigation Toggle ───────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.querySelector('.nav-toggle');
    const links = document.querySelector('.nav-links');

    if (toggle && links) {
        toggle.addEventListener('click', () => {
            links.classList.toggle('active');
        });

        // Close on link click
        links.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                links.classList.remove('active');
            });
        });
    }
});

// ── Smooth Scroll for Anchor Links ─────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const offset = 80;
            const targetPosition = target.offsetTop - offset;
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// ── Navbar Scroll Effect ───────────────────────────────────────
let lastScroll = 0;
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    const currentScroll = window.pageYOffset;

    if (currentScroll > 100) {
        navbar.style.padding = '8px 0';
        navbar.style.boxShadow = '0 4px 20px rgba(0,0,0,0.3)';
    } else {
        navbar.style.padding = '16px 0';
        navbar.style.boxShadow = 'none';
    }

    lastScroll = currentScroll;
});

// ── Pipeline Stage Hover Animation ─────────────────────────────
document.querySelectorAll('.pipeline-stage').forEach(stage => {
    stage.addEventListener('mouseenter', () => {
        const checkpoint = stage.querySelector('.stage-checkpoint');
        if (checkpoint) {
            checkpoint.style.transform = 'translateX(-50%) scale(1.1)';
            checkpoint.style.boxShadow = '0 4px 16px rgba(108, 92, 231, 0.4)';
        }
    });

    stage.addEventListener('mouseleave', () => {
        const checkpoint = stage.querySelector('.stage-checkpoint');
        if (checkpoint) {
            checkpoint.style.transform = 'translateX(-50%) scale(1)';
            checkpoint.style.boxShadow = 'none';
        }
    });
});

// ── Intersection Observer for Animations ───────────────────────
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Apply entrance animation to cards
document.addEventListener('DOMContentLoaded', () => {
    const elements = document.querySelectorAll(
        '.feature-card, .api-card, .project-card, .step, .pipeline-stage'
    );

    elements.forEach((el, i) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = `opacity 0.6s ease ${i * 0.1}s, transform 0.6s ease ${i * 0.1}s`;
        observer.observe(el);
    });
});
