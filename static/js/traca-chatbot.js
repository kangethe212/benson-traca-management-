/**
 * Traca Management Services - Bilingual Chatbot
 * Professional real estate chatbot with English/Swahili support
 */

class TracaChatbot {
    constructor() {
        this.isOpen = false;
        this.currentLanguage = 'en'; // Default to English
        this.chatHistory = [];
        this.isTyping = false;
        
        // Initialize the chatbot
        this.init();
    }

    init() {
        this.createChatbotHTML();
        this.attachEventListeners();
        this.loadChatHistory();
        
        // Debug: Check if elements are visible
        setTimeout(() => {
            this.debugVisibility();
        }, 1000);
        
        // Auto-greet after a short delay
        setTimeout(() => {
            this.showWelcomeMessage();
        }, 2000);
    }

    createChatbotHTML() {
        // Create chatbot container
        const chatbotHTML = `
            <div id="traca-chatbot" class="traca-chatbot-container">
                <!-- Chat Toggle Button -->
                <div id="chatbot-toggle" class="chatbot-toggle">
                    <div class="chatbot-icon">
                        <i class="fas fa-comments"></i>
                        <span class="notification-badge" id="notification-badge" style="display: none;">1</span>
                    </div>
                </div>

                <!-- Chat Window -->
                <div id="chatbot-window" class="chatbot-window" style="display: none;">
                    <!-- Chat Header -->
                    <div class="chatbot-header">
                        <div class="chatbot-header-info">
                            <div class="chatbot-avatar">
                                <i class="fas fa-building"></i>
                            </div>
                            <div class="chatbot-title">
                                <h6>Traca Management</h6>
                                <small class="status-text">Online</small>
                            </div>
                        </div>
                        <div class="chatbot-controls">
                            <button id="minimize-chat" class="chatbot-btn">
                                <i class="fas fa-minus"></i>
                            </button>
                            <button id="close-chat" class="chatbot-btn">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>

                    <!-- Chat Messages -->
                    <div id="chatbot-messages" class="chatbot-messages">
                        <!-- Messages will be inserted here -->
                    </div>

                    <!-- Chat Input -->
                    <div class="chatbot-input-container">
                    <div class="chatbot-input-wrapper">
                        <input type="text" id="chatbot-input" placeholder="Type your message..." autocomplete="off">
                        <button id="chatbot-send" class="chatbot-send-btn">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                    <div class="quick-actions" id="quick-actions">
                        <button class="quick-action-btn" onclick="quickAction('contact')">
                            <i class="fas fa-phone"></i> Contact
                        </button>
                        <button class="quick-action-btn" onclick="quickAction('properties')">
                            <i class="fas fa-home"></i> Properties
                        </button>
                        <button class="quick-action-btn" onclick="quickAction('services')">
                            <i class="fas fa-cogs"></i> Services
                        </button>
                    </div>
                        <div class="chatbot-suggestions" id="chatbot-suggestions">
                            <!-- Quick suggestions will appear here -->
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Insert chatbot into page
        document.body.insertAdjacentHTML('beforeend', chatbotHTML);
    }

    attachEventListeners() {
        // Toggle chat
        document.getElementById('chatbot-toggle').addEventListener('click', () => {
            this.toggleChat();
        });

        // Close chat
        document.getElementById('close-chat').addEventListener('click', () => {
            this.closeChat();
        });

        // Minimize chat
        document.getElementById('minimize-chat').addEventListener('click', () => {
            this.closeChat();
        });

        // Send message
        document.getElementById('chatbot-send').addEventListener('click', () => {
            this.sendMessage();
        });

        // Enter key to send
        document.getElementById('chatbot-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // Language detection on input
        document.getElementById('chatbot-input').addEventListener('input', (e) => {
            this.detectLanguage(e.target.value);
        });
    }

    detectLanguage(text) {
        if (text.length < 3) return;
        
        // Simple language detection based on common Swahili words
        const swahiliWords = ['karibu', 'asante', 'hujambo', 'sijambo', 'habari', 'mzuri', 'sana', 'naweza', 'kukusaidia', 'leo', 'nyumba', 'kodi', 'huduma', 'ofisi', 'wapi', 'ninaweza', 'kuwasiliana', 'nanyi', 'mnashughulikia', 'majengo', 'makazi', 'biashara', 'ninawezaje', 'kuweka', 'chini', 'usimamizi', 'wenu', 'nani', 'hushughulikia', 'matengenezo', 'nalipa', 'kivipi', 'mna', 'zilizopo', 'wazi', 'naweza', 'kupanga', 'muda', 'kutazama', 'mnatoza', 'kiwango', 'gani', 'samahani', 'sijaelewa', 'vizuri', 'tafadhali', 'fafanua', 'swali', 'lako'];
        
        const words = text.toLowerCase().split(' ');
        const swahiliCount = words.filter(word => swahiliWords.includes(word)).length;
        
        if (swahiliCount > 0) {
            this.currentLanguage = 'sw';
        } else {
            this.currentLanguage = 'en';
        }
    }

    showWelcomeMessage() {
        const welcomeMessages = {
            en: "👋 Hello! Welcome to Traca Management Services! I'm your personal real estate assistant. I'm here to help you with everything related to properties, rentals, sales, and management services. What can I help you with today?",
            sw: "👋 Hujambo! Karibu Traca Management Services! Mimi ni msaidizi wako wa mali. Niko hapa kukusaidia na kila kitu kuhusu mali, kukodi, uuzaji, na huduma za usimamizi. Ninaweza kukusaidia na nini leo?"
        };

        this.addBotMessage(welcomeMessages[this.currentLanguage]);
        
        // Show initial conversation starters
        setTimeout(() => {
            this.showConversationStarters();
            this.forceShowElements(); // Ensure all elements are visible
        }, 1000);
    }

    showQuickSuggestions() {
        const suggestions = {
            en: [
                "What services do you offer?",
                "Property management services",
                "Property sales and rentals",
                "Marketing services",
                "Where are your offices?",
                "How can I contact you?",
                "Do you have available properties?",
                "What are your charges?",
                "How can I list my property?",
                "About Traca Management"
            ],
            sw: [
                "Mna toa huduma gani?",
                "Huduma za usimamizi wa mali",
                "Uuzaji na kukodi kwa mali",
                "Huduma za utangazaji",
                "Ofisi zenu ziko wapi?",
                "Ninawezaje kuwasiliana nanyi?",
                "Mna nyumba zilizopo wazi?",
                "Mnatoza kiwango gani?",
                "Ninawezaje kuweka mali yangu?",
                "Kuhusu Traca Management"
            ]
        };

        const suggestionsContainer = document.getElementById('chatbot-suggestions');
        suggestionsContainer.innerHTML = '';

        suggestions[this.currentLanguage].forEach(suggestion => {
            const suggestionBtn = document.createElement('button');
            suggestionBtn.className = 'suggestion-btn';
            suggestionBtn.textContent = suggestion;
            suggestionBtn.addEventListener('click', () => {
                document.getElementById('chatbot-input').value = suggestion;
                this.sendMessage();
            });
            suggestionsContainer.appendChild(suggestionBtn);
        });
    }

    showConversationStarters() {
        const starters = {
            en: [
                "🏠 I'm looking for a property to rent",
                "💰 I want to sell my property",
                "🏢 I need property management services",
                "📋 I want to list my property",
                "🔍 Show me available properties",
                "📞 How can I contact you?",
                "💼 Tell me about your services",
                "📍 Where are your offices?"
            ],
            sw: [
                "🏠 Ninatafuta mali ya kukodi",
                "💰 Ninataka kuuza mali yangu",
                "🏢 Nahitaji huduma za usimamizi wa mali",
                "📋 Ninataka kuweka mali yangu",
                "🔍 Nionyeshe mali zilizopo",
                "📞 Ninawezaje kuwasiliana nanyi?",
                "💼 Nionyeshe huduma zenu",
                "📍 Ofisi zenu ziko wapi?"
            ]
        };

        const suggestionsContainer = document.getElementById('chatbot-suggestions');
        suggestionsContainer.innerHTML = '';

        // Show conversation starters in a more engaging way
        const starterText = this.currentLanguage === 'en' 
            ? "💡 Here are some things I can help you with:"
            : "💡 Haya ni mambo ninaweza kukusaidia:";
        
        const starterDiv = document.createElement('div');
        starterDiv.className = 'conversation-starter-intro';
        starterDiv.textContent = starterText;
        suggestionsContainer.appendChild(starterDiv);

        starters[this.currentLanguage].forEach(starter => {
            const starterBtn = document.createElement('button');
            starterBtn.className = 'conversation-starter-btn';
            starterBtn.innerHTML = starter;
            starterBtn.addEventListener('click', () => {
                document.getElementById('chatbot-input').value = starter;
                this.sendMessage();
            });
            suggestionsContainer.appendChild(starterBtn);
        });
    }

    showContextualSuggestions(response) {
        const contextualSuggestions = {
            en: {
                services: ["Property management services", "Property sales", "Marketing services", "What are your charges?"],
                property_management: ["What are your charges?", "How can I list my property?", "Maintenance services", "Contact information"],
                sales: ["Available properties", "Property valuations", "Marketing services", "How to buy property?"],
                marketing: ["Property photography", "Virtual tours", "Online listings", "What are your charges?"],
                renting: ["Available rentals", "How to rent?", "Rent payment methods", "Property viewings"],
                location: ["Contact information", "Property locations", "Office hours", "Local agents"],
                contact: ["Office hours", "Emergency contact", "WhatsApp support", "Email support"],
                properties: ["Property viewings", "Property details", "Pricing information", "Location details"],
                available_properties: ["Schedule viewing", "Property details", "Pricing", "Contact agent"],
                maintenance: ["Emergency repairs", "Preventive maintenance", "Maintenance costs", "Contact maintenance"],
                rent_payment: ["Payment methods", "Payment schedule", "Late payments", "Payment history"],
                viewing: ["Available times", "Property details", "Agent contact", "Directions"],
                charges: ["Property management fees", "Sales commission", "Additional services", "Payment terms"],
                listing: ["Property assessment", "Management agreement", "Marketing plan", "Contact us"],
                company: ["Our services", "Our locations", "Contact us", "Why choose us?"],
                fallback: ["What services do you offer?", "Available properties", "Contact information", "Property management"]
            },
            sw: {
                services: ["Huduma za usimamizi wa mali", "Uuzaji wa mali", "Huduma za utangazaji", "Mnatoza kiwango gani?"],
                property_management: ["Mnatoza kiwango gani?", "Ninawezaje kuweka mali yangu?", "Huduma za matengenezo", "Taarifa za mawasiliano"],
                sales: ["Mali zilizopo", "Tathmini za mali", "Huduma za utangazaji", "Jinsi ya kununua mali?"],
                marketing: ["Upigaji picha wa mali", "Mazungumzo ya virtual", "Orodha za mtandaoni", "Mnatoza kiwango gani?"],
                renting: ["Mali za kukodi", "Jinsi ya kukodi?", "Njia za malipo ya kodi", "Kutazama mali"],
                location: ["Taarifa za mawasiliano", "Mahali pa mali", "Masaa ya ofisi", "Wakala wa ndani"],
                contact: ["Masaa ya ofisi", "Mawasiliano ya dharura", "Msaada wa WhatsApp", "Msaada wa barua pepe"],
                properties: ["Kutazama mali", "Maelezo ya mali", "Taarifa za bei", "Maelezo ya mahali"],
                available_properties: ["Panga kutazama", "Maelezo ya mali", "Bei", "Wasiliana na wakala"],
                maintenance: ["Matengenezo ya dharura", "Matengenezo ya kukinga", "Gharama za matengenezo", "Wasiliana na matengenezo"],
                rent_payment: ["Njia za malipo", "Ratiba ya malipo", "Malipo ya kuchelewa", "Historia ya malipo"],
                viewing: ["Muda unaopatikana", "Maelezo ya mali", "Mawasiliano ya wakala", "Maelekezo"],
                charges: ["Ada za usimamizi wa mali", "Komisheni ya uuzaji", "Huduma za ziada", "Masharti ya malipo"],
                listing: ["Tathmini ya mali", "Makubaliano ya usimamizi", "Mpango wa utangazaji", "Wasiliana nasi"],
                company: ["Huduma zetu", "Mahali pa ofisi zetu", "Wasiliana nasi", "Kwa nini utuchague?"],
                fallback: ["Mna toa huduma gani?", "Mali zilizopo", "Taarifa za mawasiliano", "Usimamizi wa mali"]
            }
        };

        // Determine which suggestions to show based on response content
        let suggestionsToShow = [];
        
        if (response.includes('comprehensive real estate services') || response.includes('huduma za mali')) {
            suggestionsToShow = contextualSuggestions[this.currentLanguage].services;
        } else if (response.includes('property management services') || response.includes('usimamizi wa mali')) {
            suggestionsToShow = contextualSuggestions[this.currentLanguage].property_management;
        } else if (response.includes('property sales services') || response.includes('uuza')) {
            suggestionsToShow = contextualSuggestions[this.currentLanguage].sales;
        } else if (response.includes('marketing services') || response.includes('utangazaji')) {
            suggestionsToShow = contextualSuggestions[this.currentLanguage].marketing;
        } else if (response.includes('rental services') || response.includes('kukodi')) {
            suggestionsToShow = contextualSuggestions[this.currentLanguage].renting;
        } else if (response.includes('office is located') || response.includes('ofisi')) {
            suggestionsToShow = contextualSuggestions[this.currentLanguage].location;
        } else if (response.includes('contact us through') || response.includes('kuwasiliana')) {
            suggestionsToShow = contextualSuggestions[this.currentLanguage].contact;
        } else if (response.includes('extensive selection') || response.includes('mali nyingi')) {
            suggestionsToShow = contextualSuggestions[this.currentLanguage].properties;
        } else if (response.includes('currently have properties') || response.includes('mali zilizopo')) {
            suggestionsToShow = contextualSuggestions[this.currentLanguage].available_properties;
        } else if (response.includes('maintenance services') || response.includes('matengenezo')) {
            suggestionsToShow = contextualSuggestions[this.currentLanguage].maintenance;
        } else if (response.includes('payment methods') || response.includes('malipo')) {
            suggestionsToShow = contextualSuggestions[this.currentLanguage].rent_payment;
        } else if (response.includes('viewing options') || response.includes('kutazama')) {
            suggestionsToShow = contextualSuggestions[this.currentLanguage].viewing;
        } else if (response.includes('service charges') || response.includes('kiwango')) {
            suggestionsToShow = contextualSuggestions[this.currentLanguage].charges;
        } else if (response.includes('list your property') || response.includes('kuweka mali')) {
            suggestionsToShow = contextualSuggestions[this.currentLanguage].listing;
        } else if (response.includes('Traca Management Services') || response.includes('kampuni')) {
            suggestionsToShow = contextualSuggestions[this.currentLanguage].company;
        } else {
            suggestionsToShow = contextualSuggestions[this.currentLanguage].fallback;
        }

        const suggestionsContainer = document.getElementById('chatbot-suggestions');
        suggestionsContainer.innerHTML = '';

        suggestionsToShow.forEach(suggestion => {
            const suggestionBtn = document.createElement('button');
            suggestionBtn.className = 'suggestion-btn';
            suggestionBtn.textContent = suggestion;
            suggestionBtn.addEventListener('click', () => {
                document.getElementById('chatbot-input').value = suggestion;
                this.sendMessage();
            });
            suggestionsContainer.appendChild(suggestionBtn);
        });
    }

    showConversationPrompts() {
        const conversationPrompts = {
            en: [
                "Ask me anything else!",
                "What else can I help you with?",
                "Do you have more questions?",
                "Need more information?",
                "Anything else you'd like to know?",
                "Feel free to ask more questions!",
                "I'm here to help with anything else!",
                "What would you like to know next?"
            ],
            sw: [
                "Uliza chochote kingine!",
                "Ninaweza kukusaidia na nini kingine?",
                "Una maswali mengine?",
                "Unahitaji taarifa zaidi?",
                "Kitu kingine unataka kujua?",
                "Jisikie huru kuuliza maswali zaidi!",
                "Niko hapa kukusaidia na chochote kingine!",
                "Unataka kujua nini baadaye?"
            ]
        };

        // Add a subtle conversation prompt after suggestions
        setTimeout(() => {
            const suggestionsContainer = document.getElementById('chatbot-suggestions');
            if (suggestionsContainer && suggestionsContainer.children.length > 0) {
                const promptText = conversationPrompts[this.currentLanguage][Math.floor(Math.random() * conversationPrompts[this.currentLanguage].length)];
                
                const promptDiv = document.createElement('div');
                promptDiv.className = 'conversation-prompt';
                promptDiv.innerHTML = `
                    <div class="prompt-text">
                        <i class="fas fa-comment-dots me-2"></i>
                        ${promptText}
                    </div>
                `;
                
                suggestionsContainer.appendChild(promptDiv);
                
                // Add a "Continue Conversation" button
                const continueBtn = document.createElement('button');
                continueBtn.className = 'continue-conversation-btn';
                continueBtn.innerHTML = `
                    <i class="fas fa-comments me-2"></i>
                    ${this.currentLanguage === 'en' ? 'Continue Conversation' : 'Endelea Mazungumzo'}
                `;
                continueBtn.addEventListener('click', () => {
                    document.getElementById('chatbot-input').focus();
                    continueBtn.style.display = 'none';
                });
                
                suggestionsContainer.appendChild(continueBtn);
            }
        }, 1000);
    }

    showHelpfulTips() {
        const tips = {
            en: [
                "💡 Tip: You can ask me about specific property types, locations, or services!",
                "💡 Tip: I can help you find properties in any county in Kenya!",
                "💡 Tip: Ask me about our pricing and how to get started!",
                "💡 Tip: I'm available 24/7 to answer your questions!",
                "💡 Tip: You can ask me to schedule a property viewing!",
                "💡 Tip: I can help you understand our property management process!"
            ],
            sw: [
                "💡 Kidokezo: Unaweza kuniuliza kuhusu aina za mali, maeneo, au huduma!",
                "💡 Kidokezo: Ninaweza kukusaidia kupata mali katika kaunti yoyote ya Kenya!",
                "💡 Kidokezo: Niulize kuhusu bei zetu na jinsi ya kuanza!",
                "💡 Kidokezo: Ninapatikana masaa 24 kujibu maswali yako!",
                "💡 Kidokezo: Unaweza kuniomba kupanga kutazama mali!",
                "💡 Kidokezo: Ninaweza kukusaidia kuelewa mchakato wetu wa usimamizi wa mali!"
            ]
        };

        // Show a random tip occasionally
        if (Math.random() < 0.3) { // 30% chance
            setTimeout(() => {
                const suggestionsContainer = document.getElementById('chatbot-suggestions');
                if (suggestionsContainer && suggestionsContainer.children.length > 0) {
                    const randomTip = tips[this.currentLanguage][Math.floor(Math.random() * tips[this.currentLanguage].length)];
                    
                    const tipDiv = document.createElement('div');
                    tipDiv.className = 'helpful-tip';
                    tipDiv.innerHTML = `
                        <div class="tip-content">
                            ${randomTip}
                        </div>
                    `;
                    
                    suggestionsContainer.appendChild(tipDiv);
                }
            }, 2000);
        }
    }

    debugVisibility() {
        console.log('=== CHATBOT DEBUG ===');
        
        // Check if elements exist
        const elements = [
            'traca-chatbot',
            'chatbot-toggle',
            'chatbot-window',
            'chatbot-messages',
            'chatbot-input',
            'chatbot-send',
            'quick-actions',
            'chatbot-suggestions'
        ];
        
        elements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                const style = window.getComputedStyle(element);
                console.log(`${id}:`, {
                    display: style.display,
                    visibility: style.visibility,
                    opacity: style.opacity,
                    position: style.position,
                    zIndex: style.zIndex
                });
            } else {
                console.log(`${id}: NOT FOUND`);
            }
        });
        
        // Force show all elements
        const quickActions = document.getElementById('quick-actions');
        if (quickActions) {
            quickActions.style.display = 'flex';
            quickActions.style.visibility = 'visible';
            quickActions.style.opacity = '1';
        }
        
        const suggestions = document.getElementById('chatbot-suggestions');
        if (suggestions) {
            suggestions.style.display = 'flex';
            suggestions.style.visibility = 'visible';
            suggestions.style.opacity = '1';
        }
        
        console.log('=== END DEBUG ===');
    }

    forceShowElements() {
        // Force show quick actions
        const quickActions = document.getElementById('quick-actions');
        if (quickActions) {
            quickActions.style.display = 'flex';
            quickActions.style.visibility = 'visible';
            quickActions.style.opacity = '1';
        }
        
        // Force show suggestions
        const suggestions = document.getElementById('chatbot-suggestions');
        if (suggestions) {
            suggestions.style.display = 'flex';
            suggestions.style.visibility = 'visible';
            suggestions.style.opacity = '1';
        }
        
        // Force show all buttons
        const buttons = document.querySelectorAll('.quick-action-btn, .suggestion-btn, .conversation-starter-btn, .continue-conversation-btn');
        buttons.forEach(btn => {
            btn.style.display = btn.classList.contains('quick-action-btn') ? 'flex' : 'block';
            btn.style.visibility = 'visible';
            btn.style.opacity = '1';
        });
        
        // Force show prompts and tips
        const prompts = document.querySelectorAll('.conversation-prompt, .helpful-tip');
        prompts.forEach(prompt => {
            prompt.style.display = 'block';
            prompt.style.visibility = 'visible';
            prompt.style.opacity = '1';
        });
    }

    toggleChat() {
        const window = document.getElementById('chatbot-window');
        const toggle = document.getElementById('chatbot-toggle');
        
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }

    openChat() {
        const window = document.getElementById('chatbot-window');
        const toggle = document.getElementById('chatbot-toggle');
        
        window.style.display = 'block';
        toggle.style.display = 'none';
        this.isOpen = true;
        
        // Focus input
        setTimeout(() => {
            document.getElementById('chatbot-input').focus();
        }, 100);
        
        // Hide notification badge
        document.getElementById('notification-badge').style.display = 'none';
        
        // Force show all elements
        this.forceShowElements();
        
        // Show conversation continuation message if there's history
        if (this.chatHistory.length > 0) {
            setTimeout(() => {
                const continuationMessage = this.currentLanguage === 'en' 
                    ? "Welcome back! I'm here to continue helping you with your real estate needs. What else would you like to know?"
                    : "Karibu tena! Niko hapa kuendelea kukusaidia na mahitaji yako ya mali. Unataka kujua nini kingine?";
                this.addBotMessage(continuationMessage);
                this.showQuickSuggestions();
            }, 500);
        }
    }

    closeChat() {
        const window = document.getElementById('chatbot-window');
        const toggle = document.getElementById('chatbot-toggle');
        
        window.style.display = 'none';
        toggle.style.display = 'flex';
        this.isOpen = false;
    }

    sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message
        this.addUserMessage(message);
        
        // Clear input but keep focus for continued conversation
        input.value = '';
        
        // Hide suggestions temporarily
        document.getElementById('chatbot-suggestions').innerHTML = '';
        
        // Keep input focused for continued conversation
        setTimeout(() => {
            input.focus();
        }, 100);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Process message after a more natural delay
        const delay = Math.random() * 1000 + 1500; // 1.5-2.5 seconds
        setTimeout(() => {
            this.processMessage(message);
        }, delay);
    }

    addUserMessage(message) {
        const messagesContainer = document.getElementById('chatbot-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${this.escapeHtml(message)}</p>
                <span class="message-time">${this.getCurrentTime()}</span>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Store message in chat history
        this.chatHistory.push({
            type: 'user',
            message: message,
            timestamp: new Date().toISOString()
        });
        this.saveChatHistory();
    }

    addBotMessage(message) {
        const messagesContainer = document.getElementById('chatbot-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-building"></i>
            </div>
            <div class="message-content">
                <p>${this.escapeHtml(message)}</p>
                <span class="message-time">${this.getCurrentTime()}</span>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Store message in chat history
        this.chatHistory.push({
            type: 'bot',
            message: message,
            timestamp: new Date().toISOString()
        });
        this.saveChatHistory();
        
        // Play notification sound if chat is closed
        if (!this.isOpen) {
            this.playNotificationSound();
            this.showNotificationBadge();
        }
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatbot-messages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-building"></i>
            </div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
        this.isTyping = true;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
        this.isTyping = false;
    }

    processMessage(message) {
        this.hideTypingIndicator();
        
        const response = this.getResponse(message);
        this.addBotMessage(response);
        
        // Show new suggestions after most responses to encourage continued conversation
        setTimeout(() => {
            this.showContextualSuggestions(response);
            this.showConversationPrompts();
            this.showHelpfulTips();
            this.forceShowElements(); // Ensure all elements are visible
        }, 500);
    }

    getResponse(message) {
        const lowerMessage = message.toLowerCase();
        
        // Comprehensive FAQ Responses
        const faqs = {
            en: {
                // Core Services
                services: "Great question! We offer comprehensive real estate services to help you with all your property needs:\n\n🏠 **PROPERTY SALES**: Buying and selling residential and commercial properties\n🏢 **PROPERTY MANAGEMENT**: Complete management of rental properties\n💰 **RENT COLLECTION**: Automated rent collection and tenant management\n🔧 **MAINTENANCE**: 24/7 maintenance coordination and emergency repairs\n👥 **TENANT PLACEMENT**: Finding and screening qualified tenants\n📋 **PROPERTY INSPECTIONS**: Regular property assessments and reports\n💼 **LANDLORD ADVISORY**: Expert consultation for property owners\n📊 **MARKETING**: Professional property marketing and advertising\n\nWe serve all major counties in Kenya with over 20 years of experience since 2004.\n\n✨ **What interests you most?** Are you looking to buy, sell, rent, or manage a property?",
                
                property_management: "Our property management services include:\n\n✅ Rent collection and tenant screening\n✅ Maintenance coordination and emergency repairs\n✅ Property inspections and condition reports\n✅ Financial reporting and accounting\n✅ Legal compliance and documentation\n✅ Marketing and tenant placement\n✅ 24/7 emergency support\n✅ Regular property assessments\n\nWe handle everything so you can focus on your investment returns. Contact us for a free property assessment.\n\nWould you like to know about our pricing or how to get started?",
                
                sales: "Our property sales services include:\n\n🏘️ RESIDENTIAL SALES: Houses, apartments, townhouses\n🏢 COMMERCIAL SALES: Office buildings, retail spaces, warehouses\n🏭 INDUSTRIAL SALES: Manufacturing facilities, storage units\n🌾 LAND SALES: Residential plots, commercial land, agricultural land\n\nWe provide:\n• Professional property valuations\n• Marketing and advertising\n• Buyer screening and qualification\n• Negotiation and closing support\n• Legal documentation assistance\n\nBrowse our current listings or contact us to list your property.\n\nAre you looking to buy or sell a property?",
                
                marketing: "Our marketing services include:\n\n📱 DIGITAL MARKETING: Online listings, social media promotion\n📸 PROFESSIONAL PHOTOGRAPHY: High-quality property photos\n🎥 VIRTUAL TOURS: 360° virtual property tours\n📋 DETAILED LISTINGS: Comprehensive property descriptions\n📊 MARKET ANALYSIS: Pricing and market positioning\n📢 ADVERTISING: Multi-platform advertising campaigns\n🌐 WEBSITE LISTINGS: Featured listings on our website\n📱 MOBILE OPTIMIZATION: Mobile-friendly property showcases\n\nWe ensure maximum visibility for your property across all channels.",
                
                renting: "Our rental services include:\n\n🏠 RESIDENTIAL RENTALS: Houses, apartments, studios\n🏢 COMMERCIAL RENTALS: Office spaces, retail shops, warehouses\n🏭 INDUSTRIAL RENTALS: Manufacturing facilities, storage units\n🌾 LAND RENTALS: Agricultural land, development plots\n\nWe provide:\n• Tenant screening and background checks\n• Lease agreement preparation\n• Rent collection and management\n• Property maintenance coordination\n• Regular property inspections\n• Legal compliance support\n\nFind your perfect rental property or list your property for rent with us.",
                
                // Location and Contact
                location: "Our main office is located in Nairobi, Kenya. We serve properties across all 47 counties in Kenya including:\n\n📍 NAIROBI: Westlands, Karen, Kilimani, Lavington, Runda\n📍 MOMBASA: Nyali, Mombasa CBD, Diani\n📍 KISUMU: Kisumu CBD, Milimani\n📍 NAKURU: Nakuru Town, Naivasha\n📍 ELDORET: Eldoret CBD, Kapseret\n📍 KIAMBU: Thika, Ruiru, Kikuyu\n📍 And many more counties across Kenya\n\nWe have local agents in major towns to provide personalized service.",
                
                contact: "You can contact us through multiple channels:\n\n📞 PHONE: Call our main office for immediate assistance\n📧 EMAIL: Send us detailed inquiries via email\n🌐 WEBSITE: Use our contact form for specific requests\n💬 CHAT: Continue chatting with me for quick answers\n📱 WHATSAPP: Message us for instant support\n\nWe're available:\n• Monday to Friday: 8:00 AM - 6:00 PM\n• Saturday: 9:00 AM - 4:00 PM\n• Sunday: 10:00 AM - 2:00 PM\n• Emergency support: 24/7 for urgent matters\n\nVisit our contact page for detailed contact information.",
                
                // Properties and Listings
                properties: "Yes! We have an extensive selection of properties:\n\n🏠 FOR SALE: Houses, apartments, commercial buildings, land\n🏠 FOR RENT: Residential and commercial rental properties\n🏢 COMMERCIAL: Office spaces, retail shops, warehouses\n🌾 LAND: Residential plots, commercial land, agricultural land\n\nOur properties are located across Kenya in:\n• Nairobi and surrounding areas\n• Mombasa and coastal regions\n• Kisumu and western Kenya\n• Nakuru and Rift Valley\n• Eldoret and northern Kenya\n\nBrowse our properties page or tell me your specific requirements!",
                
                available_properties: "We currently have properties available in:\n\n🏠 NAIROBI: Modern apartments in Westlands, family homes in Karen, townhouses in Kilimani\n🏠 MOMBASA: Beachfront villas in Nyali, apartments in Mombasa CBD\n🏠 KISUMU: Lakefront properties, city center apartments\n🏠 NAKURU: Suburban homes, commercial spaces\n🏠 ELDORET: University area properties, business district offices\n\nPrice ranges from KSh 15,000/month for studios to KSh 500,000/month for luxury properties.\n\nWhat type of property are you looking for? I can help you find the perfect match!",
                
                // Maintenance and Services
                maintenance: "Our comprehensive maintenance services include:\n\n🔧 PREVENTIVE MAINTENANCE: Regular inspections and upkeep\n⚡ EMERGENCY REPAIRS: 24/7 emergency response team\n🏠 GENERAL REPAIRS: Plumbing, electrical, carpentry\n🧹 CLEANING SERVICES: Regular and deep cleaning\n🌿 LANDSCAPING: Garden maintenance and landscaping\n🔒 SECURITY: Security system maintenance\n📱 SMART HOME: Technology and automation support\n\nWe have a network of:\n• Licensed contractors\n• Certified technicians\n• Emergency response teams\n• Quality assurance inspectors\n\nAll work is guaranteed and insured.",
                
                rent_payment: "We offer multiple convenient payment methods:\n\n💳 BANK TRANSFERS: Direct bank transfers to our account\n📱 MOBILE MONEY: M-Pesa, Airtel Money, T-Kash\n💻 ONLINE PAYMENTS: Secure online payment portal\n🏦 BANK DEPOSITS: Cash deposits at any bank branch\n📊 AUTOMATED PAYMENTS: Set up automatic monthly payments\n\nPayment options:\n• Monthly, quarterly, or annual payments\n• Payment reminders via SMS and email\n• Online payment history and receipts\n• Late payment management\n• Payment plan arrangements for difficulties\n\nYou'll receive detailed payment instructions when you become a tenant.",
                
                // Viewing and Scheduling
                viewing: "Absolutely! We offer flexible viewing options:\n\n📅 SCHEDULED VIEWINGS: Book appointments at your convenience\n🏠 VIRTUAL TOURS: 360° virtual property tours online\n📱 VIDEO CALLS: Live video property tours via WhatsApp\n🚗 ACCOMPANIED VIEWINGS: Our agents will show you around\n⏰ FLEXIBLE TIMING: Weekdays, weekends, and evenings available\n\nTo schedule a viewing:\n• Contact us directly\n• Use our online booking system\n• Message us via WhatsApp\n• Continue chatting with me\n\nWe'll arrange a convenient time and provide directions to the property.",
                
                // Pricing and Charges
                charges: "Our service charges are competitive and transparent:\n\n🏠 PROPERTY MANAGEMENT: 8-12% of monthly rent\n💰 SALES COMMISSION: 3-5% of sale price\n🏢 COMMERCIAL MANAGEMENT: 10-15% of monthly rent\n📋 PROPERTY INSPECTIONS: KSh 2,000-5,000 per inspection\n🔧 MAINTENANCE COORDINATION: Included in management fee\n📊 MARKETING SERVICES: KSh 5,000-15,000 per property\n\nAdditional services:\n• Legal documentation: KSh 10,000-25,000\n• Property valuation: KSh 3,000-8,000\n• Tenant screening: KSh 1,000 per applicant\n• Emergency call-out: KSh 2,000-5,000\n\nContact us for a detailed quote based on your specific needs.",
                
                // Listing and Management
                listing: "To list your property with us:\n\n📋 STEP 1: Fill out our property management request form\n🏠 STEP 2: We'll conduct a free property assessment\n📊 STEP 3: Receive a detailed management proposal\n📝 STEP 4: Sign our management agreement\n🚀 STEP 5: We'll start marketing your property immediately\n\nWe'll handle:\n• Property photography and virtual tours\n• Marketing across multiple platforms\n• Tenant screening and selection\n• Lease agreement preparation\n• Rent collection and management\n• Maintenance coordination\n• Regular property inspections\n\nContact us today for a free consultation!",
                
                // Company Information
                company: "Traca Management Services Ltd:\n\n🏢 ESTABLISHED: 2004 (Over 20 years of experience)\n📍 HEADQUARTERS: Nairobi, Kenya\n🌍 COVERAGE: All 47 counties in Kenya\n👥 TEAM: Professional agents and property managers\n🏆 REPUTATION: Trusted by thousands of clients\n\nOur mission: To provide exceptional property management and real estate services across Kenya.\n\nWe specialize in:\n• Residential and commercial property management\n• Property sales and rentals\n• Investment property consulting\n• Market analysis and valuations\n• Legal compliance and documentation\n\nWhy choose us:\n✅ 20+ years of experience\n✅ Licensed and insured\n✅ 24/7 customer support\n✅ Transparent pricing\n✅ Professional team",
                
                // Fallback
                fallback: "I'm not sure I understood that. Could you please rephrase your question? I'm here to help with information about:\n\n🏠 Property sales and rentals\n🏢 Property management services\n💰 Rent collection and tenant management\n🔧 Maintenance and repairs\n📊 Marketing and advertising\n📋 Property inspections\n💼 Company advisory services\n📞 Contact information\n\nFeel free to ask me anything else! What would you like to know more about?"
            },
            sw: {
                // Core Services
                services: "Tunatoa huduma za mali pamoja na:\n\n🏠 UUZAJI WA MALI: Kununua na kuuza mali za makazi na biashara\n🏢 USIMAMIZI WA MALI: Usimamizi kamili wa mali za kukodi\n💰 UKUSANYAJI WA KODI: Ukusanyaji wa kodi na usimamizi wa wakodi\n🔧 MATENGENEZO: Kuratibu matengenezo na matengenezo ya dharura\n👥 KUWEKA WAKODI: Kutafuta na kuchunguza wakodi waliohitimu\n📋 UKAGUZI WA MALI: Tathmini za kawaida za mali na ripoti\n💼 USHAURI KWA WAMILIKI: Ushauri wa kitaalamu kwa wamiliki wa mali\n📊 UTANGAZAJI: Utangazaji wa kitaalamu wa mali\n\nTunahudumia kaunti zote 47 za Kenya na uzoefu wa zaidi ya miaka 20 tangu 2004.",
                
                property_management: "Huduma zetu za usimamizi wa mali ni pamoja na:\n\n✅ Ukusanyaji wa kodi na uchunguzi wa wakodi\n✅ Kuratibu matengenezo na matengenezo ya dharura\n✅ Ukaguzi wa mali na ripoti za hali\n✅ Ripoti za kifedha na uhasibu\n✅ Kufuata sheria na nyaraka\n✅ Utangazaji na kuweka wakodi\n✅ Msaada wa dharura masaa 24\n✅ Tathmini za kawaida za mali\n\nTunashughulikia kila kitu ili uweze kuzingatia faida ya uwekezaji wako.",
                
                sales: "Huduma zetu za uuzaji wa mali ni pamoja na:\n\n🏘️ UUZAJI WA MAKAZI: Nyumba, vyumba, nyumba za mjini\n🏢 UUZAJI WA BIASHARA: Majengo ya ofisi, maeneo ya rejareja, magorofa\n🏭 UUZAJI WA VIWANDA: Vifaa vya uzalishaji, vitengo vya uhifadhi\n🌾 UUZAJI WA ARDHI: Vipande vya makazi, ardhi ya biashara, ardhi ya kilimo\n\nTunatoa:\n• Tathmini za kitaalamu za mali\n• Utangazaji na matangazo\n• Uchunguzi na kuhitimu wanunuzi\n• Msaada wa mazungumzo na kufunga\n• Msaada wa nyaraka za kisheria",
                
                marketing: "Huduma zetu za utangazaji ni pamoja na:\n\n📱 UTANGAZAJI WA KIDIJITALI: Orodha za mtandaoni, utangazaji wa mitandao ya kijamii\n📸 UPIGA PICHA WA KITAALAMU: Picha za hali ya juu za mali\n🎥 MAZUNGUMZO YA VIRTUAL: Mazungumzo ya mali ya 360°\n📋 ORODHA ZA KINA: Maelezo ya kina ya mali\n📊 UCHAMBUZI WA SOKO: Bei na uwekaji wa soko\n📢 MATANGAZO: Kampeni za matangazo kwenye mifumo mingi\n🌐 ORODHA ZA TOVUTI: Orodha za mali kwenye tovuti yetu\n📱 UBOFAYA WA SIMU: Maonyesho ya mali yanayofaa kwa simu",
                
                renting: "Huduma zetu za kukodi ni pamoja na:\n\n🏠 KUKODI KWA MAKAZI: Nyumba, vyumba, studio\n🏢 KUKODI KWA BIASHARA: Maeneo ya ofisi, maduka ya rejareja, magorofa\n🏭 KUKODI KWA VIWANDA: Vifaa vya uzalishaji, vitengo vya uhifadhi\n🌾 KUKODI KWA ARDHI: Ardhi ya kilimo, vipande vya maendeleo\n\nTunatoa:\n• Uchunguzi wa wakodi na uchunguzi wa historia\n• Maandalizi ya makubaliano ya kukodi\n• Ukusanyaji na usimamizi wa kodi\n• Kuratibu matengenezo ya mali\n• Ukaguzi wa kawaida wa mali\n• Msaada wa kufuata sheria",
                
                // Location and Contact
                location: "Ofisi yetu kuu iko Nairobi, Kenya. Tunahudumia mali katika kaunti zote 47 za Kenya pamoja na:\n\n📍 NAIROBI: Westlands, Karen, Kilimani, Lavington, Runda\n📍 MOMBASA: Nyali, Mombasa CBD, Diani\n📍 KISUMU: Kisumu CBD, Milimani\n📍 NAKURU: Nakuru Town, Naivasha\n📍 ELDORET: Eldoret CBD, Kapseret\n📍 KIAMBU: Thika, Ruiru, Kikuyu\n📍 Na kaunti nyingine nyingi za Kenya\n\nTunao wakala wa ndani katika miji mikubwa kutoa huduma ya kibinafsi.",
                
                contact: "Unaweza kuwasiliana nasi kupitia njia nyingi:\n\n📞 SIMU: Piga simu ofisini kwetu kwa msaada wa haraka\n📧 BARUA PEPE: Tutumie maswali ya kina kupitia barua pepe\n🌐 TOVUTI: Tumia fomu yetu ya mawasiliano kwa maombi maalum\n💬 MAZUNGUMZO: Endelea kuzungumza nami kwa majibu ya haraka\n📱 WHATSAPP: Tutumie ujumbe kwa msaada wa haraka\n\nTunapatikana:\n• Jumatatu hadi Ijumaa: 8:00 asubuhi - 6:00 jioni\n• Jumamosi: 9:00 asubuhi - 4:00 jioni\n• Jumapili: 10:00 asubuhi - 2:00 jioni\n• Msaada wa dharura: masaa 24 kwa mambo ya dharura",
                
                // Properties and Listings
                properties: "Ndiyo! Tunayo mali nyingi:\n\n🏠 ZA KUUZA: Nyumba, vyumba, majengo ya biashara, ardhi\n🏠 ZA KUKODI: Mali za kukodi za makazi na biashara\n🏢 BIASHARA: Maeneo ya ofisi, maduka ya rejareja, magorofa\n🌾 ARDHI: Vipande vya makazi, ardhi ya biashara, ardhi ya kilimo\n\nMali zetu ziko katika:\n• Nairobi na maeneo ya jirani\n• Mombasa na maeneo ya pwani\n• Kisumu na magharibi mwa Kenya\n• Nakuru na Bonde la Ufa\n• Eldoret na kaskazini mwa Kenya",
                
                available_properties: "Kwa sasa tunayo mali zilizopo katika:\n\n🏠 NAIROBI: Vyumba vya kisasa Westlands, nyumba za familia Karen, nyumba za mjini Kilimani\n🏠 MOMBASA: Villa za pwani Nyali, vyumba Mombasa CBD\n🏠 KISUMU: Mali za pwani ya ziwa, vyumba vya katikati mwa jiji\n🏠 NAKURU: Nyumba za mjini, maeneo ya biashara\n🏠 ELDORET: Mali za eneo la chuo kikuu, ofisi za eneo la biashara\n\nBei zinaanzia KSh 15,000/mwezi kwa studio hadi KSh 500,000/mwezi kwa mali za anasa.\n\nUnatafuta aina gani ya mali? Ninaweza kukusaidia kupata mechi kamili!",
                
                // Maintenance and Services
                maintenance: "Huduma zetu za matengenezo ni pamoja na:\n\n🔧 MATENGENEZO YA KUKINGA: Ukaguzi wa kawaida na utunzaji\n⚡ MATENGENEZO YA DHARURA: Timu ya majibu ya dharura masaa 24\n🏠 MATENGENEZO YA JUMLA: Mifumo ya maji, umeme, ujenzi\n🧹 HUDUMA ZA USAFI: Usafi wa kawaida na wa kina\n🌿 BUSTANI: Utunzaji wa bustani na bustani\n🔒 USALAMA: Utunzaji wa mifumo ya usalama\n📱 NYUMBA ZA AKILI: Msaada wa teknolojia na automatiki\n\nTunayo mtandao wa:\n• Wakandarasi walioidhinishwa\n• Wataalamu waliohitimu\n• Timu za majibu ya dharura\n• Wakaguzi wa uhakika wa ubora",
                
                rent_payment: "Tunatoa njia nyingi za malipo:\n\n💳 UHAMISHO WA BENKI: Uhamisho wa moja kwa moja kwenye akaunti yetu\n📱 PESA ZA SIMU: M-Pesa, Airtel Money, T-Kash\n💻 MALIPO YA MTANDAONI: Portal salama ya malipo ya mtandaoni\n🏦 AMANA ZA BENKI: Amana za pesa taslimu katika tawi lolote la benki\n📊 MALIPO YA AUTOMATIKI: Panga malipo ya kila mwezi ya kiotomatiki\n\nChaguzi za malipo:\n• Malipo ya kila mwezi, robo, au kila mwaka\n• Ukumbusho wa malipo kupitia SMS na barua pepe\n• Historia ya malipo ya mtandaoni na risiti\n• Usimamizi wa malipo ya kuchelewa\n• Mipango ya malipo kwa matatizo",
                
                // Viewing and Scheduling
                viewing: "Bila shaka! Tunatoa chaguzi za kutazama:\n\n📅 KUTAZAMA KWA MIPANGO: Panga miadi kwa urahisi wako\n🏠 MAZUNGUMZO YA VIRTUAL: Mazungumzo ya mali ya 360° mtandaoni\n📱 SIMU ZA VIDEO: Mazungumzo ya mali ya moja kwa moja kupitia WhatsApp\n🚗 KUTAZAMA KWA MSHIRIKA: Wakala wetu watakuonyesha\n⏰ MUDA WA KUBADILIKA: Siku za kazi, wikendi, na jioni zinawezekana\n\nKupanga kutazama:\n• Wasiliana nasi moja kwa moja\n• Tumia mfumo wetu wa kupanga mtandaoni\n• Tutumie ujumbe kupitia WhatsApp\n• Endelea kuzungumza nami\n\nTutapanga muda unaokufaa na kutoa maelekezo ya mali.",
                
                // Pricing and Charges
                charges: "Malipo yetu ya huduma ni ya ushindani na wazi:\n\n🏠 USIMAMIZI WA MALI: 8-12% ya kodi ya kila mwezi\n💰 KOMISHENI YA UUZAJI: 3-5% ya bei ya uuzaji\n🏢 USIMAMIZI WA BIASHARA: 10-15% ya kodi ya kila mwezi\n📋 UKAGUZI WA MALI: KSh 2,000-5,000 kwa kila ukaguzi\n🔧 KURATIBU MATENGENEZO: Imejumuishwa katika ada ya usimamizi\n📊 HUDUMA ZA UTANGAZAJI: KSh 5,000-15,000 kwa kila mali\n\nHuduma za ziada:\n• Nyaraka za kisheria: KSh 10,000-25,000\n• Tathmini ya mali: KSh 3,000-8,000\n• Uchunguzi wa wakodi: KSh 1,000 kwa kila mwombaji\n• Wito wa dharura: KSh 2,000-5,000",
                
                // Listing and Management
                listing: "Kuweka mali yako chini yetu:\n\n📋 HATUA 1: Jaza fomu yetu ya ombi la usimamizi wa mali\n🏠 HATUA 2: Tutafanya tathmini ya mali bila malipo\n📊 HATUA 3: Pokea pendekezo la kina la usimamizi\n📝 HATUA 4: Saini makubaliano yetu ya usimamizi\n🚀 HATUA 5: Tutaanza kutangaza mali yako mara moja\n\nTutashughulikia:\n• Upigaji picha wa mali na mazungumzo ya virtual\n• Utangazaji kwenye mifumo mingi\n• Uchunguzi na uteuzi wa wakodi\n• Maandalizi ya makubaliano ya kukodi\n• Ukusanyaji na usimamizi wa kodi\n• Kuratibu matengenezo\n• Ukaguzi wa kawaida wa mali",
                
                // Company Information
                company: "Traca Management Services Ltd:\n\n🏢 IMEANZISHWA: 2004 (Uzoefu wa zaidi ya miaka 20)\n📍 MAKAO MAKUU: Nairobi, Kenya\n🌍 ENEO: Kaunti zote 47 za Kenya\n👥 TIMU: Wakala wa kitaalamu na wasimamizi wa mali\n🏆 SIFA: Inaaminika na maelfu ya wateja\n\nDhamira yetu: Kutoa huduma bora za usimamizi wa mali na mali katika Kenya.\n\nTunajihusisha na:\n• Usimamizi wa mali za makazi na biashara\n• Uuzaji na kukodi kwa mali\n• Ushauri wa uwekezaji wa mali\n• Uchambuzi wa soko na tathmini\n• Kufuata sheria na nyaraka\n\nKwa nini utuchague:\n✅ Uzoefu wa miaka 20+\n✅ Imelidhinishwa na kufunikwa\n✅ Msaada wa wateja masaa 24\n✅ Bei wazi\n✅ Timu ya kitaalamu",
                
                // Fallback
                fallback: "Samahani, sijaelewa vizuri. Tafadhali fafanua swali lako. Niko hapa kukusaidia kuhusu:\n\n🏠 Uuzaji na kukodi kwa mali\n🏢 Huduma za usimamizi wa mali\n💰 Ukusanyaji wa kodi na usimamizi wa wakodi\n🔧 Matengenezo na matengenezo\n📊 Utangazaji na matangazo\n📋 Ukaguzi wa mali\n💼 Huduma za ushauri kwa wamiliki\n📞 Taarifa za mawasiliano\n\nJisikie huru kuuliza chochote kingine! Unataka kujua zaidi kuhusu nini?"
            }
        };

        // Check for keywords and return appropriate response
        const responses = faqs[this.currentLanguage];
        
        // Core Services
        if (lowerMessage.includes('service') || lowerMessage.includes('huduma') || lowerMessage.includes('what do you offer')) {
            return responses.services;
        } else if (lowerMessage.includes('property management') || lowerMessage.includes('usimamizi wa mali') || lowerMessage.includes('manage property')) {
            return responses.property_management;
        } else if (lowerMessage.includes('sales') || lowerMessage.includes('sell') || lowerMessage.includes('buy') || lowerMessage.includes('uuza') || lowerMessage.includes('nunua')) {
            return responses.sales;
        } else if (lowerMessage.includes('marketing') || lowerMessage.includes('advertise') || lowerMessage.includes('promote') || lowerMessage.includes('utangazaji')) {
            return responses.marketing;
        } else if (lowerMessage.includes('rent') || lowerMessage.includes('rental') || lowerMessage.includes('kukodi') || lowerMessage.includes('kodi')) {
            return responses.renting;
        }
        
        // Location and Contact
        else if (lowerMessage.includes('office') || lowerMessage.includes('location') || lowerMessage.includes('where') || lowerMessage.includes('wapi') || lowerMessage.includes('ofisi')) {
            return responses.location;
        } else if (lowerMessage.includes('contact') || lowerMessage.includes('phone') || lowerMessage.includes('email') || lowerMessage.includes('kuwasiliana') || lowerMessage.includes('simu')) {
            return responses.contact;
        }
        
        // Properties and Listings
        else if (lowerMessage.includes('available') || lowerMessage.includes('properties') || lowerMessage.includes('nyumba') || lowerMessage.includes('wazi') || lowerMessage.includes('listings')) {
            return responses.available_properties;
        } else if (lowerMessage.includes('property') || lowerMessage.includes('house') || lowerMessage.includes('apartment') || lowerMessage.includes('mali') || lowerMessage.includes('nyumba')) {
            return responses.properties;
        }
        
        // Maintenance and Services
        else if (lowerMessage.includes('maintenance') || lowerMessage.includes('repair') || lowerMessage.includes('fix') || lowerMessage.includes('matengenezo') || lowerMessage.includes('remedy')) {
            return responses.maintenance;
        } else if (lowerMessage.includes('pay') || lowerMessage.includes('payment') || lowerMessage.includes('rent payment') || lowerMessage.includes('kodi') || lowerMessage.includes('lipa') || lowerMessage.includes('malipo')) {
            return responses.rent_payment;
        }
        
        // Viewing and Scheduling
        else if (lowerMessage.includes('viewing') || lowerMessage.includes('view') || lowerMessage.includes('visit') || lowerMessage.includes('schedule') || lowerMessage.includes('kutazama') || lowerMessage.includes('panga') || lowerMessage.includes('tembelea')) {
            return responses.viewing;
        }
        
        // Pricing and Charges
        else if (lowerMessage.includes('charge') || lowerMessage.includes('cost') || lowerMessage.includes('price') || lowerMessage.includes('fee') || lowerMessage.includes('kiwango') || lowerMessage.includes('toza') || lowerMessage.includes('bei') || lowerMessage.includes('malipo')) {
            return responses.charges;
        }
        
        // Listing and Management
        else if (lowerMessage.includes('list') || lowerMessage.includes('manage') || lowerMessage.includes('management') || lowerMessage.includes('kuweka') || lowerMessage.includes('usimamizi') || lowerMessage.includes('list property')) {
            return responses.listing;
        }
        
        // Company Information
        else if (lowerMessage.includes('company') || lowerMessage.includes('about') || lowerMessage.includes('traca') || lowerMessage.includes('kampuni') || lowerMessage.includes('kuhusu')) {
            return responses.company;
        }
        
        // Fallback
        else {
            return responses.fallback;
        }
    }

    showNotificationBadge() {
        const badge = document.getElementById('notification-badge');
        badge.style.display = 'block';
    }

    playNotificationSound() {
        // Create a simple notification sound
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
        oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.3);
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatbot-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    loadChatHistory() {
        // Load chat history from localStorage if available
        const savedHistory = localStorage.getItem('traca-chatbot-history');
        if (savedHistory) {
            this.chatHistory = JSON.parse(savedHistory);
        }
    }

    saveChatHistory() {
        // Save chat history to localStorage
        localStorage.setItem('traca-chatbot-history', JSON.stringify(this.chatHistory));
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if chatbot is already initialized
    if (!document.getElementById('traca-chatbot')) {
        window.tracaChatbotInstance = new TracaChatbot();
    }
});

// Quick action function
function quickAction(action) {
    const chatbot = window.tracaChatbotInstance;
    if (!chatbot) return;
    
    const actions = {
        contact: chatbot.currentLanguage === 'en' ? "How can I contact you?" : "Ninawezaje kuwasiliana nanyi?",
        properties: chatbot.currentLanguage === 'en' ? "Show me available properties" : "Nionyeshe mali zilizopo",
        services: chatbot.currentLanguage === 'en' ? "What services do you offer?" : "Mna toa huduma gani?"
    };
    
    document.getElementById('chatbot-input').value = actions[action];
    chatbot.sendMessage();
}

// Export for potential external use
window.TracaChatbot = TracaChatbot;
window.quickAction = quickAction;
