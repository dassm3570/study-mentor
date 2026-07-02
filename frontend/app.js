document.addEventListener('DOMContentLoaded', () => {
    const sendBtn = document.getElementById('send-btn');
    const stimulusInput = document.getElementById('stimulus-input');
    const thoughtDisplay = document.getElementById('thought-display');

    // Innovation Engine Elements
    const innovationCard = document.getElementById('engine-innovation');
    const innovationModal = document.getElementById('innovation-modal');
    const closeInnovationBtn = document.getElementById('close-innovation-btn');
    const generateInnovationBtn = document.getElementById('generate-innovation-btn');
    const innovationGoalInput = document.getElementById('innovation-goal');
    const innovationIndustryInput = document.getElementById('innovation-industry');
    const innovationFocusInput = document.getElementById('innovation-focus');
    
    const innovationLoading = document.getElementById('innovation-loading');
    const innovationResults = document.getElementById('innovation-results');
    
    const resultIndustryBadge = document.getElementById('result-industry-badge');
    const resultFocusBadge = document.getElementById('result-focus-badge');
    
    const productsTab = document.getElementById('products-tab');
    const featuresTab = document.getElementById('features-tab');
    const researchTab = document.getElementById('research-tab');

    async function processThought() {
        const stimulus = stimulusInput.value.trim();
        if (!stimulus) return;

        // Display user stimulus
        const userLine = document.createElement('div');
        userLine.className = 'monologue user-input-show';
        userLine.textContent = `> STIMULUS: ${stimulus}`;
        thoughtDisplay.appendChild(userLine);
        stimulusInput.value = '';
        thoughtDisplay.scrollTop = thoughtDisplay.scrollHeight;

        // Send request to FastAPI endpoint
        try {
            const response = await fetch('/api/v1/think', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ type: 'user_stimulus', value: stimulus })
            });

            if (!response.ok) throw new Error('Network response error');

            const data = await response.json();
            
            const responseLine = document.createElement('div');
            responseLine.className = 'monologue brain-response-show';
            responseLine.textContent = `< AETHER: ${data.thought_process}`;
            thoughtDisplay.appendChild(responseLine);
        } catch (error) {
            const errLine = document.createElement('div');
            errLine.className = 'monologue';
            errLine.style.color = '#ef4444';
            errLine.textContent = `! ERROR: Could not connect to Core Brain.`;
            thoughtDisplay.appendChild(errLine);
        }

        thoughtDisplay.scrollTop = thoughtDisplay.scrollHeight;
    }

    sendBtn.addEventListener('click', processThought);
    stimulusInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            processThought();
        }
    });

    // --- Innovation Engine Modal Logic ---

    // Open Modal
    if (innovationCard) {
        innovationCard.addEventListener('click', () => {
            innovationModal.classList.remove('hidden');
            innovationGoalInput.focus();
        });
    }

    // Close Modal
    if (closeInnovationBtn) {
        closeInnovationBtn.addEventListener('click', () => {
            innovationModal.classList.add('hidden');
        });
    }

    // Close Modal on Outside Click
    window.addEventListener('click', (e) => {
        if (e.target === innovationModal) {
            innovationModal.classList.add('hidden');
        }
    });

    // Handle Generation
    if (generateInnovationBtn) {
        generateInnovationBtn.addEventListener('click', async () => {
            const goal = innovationGoalInput.value.trim();
            const industry = innovationIndustryInput.value.trim() || null;
            const focus_area = innovationFocusInput.value.trim() || null;

            if (!goal) {
                alert('Please enter a core goal or challenge.');
                innovationGoalInput.focus();
                return;
            }

            // Show loading, hide results
            innovationLoading.classList.remove('hidden');
            innovationResults.classList.add('hidden');
            generateInnovationBtn.disabled = true;
            generateInnovationBtn.textContent = 'Generating...';

            try {
                const response = await fetch('/api/v1/innovation/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ goal, industry, focus_area })
                });

                if (!response.ok) throw new Error('Failed to generate innovation package.');

                const data = await response.json();
                renderInnovationResults(data);
            } catch (error) {
                console.error(error);
                alert('Error generating ideas. Please try again.');
            } finally {
                innovationLoading.classList.add('hidden');
                generateInnovationBtn.disabled = false;
                generateInnovationBtn.textContent = 'Generate Innovation Package';
            }
        });
    }

    // Render Results
    function renderInnovationResults(data) {
        // Update badges
        resultIndustryBadge.textContent = `Industry: ${data.industry}`;
        resultFocusBadge.textContent = `Focus: ${data.focus_area}`;

        // 1. Render Products
        productsTab.innerHTML = '';
        if (data.product_ideas && data.product_ideas.length > 0) {
            data.product_ideas.forEach(idea => {
                const card = document.createElement('div');
                card.className = 'idea-card';
                card.innerHTML = `
                    <div class="idea-card-header">
                        <h3 class="idea-title">${idea.title}</h3>
                    </div>
                    <p class="idea-desc">${idea.description}</p>
                    <div class="idea-details">
                        <div class="detail-row">
                            <span class="detail-label">Audience</span>
                            <span class="detail-value">${idea.audience}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Value Prop</span>
                            <span class="detail-value">${idea.value_prop}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Tech Stack</span>
                            <span class="detail-value">${idea.tech_stack}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Monetization</span>
                            <span class="detail-value">${idea.monetization}</span>
                        </div>
                    </div>
                `;
                productsTab.appendChild(card);
            });
        } else {
            productsTab.innerHTML = '<p class="subtitle">No product ideas generated.</p>';
        }

        // 2. Render Features
        featuresTab.innerHTML = '';
        if (data.feature_ideas && data.feature_ideas.length > 0) {
            data.feature_ideas.forEach(feature => {
                const card = document.createElement('div');
                card.className = 'idea-card';
                const impactClass = feature.impact.toLowerCase();
                const complexityClass = feature.complexity.toLowerCase();
                card.innerHTML = `
                    <div class="idea-card-header">
                        <h3 class="idea-title">${feature.title}</h3>
                        <div style="display: flex; gap: 0.5rem;">
                            <span class="badge ${impactClass}">Impact: ${feature.impact}</span>
                            <span class="badge ${complexityClass}">Complexity: ${feature.complexity}</span>
                        </div>
                    </div>
                    <p class="idea-desc">${feature.description}</p>
                    <div class="idea-details">
                        <div class="detail-row">
                            <span class="detail-label">User Flow</span>
                            <span class="detail-value">${feature.user_flow}</span>
                        </div>
                    </div>
                `;
                featuresTab.appendChild(card);
            });
        } else {
            featuresTab.innerHTML = '<p class="subtitle">No feature ideas generated.</p>';
        }

        // 3. Render Research Suggestions
        researchTab.innerHTML = '';
        if (data.research_suggestions && data.research_suggestions.length > 0) {
            data.research_suggestions.forEach(res => {
                const card = document.createElement('div');
                card.className = 'idea-card';
                card.innerHTML = `
                    <div class="idea-card-header">
                        <h3 class="idea-title">${res.topic}</h3>
                    </div>
                    <div class="idea-details" style="border-top: none; padding-top: 0;">
                        <div class="detail-row">
                            <span class="detail-label">Hypothesis</span>
                            <span class="detail-value">${res.hypothesis}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Methodology</span>
                            <span class="detail-value">${res.methodology}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Expected Outcome</span>
                            <span class="detail-value">${res.expected_outcome}</span>
                        </div>
                    </div>
                `;
                researchTab.appendChild(card);
            });
        } else {
            researchTab.innerHTML = '<p class="subtitle">No research suggestions generated.</p>';
        }

        // Show results
        innovationResults.classList.remove('hidden');
    }

    // Tab Switching Logic
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons and contents
            tabButtons.forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            // Add active class to current button and target content
            btn.classList.add('active');
            const targetTab = btn.getAttribute('data-tab');
            document.getElementById(targetTab).classList.add('active');
        });
    });

    // --- Genesis Engine Modal & Blueprint Logic ---
    const genesisCard = document.getElementById('engine-genesis');
    const genesisModal = document.getElementById('genesis-modal');
    const closeGenesisBtn = document.getElementById('close-genesis-btn');
    const generateGenesisBtn = document.getElementById('generate-genesis-btn');
    const genesisGoalInput = document.getElementById('genesis-goal');
    const genesisStackInput = document.getElementById('genesis-stack');
    const genesisDbInput = document.getElementById('genesis-db');
    
    const genesisLoading = document.getElementById('genesis-loading');
    const genesisResults = document.getElementById('genesis-results');
    const blueprintNavList = document.getElementById('blueprint-nav-list');
    const blueprintDocContent = document.getElementById('blueprint-doc-content');
    const activeDocTitle = document.getElementById('active-doc-title');
    const copyBlueprintBtn = document.getElementById('copy-blueprint-btn');

    let currentBlueprintData = {};
    let activeBlueprintKey = '';

    // Open Genesis Modal
    if (genesisCard) {
        genesisCard.addEventListener('click', () => {
            genesisModal.classList.remove('hidden');
            genesisGoalInput.focus();
        });
    }

    // Close Genesis Modal
    if (closeGenesisBtn) {
        closeGenesisBtn.addEventListener('click', () => {
            genesisModal.classList.add('hidden');
        });
    }

    // Close on Outside Click
    window.addEventListener('click', (e) => {
        if (e.target === genesisModal) {
            genesisModal.classList.add('hidden');
        }
    });

    // Coordinate & Generate Blueprint
    if (generateGenesisBtn) {
        generateGenesisBtn.addEventListener('click', async () => {
            const goal = genesisGoalInput.value.trim();
            const tech_stack = genesisStackInput.value.trim() || null;
            const db_type = genesisDbInput.value.trim() || null;

            if (!goal) {
                alert('Please enter a project goal or core concept.');
                genesisGoalInput.focus();
                return;
            }

            // Get selected specialists
            const selectedCheckboxes = document.querySelectorAll('.specialist-grid input[type="checkbox"]:checked');
            const modules = Array.from(selectedCheckboxes).map(cb => cb.value);

            if (modules.length === 0) {
                alert('Please select at least one specialist module.');
                return;
            }

            // Show loading, hide results
            genesisLoading.classList.remove('hidden');
            genesisResults.classList.add('hidden');
            generateGenesisBtn.disabled = true;
            generateGenesisBtn.textContent = 'Coordinating Team...';

            try {
                const response = await fetch('/api/v1/genesis/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ goal, modules, tech_stack, db_type })
                });

                if (!response.ok) throw new Error('Failed to generate project blueprint.');

                const data = await response.json();
                currentBlueprintData = data.blueprint;
                renderBlueprintWorkspace();
            } catch (error) {
                console.error(error);
                alert('Error generating blueprint. Please try again.');
            } finally {
                genesisLoading.classList.add('hidden');
                generateGenesisBtn.disabled = false;
                generateGenesisBtn.textContent = 'Coordinate Team & Build Blueprint';
            }
        });
    }

    // Render Blueprint Workspace (Sidebar and initial document)
    function renderBlueprintWorkspace() {
        blueprintNavList.innerHTML = '';
        const keys = Object.keys(currentBlueprintData);

        if (keys.length === 0) {
            blueprintDocContent.innerHTML = '<p class="subtitle">No documents generated.</p>';
            genesisResults.classList.remove('hidden');
            return;
        }

        // Generate navigation buttons
        keys.forEach((key, index) => {
            const btn = document.createElement('button');
            btn.className = `blueprint-nav-btn ${index === 0 ? 'active' : ''}`;
            // Format name (e.g. ui_ux -> UI/UX Design, requirements -> Requirements)
            const displayName = key.split('_')
                                   .map(word => word.toUpperCase() === 'UI' || word.toUpperCase() === 'UX' || word.toUpperCase() === 'AI' ? word.toUpperCase() : word.charAt(0).toUpperCase() + word.slice(1))
                                   .join(' ');
            btn.textContent = displayName;
            btn.addEventListener('click', () => {
                document.querySelectorAll('.blueprint-nav-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                displayDocument(key);
            });
            blueprintNavList.appendChild(btn);
        });

        // Display first document
        displayDocument(keys[0]);
        genesisResults.classList.remove('hidden');
    }

    // Display a specific document
    function displayDocument(key) {
        activeBlueprintKey = key;
        const displayName = key.split('_')
                               .map(word => word.toUpperCase() === 'UI' || word.toUpperCase() === 'UX' || word.toUpperCase() === 'AI' ? word.toUpperCase() : word.charAt(0).toUpperCase() + word.slice(1))
                               .join(' ');
        activeDocTitle.textContent = displayName;
        const markdown = currentBlueprintData[key];
        blueprintDocContent.innerHTML = parseMarkdown(markdown);
    }

    // Copy Current Document Markdown to Clipboard
    if (copyBlueprintBtn) {
        copyBlueprintBtn.addEventListener('click', () => {
            const markdown = currentBlueprintData[activeBlueprintKey];
            if (markdown) {
                navigator.clipboard.writeText(markdown).then(() => {
                    const originalText = copyBlueprintBtn.textContent;
                    copyBlueprintBtn.textContent = 'Copied!';
                    setTimeout(() => {
                        copyBlueprintBtn.textContent = originalText;
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy text: ', err);
                });
            }
        });
    }

    // Simple Markdown to HTML Parser
    function parseMarkdown(md) {
        if (!md) return '';
        let html = md;
        
        // Escape HTML tags to prevent XSS and formatting breaks
        html = html.replace(/&/g, '&amp;')
                   .replace(/</g, '&lt;')
                   .replace(/>/g, '&gt;');

        // Fenced code blocks with code highlight tags
        html = html.replace(/```(.*?)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
        
        // Inline code
        html = html.replace(/`([^`\n]+)`/g, '<code>$1</code>');
        
        // Headings
        html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
        html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
        
        // Bold
        html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // Lists
        html = html.replace(/^\* (.*$)/gim, '<ul><li>$1</li></ul>');
        html = html.replace(/<\/ul>\s*<ul>/g, ''); 
        
        html = html.replace(/^- (.*$)/gim, '<ul><li>$1</li></ul>');
        html = html.replace(/<\/ul>\s*<ul>/g, ''); 
        
        html = html.replace(/^\d+\.\s(.*$)/gim, '<ol><li>$1</li></ol>');
        html = html.replace(/<\/ol>\s*<ol>/g, '');
        
        // Newlines
        html = html.replace(/\n/g, '<br>');
        
        // Restore code blocks formatting (prevent <br> in code)
        html = html.replace(/<pre><code>([\s\S]*?)<\/code><\/pre>/g, (match, p1) => {
            return '<pre><code>' + p1.replace(/<br>/g, '\n') + '</code></pre>';
        });

        // Clean up double br inside structural tags
        html = html.replace(/<(ul|ol|li|h1|h2|h3|pre)>(.*?)<br>/g, '<$1>$2');
        html = html.replace(/<br><(ul|ol|li|h1|h2|h3|pre)>/g, '<$1>');
        
        return html;
    }
});


