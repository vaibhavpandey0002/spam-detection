document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('spam-form');
    const messageInput = document.getElementById('message');
    
    const themeToggleBtn = document.getElementById('theme-toggle');
    const darkIcon = document.getElementById('theme-toggle-dark-icon');
    const lightIcon = document.getElementById('theme-toggle-light-icon');

    // Theme Toggle Logic
    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
        lightIcon.classList.remove('hidden');
    } else {
        document.documentElement.classList.remove('dark');
        darkIcon.classList.remove('hidden');
    }

    themeToggleBtn.addEventListener('click', () => {
        darkIcon.classList.toggle('hidden');
        lightIcon.classList.toggle('hidden');
        if (document.documentElement.classList.contains('dark')) {
            document.documentElement.classList.remove('dark');
            localStorage.theme = 'light';
        } else {
            document.documentElement.classList.add('dark');
            localStorage.theme = 'dark';
        }
    });

    // Example Buttons
    document.querySelectorAll('.example-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            messageInput.value = btn.getAttribute('data-text');
        });
    });

    // Form Submission
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = messageInput.value.trim();
        if (text) {
            // Save to localStorage and redirect
            localStorage.setItem('spamMessage', text);
            window.location.href = 'result.html';
        }
    });
});
