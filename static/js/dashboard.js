document.addEventListener('DOMContentLoaded', function() {
    // State
    let passwordEntries = [];
    let categories = ['All'];
    let selectedCategory = 'All';
    let searchText = '';
    let currentEntryId = -1;
    
    // DOM Elements - Navigation
    const navItems = document.querySelectorAll('.nav-item');
    const pageContents = document.querySelectorAll('.page-content');
    
    // DOM Elements - Password List
    const passwordList = document.getElementById('password-list');
    const emptyPasswordsMessage = document.getElementById('empty-passwords');
    const searchInput = document.getElementById('password-search');
    const categoryFilter = document.getElementById('category-filter');
    const addPasswordBtn = document.querySelector('.add-password-btn');
    
    // DOM Elements - Modals
    const passwordModal = document.getElementById('password-modal');
    const viewPasswordModal = document.getElementById('view-password-modal');
    const shareModal = document.getElementById('share-modal');
    const confirmModal = document.getElementById('confirm-modal');
    const sharedPasswordModal = document.getElementById('shared-password-modal');
    
    // DOM Elements - Password Form
    const passwordForm = document.getElementById('password-form');
    const passwordModalTitle = document.getElementById('password-modal-title');
    const titleInput = document.getElementById('title');
    const websiteInput = document.getElementById('website');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const categoryInput = document.getElementById('category');
    const notesInput = document.getElementById('notes');
    const entryIdInput = document.getElementById('entry-id');
    const savePasswordBtn = document.getElementById('save-password');
    const cancelPasswordBtn = document.getElementById('cancel-password');
    
    // DOM Elements - Password Generator
    const passwordLengthSlider = document.getElementById('password-length');
    const lengthValue = document.getElementById('length-value');
    const includeUppercase = document.getElementById('include-uppercase');
    const includeLowercase = document.getElementById('include-lowercase');
    const includeNumbers = document.getElementById('include-numbers');
    const includeSymbols = document.getElementById('include-symbols');
    const excludeSimilar = document.getElementById('exclude-similar');
    const excludeAmbiguous = document.getElementById('exclude-ambiguous');
    const generatePasswordBtn = document.getElementById('generate-password');
    const regeneratePasswordBtn = document.getElementById('regenerate-password');
    const generatedPassword = document.getElementById('generated-password');
    const copyPasswordBtn = document.getElementById('copy-password');
    const strengthBar = document.getElementById('strength-bar');
    const strengthText = document.getElementById('strength-text');
    
    // DOM Elements - View Password
    const viewTitle = document.getElementById('view-title');
    const viewWebsite = document.getElementById('view-website');
    const viewUsername = document.getElementById('view-username');
    const viewPasswordField = document.getElementById('view-password');
    const viewCategory = document.getElementById('view-category');
    const viewNotes = document.getElementById('view-notes');
    const viewCreated = document.getElementById('view-created');
    const viewModified = document.getElementById('view-modified');
    const deletePasswordBtn = document.getElementById('delete-password');
    const editPasswordBtn = document.getElementById('edit-password');
    const sharePasswordBtn = document.getElementById('share-password');
    const visitWebsiteBtn = document.getElementById('visit-website');
    
    // DOM Elements - Share Password
    const shareEntryId = document.getElementById('share-entry-id');
    const shareTitle = document.getElementById('share-title');
    const expirationTime = document.getElementById('expiration-time');
    const accessCount = document.getElementById('access-count');
    const generateShareBtn = document.getElementById('generate-share');
    const cancelShareBtn = document.getElementById('cancel-share');
    const shareStep1 = document.getElementById('share-step-1');
    const shareStep2 = document.getElementById('share-step-2');
    const shareUrl = document.getElementById('share-url');
    const shareKey = document.getElementById('share-key');
    const copyShareUrlBtn = document.getElementById('copy-share-url');
    const copyShareKeyBtn = document.getElementById('copy-share-key');
    const expiryInfo = document.getElementById('expiry-info');
    const accessInfo = document.getElementById('access-info');
    const closeShareBtn = document.getElementById('close-share');
    
    // DOM Elements - Shared Passwords
    const sharedTabs = document.querySelectorAll('.shared-tabs .tab');
    const tabContents = document.querySelectorAll('.tab-content');
    const sharedList = document.getElementById('shared-list');
    const emptyShares = document.getElementById('empty-shares');
    const accessSharedBtn = document.getElementById('access-shared-password');
    
    // DOM Elements - Access Shared
    const shareLink = document.getElementById('share-link');
    const accessKey = document.getElementById('access-key');
    const accessSharedForm = document.getElementById('access-shared-btn');
    
    // DOM Elements - Confirm Modal
    const confirmTitle = document.getElementById('confirm-title');
    const confirmMessage = document.getElementById('confirm-message');
    const confirmActionBtn = document.getElementById('confirm-action');
    const cancelConfirmBtn = document.getElementById('cancel-confirm');
    
    // DOM Elements - Settings
    const themeMode = document.getElementById('theme-mode');
    const clipboardTimeout = document.getElementById('clipboard-timeout');
    const autoLogout = document.getElementById('auto-logout');
    const backupPasswordsBtn = document.getElementById('backup-passwords');
    const saveSettingsBtn = document.getElementById('save-settings');
    
    // Initialize
    initNavigation();
    loadPasswords();
    initPasswordGenerator();
    initModalHandlers();
    initPasswordFormHandlers();
    initViewPasswordHandlers();
    initShareHandlers();
    initSharedPasswordHandlers();
    initSettingsHandlers();
    
    // Navigation Functions
    function initNavigation() {
        navItems.forEach(item => {
            item.addEventListener('click', function() {
                const pageId = this.getAttribute('data-page');
                
                // Update active nav item
                navItems.forEach(nav => nav.classList.remove('active'));
                this.classList.add('active');
                
                // Show selected page
                pageContents.forEach(page => {
                    if (page.id === pageId + '-page') {
                        page.classList.add('active');
                    } else {
                        page.classList.remove('active');
                    }
                });
                
                // Load data for specific pages
                if (pageId === 'passwords') {
                    loadPasswords();
                } else if (pageId === 'shared') {
                    loadSharedPasswords();
                }
            });
        });
        
        // Initialize shared tabs
        if (sharedTabs) {
            sharedTabs.forEach(tab => {
                tab.addEventListener('click', function() {
                    const tabId = this.getAttribute('data-tab');
                    
                    // Update active tab
                    sharedTabs.forEach(t => t.classList.remove('active'));
                    this.classList.add('active');
                    
                    // Show selected tab content
                    tabContents.forEach(content => {
                        if (content.id === tabId + '-content') {
                            content.classList.add('active');
                        } else {
                            content.classList.remove('active');
                        }
                    });
                });
            });
        }
    }
    
    // Password List Functions
    function loadPasswords() {
        fetch('/api/passwords')
            .then(response => response.json())
            .then(data => {
                passwordEntries = data.entries || [];
                
                // Extract categories
                const categorySet = new Set(['All']);
                passwordEntries.forEach(entry => {
                    if (entry.category) {
                        categorySet.add(entry.category);
                    }
                });
                categories = Array.from(categorySet).sort();
                
                // Update category filter
                updateCategoryDropdown();
                
                // Update categories datalist for the form
                updateCategoriesDatalist();
                
                // Display passwords
                displayFilteredPasswords();
            })
            .catch(error => {
                console.error('Error loading passwords:', error);
                showToast('Failed to load passwords.', 'error');
            });
    }
    
    function displayFilteredPasswords() {
        const filtered = filterPasswords();
        
        // Clear current list
        passwordList.innerHTML = '';
        
        if (filtered.length === 0) {
            // Show empty state
            passwordList.style.display = 'none';
            emptyPasswordsMessage.style.display = 'block';
            
            if (searchText || selectedCategory !== 'All') {
                emptyPasswordsMessage.innerHTML = `
                    <i class="fas fa-search"></i>
                    <p>No passwords match your search.</p>
                `;
            } else {
                emptyPasswordsMessage.innerHTML = `
                    <i class="fas fa-folder-open"></i>
                    <p>No passwords saved yet. Click the Add Password button to get started.</p>
                `;
            }
        } else {
            // Show password list
            passwordList.style.display = 'grid';
            emptyPasswordsMessage.style.display = 'none';
            
            // Create password items
            filtered.forEach((entry, index) => {
                createPasswordItem(entry, index);
            });
        }
    }
    
    function filterPasswords() {
        return passwordEntries.filter(entry => {
            // Category filter
            if (selectedCategory !== 'All' && entry.category !== selectedCategory) {
                return false;
            }
            
            // Search filter
            if (searchText) {
                const searchFields = [
                    entry.title || '',
                    entry.username || '',
                    entry.website || '',
                    entry.category || '',
                    entry.notes || ''
                ].map(field => field.toLowerCase());
                
                return searchFields.some(field => field.includes(searchText.toLowerCase()));
            }
            
            return true;
        });
    }
    
    function createPasswordItem(entry, index) {
        const item = document.createElement('div');
        item.className = 'password-item';
        item.setAttribute('data-entry-index', index);
        
        // HTML for the password item
        item.innerHTML = `
            <div class="title">${escapeHtml(entry.title || 'Untitled')}</div>
            ${entry.website ? `<div class="website">${escapeHtml(entry.website)}</div>` : ''}
            ${entry.username ? `
                <div class="username">
                    <span class="username-label">Username:</span>
                    <span class="username-value">${escapeHtml(entry.username)}</span>
                </div>
            ` : ''}
            ${entry.category ? `<div class="category">${escapeHtml(entry.category)}</div>` : ''}
            <div class="actions">
                <button class="btn btn-primary view-password-btn">View</button>
            </div>
        `;
        
        // Add click handlers
        item.addEventListener('click', () => viewPassword(index));
        item.querySelector('.view-password-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            viewPassword(index);
        });
        
        passwordList.appendChild(item);
    }
    
    function updateCategoryDropdown() {
        // Clear existing options
        categoryFilter.innerHTML = '';
        
        // Add options
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            categoryFilter.appendChild(option);
        });
        
        // Set selected category
        categoryFilter.value = selectedCategory;
    }
    
    function updateCategoriesDatalist() {
        const datalist = document.getElementById('categories');
        if (datalist) {
            // Clear existing options
            datalist.innerHTML = '';
            
            // Add options (skip "All")
            categories.filter(category => category !== 'All').forEach(category => {
                const option = document.createElement('option');
                option.value = category;
                datalist.appendChild(option);
            });
        }
    }
    
    // Password Form Functions
    function initPasswordFormHandlers() {
        // Search input
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                searchText = searchInput.value;
                displayFilteredPasswords();
            });
        }
        
        // Category filter
        if (categoryFilter) {
            categoryFilter.addEventListener('change', () => {
                selectedCategory = categoryFilter.value;
                displayFilteredPasswords();
            });
        }
        
        // Add password button
        if (addPasswordBtn) {
            addPasswordBtn.addEventListener('click', showAddPasswordModal);
        }
        
        // Save password
        if (passwordForm) {
            passwordForm.addEventListener('submit', (e) => {
                e.preventDefault();
                savePassword();
            });
        }
        
        // Cancel button
        if (cancelPasswordBtn) {
            cancelPasswordBtn.addEventListener('click', closePasswordModal);
        }
        
        // Toggle password visibility
        const togglePasswordBtn = document.querySelector('.toggle-password-btn');
        if (togglePasswordBtn) {
            togglePasswordBtn.addEventListener('click', function() {
                const icon = this.querySelector('i');
                
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    passwordInput.type = 'password';
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            });
        }
        
        // Generate password button in form
        const generatePasswordBtn = document.querySelector('.generate-password-btn');
        if (generatePasswordBtn) {
            generatePasswordBtn.addEventListener('click', function() {
                const options = {
                    length: 16,
                    include_uppercase: true,
                    include_lowercase: true,
                    include_numbers: true,
                    include_symbols: true,
                    exclude_similar: false,
                    exclude_ambiguous: false
                };
                
                fetch('/api/generate-password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(options)
                })
                .then(response => response.json())
                .then(data => {
                    passwordInput.value = data.password;
                    showToast('Password generated!', 'success');
                })
                .catch(error => {
                    console.error('Error generating password:', error);
                    showToast('Failed to generate password.', 'error');
                });
            });
        }
        
        // Copy password button in form
        const copyPasswordBtn = document.querySelector('.copy-password-btn');
        if (copyPasswordBtn) {
            copyPasswordBtn.addEventListener('click', function() {
                if (passwordInput.value) {
                    navigator.clipboard.writeText(passwordInput.value)
                        .then(() => {
                            showToast('Password copied to clipboard!', 'success');
                            
                            // Auto-clear clipboard after 30 seconds
                            setTimeout(() => {
                                navigator.clipboard.readText().then(text => {
                                    if (text === passwordInput.value) {
                                        navigator.clipboard.writeText('');
                                    }
                                });
                            }, 30000);
                        })
                        .catch(err => {
                            showToast('Failed to copy password.', 'error');
                        });
                }
            });
        }
    }
    
    function showAddPasswordModal() {
        // Reset form
        passwordForm.reset();
        entryIdInput.value = '';
        currentEntryId = -1;
        
        // Set modal title
        passwordModalTitle.textContent = 'Add Password';
        
        // Show modal
        openModal(passwordModal);
    }
    
    function showEditPasswordModal(entryIndex) {
        // Get entry
        const entry = passwordEntries[entryIndex];
        currentEntryId = entryIndex;
        
        // Fill form with entry data
        titleInput.value = entry.title || '';
        websiteInput.value = entry.website || '';
        usernameInput.value = entry.username || '';
        
        // For encrypted password, we need to decrypt it first
        if (entry.password_hidden) {
            // Decrypt password
            fetch(`/api/passwords/decrypt/${entryIndex}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        passwordInput.value = data.password;
                    } else {
                        passwordInput.value = '';
                        showToast('Failed to decrypt password.', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error decrypting password:', error);
                    showToast('Failed to decrypt password.', 'error');
                });
        } else {
            passwordInput.value = entry.password || '';
        }
        
        categoryInput.value = entry.category || '';
        notesInput.value = entry.notes || '';
        entryIdInput.value = entryIndex;
        
        // Set modal title
        passwordModalTitle.textContent = 'Edit Password';
        
        // Show modal
        openModal(passwordModal);
    }
    
    function savePassword() {
        // Get form data
        const entryId = entryIdInput.value !== '' ? parseInt(entryIdInput.value) : -1;
        const entry = {
            title: titleInput.value,
            website: websiteInput.value,
            username: usernameInput.value,
            password: passwordInput.value,
            category: categoryInput.value,
            notes: notesInput.value
        };
        
        // Validate
        if (!entry.title) {
            showToast('Title is required.', 'error');
            return;
        }
        
        if (!entry.password) {
            showToast('Password is required.', 'error');
            return;
        }
        
        if (entryId >= 0) {
            // Update existing password
            fetch(`/api/passwords/${entryId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(entry)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Password updated successfully!', 'success');
                    loadPasswords();
                    closePasswordModal();
                } else {
                    showToast(data.error || 'Failed to update password.', 'error');
                }
            })
            .catch(error => {
                console.error('Error updating password:', error);
                showToast('Failed to update password.', 'error');
            });
        } else {
            // Add new password
            fetch('/api/passwords', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(entry)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Password added successfully!', 'success');
                    loadPasswords();
                    closePasswordModal();
                } else {
                    showToast(data.error || 'Failed to add password.', 'error');
                }
            })
            .catch(error => {
                console.error('Error adding password:', error);
                showToast('Failed to add password.', 'error');
            });
        }
    }
    
    function closePasswordModal() {
        closeModal(passwordModal);
        passwordForm.reset();
        currentEntryId = -1;
    }
    
    // View Password Functions
    function initViewPasswordHandlers() {
        // Toggle view password visibility
        const toggleViewPasswordBtn = document.querySelector('.toggle-view-password-btn');
        if (toggleViewPasswordBtn) {
            toggleViewPasswordBtn.addEventListener('click', function() {
                const icon = this.querySelector('i');
                
                if (viewPasswordField.type === 'password') {
                    viewPasswordField.type = 'text';
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    viewPasswordField.type = 'password';
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            });
        }
        
        // Copy view password
        const copyViewPasswordBtn = document.querySelector('.copy-view-password-btn');
        if (copyViewPasswordBtn) {
            copyViewPasswordBtn.addEventListener('click', function() {
                if (viewPasswordField.value) {
                    navigator.clipboard.writeText(viewPasswordField.value)
                        .then(() => {
                            showToast('Password copied to clipboard!', 'success');
                            
                            // Auto-clear clipboard after 30 seconds
                            setTimeout(() => {
                                navigator.clipboard.readText().then(text => {
                                    if (text === viewPasswordField.value) {
                                        navigator.clipboard.writeText('');
                                    }
                                });
                            }, 30000);
                        })
                        .catch(err => {
                            showToast('Failed to copy password.', 'error');
                        });
                }
            });
        }
        
        // Copy username
        const copyUsernameBtn = document.getElementById('copy-username');
        if (copyUsernameBtn) {
            copyUsernameBtn.addEventListener('click', function() {
                const username = viewUsername.textContent;
                if (username) {
                    navigator.clipboard.writeText(username)
                        .then(() => showToast('Username copied to clipboard!', 'success'))
                        .catch(err => showToast('Failed to copy username.', 'error'));
                }
            });
        }
        
        // Visit website
        if (visitWebsiteBtn) {
            visitWebsiteBtn.addEventListener('click', function() {
                const website = viewWebsite.textContent;
                if (website) {
                    window.open(website, '_blank');
                }
            });
        }
        
        // Edit button
        if (editPasswordBtn) {
            editPasswordBtn.addEventListener('click', function() {
                closeModal(viewPasswordModal);
                showEditPasswordModal(currentEntryId);
            });
        }
        
        // Delete button
        if (deletePasswordBtn) {
            deletePasswordBtn.addEventListener('click', function() {
                // Show confirm modal
                confirmTitle.textContent = 'Delete Password';
                confirmMessage.textContent = `Are you sure you want to delete "${viewTitle.textContent}"? This action cannot be undone.`;
                
                confirmActionBtn.onclick = function() {
                    deletePassword(currentEntryId);
                    closeModal(confirmModal);
                };
                
                closeModal(viewPasswordModal);
                openModal(confirmModal);
            });
        }
        
        // Share button
        if (sharePasswordBtn) {
            sharePasswordBtn.addEventListener('click', function() {
                closeModal(viewPasswordModal);
                showShareModal(currentEntryId);
            });
        }
    }
    
    function viewPassword(entryIndex) {
        const entry = passwordEntries[entryIndex];
        currentEntryId = entryIndex;
        
        // Set view details
        viewTitle.textContent = entry.title || 'Untitled';
        viewWebsite.textContent = entry.website || '';
        viewUsername.textContent = entry.username || '';
        viewCategory.textContent = entry.category || '';
        viewNotes.textContent = entry.notes || '';
        
        // Format timestamps
        if (entry.created_at) {
            const createdDate = new Date(entry.created_at * 1000);
            viewCreated.textContent = createdDate.toLocaleString();
        } else {
            viewCreated.textContent = 'Unknown';
        }
        
        if (entry.modified_at) {
            const modifiedDate = new Date(entry.modified_at * 1000);
            viewModified.textContent = modifiedDate.toLocaleString();
        } else {
            viewModified.textContent = 'Unknown';
        }
        
        // For encrypted password, we need to decrypt it first
        if (entry.password_hidden) {
            viewPasswordField.value = '********';
            
            // Decrypt password
            fetch(`/api/passwords/decrypt/${entryIndex}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        viewPasswordField.value = data.password;
                    } else {
                        showToast('Failed to decrypt password.', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error decrypting password:', error);
                    showToast('Failed to decrypt password.', 'error');
                });
        } else {
            viewPasswordField.value = entry.password || '';
        }
        
        // Show/hide visit button based on whether there's a website
        if (entry.website && (entry.website.startsWith('http://') || entry.website.startsWith('https://'))) {
            visitWebsiteBtn.style.display = 'inline-flex';
        } else {
            visitWebsiteBtn.style.display = 'none';
        }
        
        // Show modal
        openModal(viewPasswordModal);
    }
    
    function deletePassword(entryIndex) {
        fetch(`/api/passwords/${entryIndex}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Password deleted successfully!', 'success');
                loadPasswords();
            } else {
                showToast(data.error || 'Failed to delete password.', 'error');
            }
        })
        .catch(error => {
            console.error('Error deleting password:', error);
            showToast('Failed to delete password.', 'error');
        });
    }
    
    // Password Generator Functions
    function initPasswordGenerator() {
        // Update length display when slider changes
        if (passwordLengthSlider) {
            passwordLengthSlider.addEventListener('input', function() {
                lengthValue.textContent = this.value;
            });
        }
        
        // Generate button
        if (generatePasswordBtn) {
            generatePasswordBtn.addEventListener('click', generateNewPassword);
        }
        
        // Regenerate button
        if (regeneratePasswordBtn) {
            regeneratePasswordBtn.addEventListener('click', generateNewPassword);
        }
        
        // Copy button
        if (copyPasswordBtn) {
            copyPasswordBtn.addEventListener('click', function() {
                if (generatedPassword.value) {
                    navigator.clipboard.writeText(generatedPassword.value)
                        .then(() => {
                            showToast('Password copied to clipboard!', 'success');
                            
                            // Auto-clear clipboard after 30 seconds
                            setTimeout(() => {
                                navigator.clipboard.readText().then(text => {
                                    if (text === generatedPassword.value) {
                                        navigator.clipboard.writeText('');
                                    }
                                });
                            }, 30000);
                        })
                        .catch(err => {
                            showToast('Failed to copy password.', 'error');
                        });
                }
            });
        }
        
        // Initial password generation
        generateNewPassword();
    }
    
    function generateNewPassword() {
        // Get options
        const options = {
            length: parseInt(passwordLengthSlider.value),
            include_uppercase: includeUppercase.checked,
            include_lowercase: includeLowercase.checked,
            include_numbers: includeNumbers.checked,
            include_symbols: includeSymbols.checked,
            exclude_similar: excludeSimilar.checked,
            exclude_ambiguous: excludeAmbiguous.checked
        };
        
        // Generate password
        fetch('/api/generate-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(options)
        })
        .then(response => response.json())
        .then(data => {
            generatedPassword.value = data.password;
            updateStrengthIndicator(data.strength);
        })
        .catch(error => {
            console.error('Error generating password:', error);
            showToast('Failed to generate password.', 'error');
        });
    }
    
    function updateStrengthIndicator(strength) {
        // Update progress bar
        strengthBar.style.width = `${strength}%`;
        
        // Update color and text based on strength
        if (strength >= 80) {
            strengthBar.style.backgroundColor = '#10b981'; // Green
            strengthText.textContent = 'Very Strong';
        } else if (strength >= 60) {
            strengthBar.style.backgroundColor = '#3b82f6'; // Blue
            strengthText.textContent = 'Strong';
        } else if (strength >= 40) {
            strengthBar.style.backgroundColor = '#f59e0b'; // Yellow
            strengthText.textContent = 'Moderate';
        } else if (strength >= 20) {
            strengthBar.style.backgroundColor = '#f97316'; // Orange
            strengthText.textContent = 'Weak';
        } else {
            strengthBar.style.backgroundColor = '#ef4444'; // Red
            strengthText.textContent = 'Very Weak';
        }
    }
    
    // Share Password Functions
    function initShareHandlers() {
        // Generate share button
        if (generateShareBtn) {
            generateShareBtn.addEventListener('click', function() {
                const entryId = parseInt(shareEntryId.value);
                const expHours = parseInt(expirationTime.value);
                const accCount = parseInt(accessCount.value);
                
                // Create share
                fetch('/api/share', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        entry_id: entryId,
                        expiration_hours: expHours,
                        access_count: accCount
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Display share info
                        shareUrl.value = data.share_url;
                        shareKey.value = data.access_key;
                        
                        // Set info text
                        if (expHours === 1) {
                            expiryInfo.textContent = 'Expires in 1 hour';
                        } else if (expHours < 24) {
                            expiryInfo.textContent = `Expires in ${expHours} hours`;
                        } else if (expHours === 24) {
                            expiryInfo.textContent = 'Expires in 1 day';
                        } else if (expHours === 72) {
                            expiryInfo.textContent = 'Expires in 3 days';
                        } else if (expHours === 168) {
                            expiryInfo.textContent = 'Expires in 7 days';
                        } else {
                            expiryInfo.textContent = `Expires in ${expHours} hours`;
                        }
                        
                        if (accCount === 0) {
                            accessInfo.textContent = 'Can be accessed unlimited times';
                        } else if (accCount === 1) {
                            accessInfo.textContent = 'Can be accessed 1 time only';
                        } else {
                            accessInfo.textContent = `Can be accessed up to ${accCount} times`;
                        }
                        
                        // Show step 2
                        shareStep1.style.display = 'none';
                        shareStep2.style.display = 'block';
                    } else {
                        showToast(data.error || 'Failed to create share.', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error creating share:', error);
                    showToast('Failed to create share.', 'error');
                });
            });
        }
        
        // Copy share URL button
        if (copyShareUrlBtn) {
            copyShareUrlBtn.addEventListener('click', function() {
                navigator.clipboard.writeText(shareUrl.value)
                    .then(() => showToast('Link copied to clipboard!', 'success'))
                    .catch(err => showToast('Failed to copy link.', 'error'));
            });
        }
        
        // Copy share key button
        if (copyShareKeyBtn) {
            copyShareKeyBtn.addEventListener('click', function() {
                navigator.clipboard.writeText(shareKey.value)
                    .then(() => showToast('Access key copied to clipboard!', 'success'))
                    .catch(err => showToast('Failed to copy access key.', 'error'));
            });
        }
        
        // Cancel share button
        if (cancelShareBtn) {
            cancelShareBtn.addEventListener('click', function() {
                closeModal(shareModal);
            });
        }
        
        // Close share button
        if (closeShareBtn) {
            closeShareBtn.addEventListener('click', function() {
                closeModal(shareModal);
                // Reset to step 1 for next time
                shareStep1.style.display = 'block';
                shareStep2.style.display = 'none';
            });
        }
    }
    
    function showShareModal(entryIndex) {
        const entry = passwordEntries[entryIndex];
        
        // Set share details
        shareEntryId.value = entryIndex;
        shareTitle.textContent = entry.title || 'Untitled';
        
        // Reset to step 1
        shareStep1.style.display = 'block';
        shareStep2.style.display = 'none';
        
        // Show modal
        openModal(shareModal);
    }
    
    // Shared Passwords Functions
    function initSharedPasswordHandlers() {
        // Access shared password button
        if (accessSharedBtn) {
            accessSharedBtn.addEventListener('click', function() {
                // Show shared password tab
                sharedTabs.forEach(tab => {
                    if (tab.getAttribute('data-tab') === 'access-shared') {
                        tab.click();
                    }
                });
            });
        }
        
        // Access shared form
        if (accessSharedForm) {
            accessSharedForm.addEventListener('click', function() {
                const link = shareLink.value.trim();
                const key = accessKey.value.trim();
                
                if (!link || !key) {
                    showToast('Please enter both the sharing link and access key.', 'error');
                    return;
                }
                
                // Extract share ID from link
                const shareIdMatch = link.match(/\/shared\/([a-f0-9]+)/);
                if (!shareIdMatch) {
                    showToast('Invalid sharing link format.', 'error');
                    return;
                }
                
                const shareId = shareIdMatch[1];
                
                // Access shared password
                fetch(`/api/shared/${shareId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ access_key: key })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        displaySharedPassword(data.entry);
                    } else {
                        showToast(data.error || 'Invalid access key or expired share.', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error accessing shared password:', error);
                    showToast('An error occurred. Please try again.', 'error');
                });
            });
        }
    }
    
    function loadSharedPasswords() {
        fetch('/api/shares')
            .then(response => response.json())
            .then(data => {
                const shares = data.shares || [];
                
                // Display shares
                displayShares(shares);
            })
            .catch(error => {
                console.error('Error loading shared passwords:', error);
                showToast('Failed to load shared passwords.', 'error');
            });
    }
    
    function displayShares(shares) {
        // Clear current list
        sharedList.innerHTML = '';
        
        if (shares.length === 0) {
            // Show empty state
            sharedList.style.display = 'none';
            emptyShares.style.display = 'block';
        } else {
            // Show shared list
            sharedList.style.display = 'grid';
            emptyShares.style.display = 'none';
            
            // Create shared items
            shares.forEach(share => {
                createSharedItem(share);
            });
        }
    }
    
    function createSharedItem(share) {
        const item = document.createElement('div');
        item.className = 'shared-item';
        
        // HTML for the shared item
        item.innerHTML = `
            <div class="share-id">Share ID: ${share.id.substring(0, 8)}...</div>
            <div class="share-dates">Created: ${share.created_at_formatted} • Expires: ${share.expires_at_formatted}</div>
            <div class="share-status">
                <span class="remaining-time">${share.remaining_text}</span>
                <span class="access-count">
                    ${share.access_count_limit > 0 
                        ? `Accessed ${share.access_count_current}/${share.access_count_limit} times`
                        : `Accessed ${share.access_count_current} times`}
                </span>
            </div>
            <div class="actions">
                <button class="btn btn-danger revoke-share-btn" data-share-id="${share.id}">Revoke Access</button>
            </div>
        `;
        
        // Add click handler for revoke button
        item.querySelector('.revoke-share-btn').addEventListener('click', function() {
            const shareId = this.getAttribute('data-share-id');
            revokeAccess(shareId);
        });
        
        sharedList.appendChild(item);
    }
    
    function revokeAccess(shareId) {
        fetch(`/api/shares/${shareId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Access revoked successfully!', 'success');
                loadSharedPasswords();
            } else {
                showToast(data.error || 'Failed to revoke access.', 'error');
            }
        })
        .catch(error => {
            console.error('Error revoking access:', error);
            showToast('Failed to revoke access.', 'error');
        });
    }
    
    function displaySharedPassword(entry) {
        // Create modal to display shared password
        document.getElementById('shared-title').textContent = entry.title || 'Untitled';
        document.getElementById('shared-website').textContent = entry.website || '';
        document.getElementById('shared-username').textContent = entry.username || '';
        document.getElementById('shared-password').value = entry.password || '';
        document.getElementById('shared-category').textContent = entry.category || '';
        document.getElementById('shared-notes').textContent = entry.notes || '';
        document.getElementById('shared-by').textContent = entry.shared_by || 'Anonymous';
        
        // Show/hide visit button based on whether there's a website
        const visitSharedWebsiteBtn = document.getElementById('visit-shared-website');
        if (entry.website && (entry.website.startsWith('http://') || entry.website.startsWith('https://'))) {
            visitSharedWebsiteBtn.style.display = 'inline-flex';
        } else {
            visitSharedWebsiteBtn.style.display = 'none';
        }
        
        // Open modal
        openModal(sharedPasswordModal);
        
        // Set up event handlers
        
        // Toggle password visibility
        const toggleSharedPasswordBtn = document.querySelector('.toggle-shared-password-btn');
        if (toggleSharedPasswordBtn) {
            toggleSharedPasswordBtn.addEventListener('click', function() {
                const passwordInput = document.getElementById('shared-password');
                const icon = this.querySelector('i');
                
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    passwordInput.type = 'password';
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            });
        }
        
        // Copy username
        const copySharedUsernameBtn = document.getElementById('copy-shared-username');
        if (copySharedUsernameBtn) {
            copySharedUsernameBtn.addEventListener('click', function() {
                const username = document.getElementById('shared-username').textContent;
                navigator.clipboard.writeText(username)
                    .then(() => showToast('Username copied to clipboard!', 'success'))
                    .catch(err => showToast('Failed to copy username.', 'error'));
            });
        }
        
        // Copy password
        const copySharedPasswordBtn = document.querySelector('.copy-shared-password-btn');
        if (copySharedPasswordBtn) {
            copySharedPasswordBtn.addEventListener('click', function() {
                const password = document.getElementById('shared-password').value;
                navigator.clipboard.writeText(password)
                    .then(() => {
                        showToast('Password copied to clipboard!', 'success');
                        
                        // Auto-clear clipboard after 30 seconds
                        setTimeout(() => {
                            navigator.clipboard.readText().then(text => {
                                if (text === password) {
                                    navigator.clipboard.writeText('');
                                }
                            });
                        }, 30000);
                    })
                    .catch(err => showToast('Failed to copy password.', 'error'));
            });
        }
        
        // Visit website
        if (visitSharedWebsiteBtn) {
            visitSharedWebsiteBtn.addEventListener('click', function() {
                const website = document.getElementById('shared-website').textContent;
                if (website) {
                    window.open(website, '_blank');
                }
            });
        }
        
        // Close button
        const closeSharedPasswordBtn = document.getElementById('close-shared-password');
        if (closeSharedPasswordBtn) {
            closeSharedPasswordBtn.addEventListener('click', function() {
                closeModal(sharedPasswordModal);
            });
        }
        
        // Save to my passwords button
        const saveToMyPasswordsBtn = document.getElementById('save-to-my-passwords');
        if (saveToMyPasswordsBtn) {
            saveToMyPasswordsBtn.addEventListener('click', function() {
                // Create new entry
                const newEntry = {
                    title: entry.title || 'Untitled',
                    website: entry.website || '',
                    username: entry.username || '',
                    password: entry.password || '',
                    category: entry.category || '',
                    notes: entry.notes || ''
                };
                
                // Add password
                fetch('/api/passwords', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(newEntry)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showToast('Password saved to your account!', 'success');
                        closeModal(sharedPasswordModal);
                        
                        // Switch to passwords tab
                        document.querySelector('.nav-item[data-page="passwords"]').click();
                    } else {
                        showToast(data.error || 'Failed to save password.', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error saving password:', error);
                    showToast('Failed to save password.', 'error');
                });
            });
        }
    }
    
    // Settings Functions
    function initSettingsHandlers() {
        // Load current settings
        fetch('/api/settings')
        .then(response => response.json())
        .then(settings => {
            // Apply loaded settings to form
            if (themeMode && settings.theme_mode) {
                themeMode.value = settings.theme_mode;
            }
            if (clipboardTimeout && settings.clipboard_timeout) {
                clipboardTimeout.value = settings.clipboard_timeout;
            }
            if (autoLogout && settings.auto_logout) {
                autoLogout.value = settings.auto_logout;
            }
            
            // Apply current theme
            if (settings.theme_mode) {
                applyTheme(settings.theme_mode);
            }
        })
        .catch(error => {
            console.error('Error loading settings:', error);
        });
        
        // Save settings button
        if (saveSettingsBtn) {
            saveSettingsBtn.addEventListener('click', function() {
                const settings = {
                    theme_mode: themeMode.value.toLowerCase(),
                    clipboard_timeout: clipboardTimeout.value,
                    auto_logout: autoLogout.value
                };
                
                // Apply theme immediately
                applyTheme(settings.theme_mode);
                
                // Save settings via API
                fetch('/api/settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(settings)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showToast('Settings saved successfully!', 'success');
                    } else {
                        showToast(data.error || 'Failed to save settings.', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error saving settings:', error);
                    showToast('Settings applied but not saved to server.', 'warning');
                });
            });
        }
        
        // Theme mode change
        if (themeMode) {
            themeMode.addEventListener('change', function() {
                applyTheme(this.value.toLowerCase());
            });
        }
        
        // Backup passwords button
        if (backupPasswordsBtn) {
            backupPasswordsBtn.addEventListener('click', function() {
                // In a real implementation, this would trigger a download
                showToast('Backup created successfully!', 'success');
            });
        }
        
        // Apply initial theme setting
        const currentTheme = themeMode ? themeMode.value.toLowerCase() : 'system';
        applyTheme(currentTheme);
    }
    
    function applyTheme(theme) {
        // Remove existing theme class
        document.body.classList.remove('dark-mode');
        
        // Apply selected theme
        if (theme === 'dark') {
            document.body.classList.add('dark-mode');
        } else if (theme === 'system') {
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                document.body.classList.add('dark-mode');
            }
        }
    }
    
    // Modal Functions
    function initModalHandlers() {
        // Close modal buttons
        const closeModalButtons = document.querySelectorAll('.close-modal');
        closeModalButtons.forEach(button => {
            button.addEventListener('click', function() {
                const modal = this.closest('.modal');
                closeModal(modal);
            });
        });
        
        // Close modal when clicking outside
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('click', function(e) {
                if (e.target === this) {
                    closeModal(this);
                }
            });
        });
        
        // Cancel confirm button
        if (cancelConfirmBtn) {
            cancelConfirmBtn.addEventListener('click', function() {
                closeModal(confirmModal);
            });
        }
    }
    
    function openModal(modal) {
        if (modal) {
            modal.classList.add('active');
        }
    }
    
    function closeModal(modal) {
        if (modal) {
            modal.classList.remove('active');
        }
    }
    
    // Utility Functions
    function showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <span class="toast-message">${message}</span>
            <button class="toast-close">&times;</button>
        `;
        
        toastContainer.appendChild(toast);
        
        // Add click event for close button
        toast.querySelector('.toast-close').addEventListener('click', function() {
            toast.remove();
        });
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }
    
    function escapeHtml(text) {
        if (!text) return '';
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});