document.addEventListener('DOMContentLoaded', async () => {
    const loadingState = document.getElementById('loading-state');
    const resultBox = document.getElementById('result-box');
    const resultIcon = document.getElementById('result-icon');
    const resultText = document.getElementById('result-text');
    const resultSubtext = document.getElementById('result-subtext');
    
    const confidenceCircle = document.getElementById('confidence-circle');
    const confidenceText = document.getElementById('confidence-text');
    const confidenceContainer = document.getElementById('confidence-container');
    
    const keywordsContainer = document.getElementById('keywords-container');
    const keywordsList = document.getElementById('keywords-list');
    
    const reasonsContainer = document.getElementById('reasons-container');
    const reasonsList = document.getElementById('reasons-list');
    
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

    // Get message from localStorage
    const message = localStorage.getItem('spamMessage');

    if (!message) {
        // No message found, redirect back
        window.location.href = 'index.html';
        return;
    }

    // Optional: Add a slight delay so the loading animation is visible and it feels like it's "thinking"
    setTimeout(() => {
        fetchPrediction(message);
    }, 600);

    async function fetchPrediction(text) {
        try {
            // Call FastAPI Backend
            // API URL - use relative path for single deployment
            const API_URL = (typeof window.ENV !== 'undefined' && window.ENV.API_URL) || '';
            const response = await fetch(`${API_URL}/api/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: text })
            });

            if (!response.ok) {
                throw new Error('API returned an error');
            }

            const data = await response.json();
            
            // UI Result State
            showResult(data);

        } catch (error) {
            console.error(error);
            showResult({ prediction: 'Error' });
        }
    }

    function showResult(data) {
        // Hide loading, show result box
        loadingState.classList.add('hidden');
        resultBox.classList.remove('hidden');

        const prediction = data.prediction;

        if (prediction === 'Spam') {
            resultIcon.className = 'w-24 h-24 rounded-full flex-shrink-0 flex items-center justify-center bg-red-100 dark:bg-red-900/30 text-danger';
            resultIcon.innerHTML = `<svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>`;
            resultText.textContent = 'Spam Detected!';
            resultText.className = 'text-4xl font-extrabold mb-2 text-danger';
            resultSubtext.textContent = 'This message appears to be unsolicited or malicious.';
            confidenceContainer.classList.remove('hidden');
        } else if (prediction === 'Not Spam') {
            resultIcon.className = 'w-24 h-24 rounded-full flex-shrink-0 flex items-center justify-center bg-green-100 dark:bg-green-900/30 text-success';
            resultIcon.innerHTML = `<svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;
            resultText.textContent = 'Looks Safe!';
            resultText.className = 'text-4xl font-extrabold mb-2 text-success';
            resultSubtext.textContent = 'This message appears to be a normal text (Ham).';
            confidenceContainer.classList.remove('hidden');
        } else {
            // Error State
            resultIcon.className = 'w-24 h-24 rounded-full flex-shrink-0 flex items-center justify-center bg-gray-100 dark:bg-gray-800 text-gray-500';
            resultIcon.innerHTML = `<svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;
            resultText.textContent = 'Connection Error';
            resultText.className = 'text-4xl font-extrabold mb-2 text-gray-700 dark:text-gray-300';
            resultSubtext.textContent = 'Could not reach the prediction server.';
            
            confidenceContainer.classList.add('hidden');
            keywordsContainer.classList.add('hidden');
            reasonsContainer.classList.add('hidden');
            return;
        }

        // Update Confidence
        if (data.confidence !== undefined) {
            confidenceText.textContent = `${data.confidence}%`;
            // Add a slight delay for the animation to look nice
            setTimeout(() => {
                confidenceCircle.style.strokeDasharray = `${data.confidence}, 100`;
            }, 100);
            
            if (prediction === 'Spam') {
                confidenceCircle.classList.remove('text-success');
                confidenceCircle.classList.add('text-danger');
            } else {
                confidenceCircle.classList.remove('text-danger');
                confidenceCircle.classList.add('text-success');
            }
        }

        // Update Keywords
        if (data.keywords && data.keywords.length > 0) {
            keywordsContainer.classList.remove('hidden');
            keywordsList.innerHTML = data.keywords.map(kw => 
                `<span class="px-3 py-1.5 rounded-full text-sm font-semibold bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300 border border-red-200 dark:border-red-800">${kw}</span>`
            ).join('');
        } else {
            keywordsContainer.classList.add('hidden');
        }

        // Update Reasons
        if (data.reasons && data.reasons.length > 0) {
            reasonsContainer.classList.remove('hidden');
            reasonsList.innerHTML = data.reasons.map(reason => 
                `<li class="flex items-start gap-3 text-base text-gray-700 dark:text-gray-300">
                    <svg class="w-5 h-5 mt-0.5 text-primary flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4"></path></svg>
                    <span>${reason}</span>
                </li>`
            ).join('');
        } else {
            reasonsContainer.classList.add('hidden');
        }

        // Display Safety Suggestion
        const suggestionContainer = document.getElementById('suggestion-container');
        const suggestionTitle = document.getElementById('suggestion-title');
        const suggestionText = document.getElementById('suggestion-text');
        const suggestionIcon = document.getElementById('suggestion-icon');

        suggestionContainer.classList.remove('hidden');
        if (prediction === 'Spam') {
            suggestionContainer.className = "mt-8 p-5 rounded-2xl bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800";
            suggestionTitle.className = "font-bold mb-1 text-yellow-800 dark:text-yellow-400";
            suggestionText.className = "text-sm text-yellow-700 dark:text-yellow-300";
            suggestionIcon.className = "w-6 h-6 flex-shrink-0 mt-0.5 text-yellow-600 dark:text-yellow-500";
            suggestionIcon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>`;
            
            suggestionTitle.textContent = "Safety Alert & Suggestion";
            suggestionText.textContent = "You should completely avoid interacting with this type of message and stay alert for similar scams. Do not click on any suspicious links, reply to the sender, or provide any personal information.";
        } else {
            suggestionContainer.className = "mt-8 p-5 rounded-2xl bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800";
            suggestionTitle.className = "font-bold mb-1 text-blue-800 dark:text-blue-400";
            suggestionText.className = "text-sm text-blue-700 dark:text-blue-300";
            suggestionIcon.className = "w-6 h-6 flex-shrink-0 mt-0.5 text-blue-600 dark:text-blue-500";
            suggestionIcon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>`;
            
            suggestionTitle.textContent = "General Advice";
            suggestionText.textContent = "While this message looks safe, always ensure you verify the sender's identity if they are asking for sensitive information.";
        }
    }
});
