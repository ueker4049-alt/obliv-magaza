document.addEventListener('DOMContentLoaded', () => {
    updateCartCount();
    setupCartDrawer();
    setupMobileMenu();
});
function setupCartDrawer() {
    const cartToggles = [
        document.getElementById('cart-toggle-btn'),
        document.getElementById('mobile-cart-btn')
    ].filter(Boolean);
    const cartSidebar = document.getElementById('cart-sidebar');
    const cartOverlay = document.getElementById('cart-overlay');
    const cartClose = document.getElementById('cart-close-btn');

    cartToggles.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            openCart();
        });
    });
    if (cartClose) {
        cartClose.addEventListener('click', closeCart);
    }
    if (cartOverlay) {
        cartOverlay.addEventListener('click', closeCart);
    }
}

function setupMobileMenu() {
    const toggleBtn = document.getElementById('mobile-menu-toggle');
    const closeBtn = document.getElementById('mobile-menu-close');
    const drawer = document.getElementById('mobile-menu-drawer');
    const overlay = document.getElementById('mobile-menu-overlay');
    if (!toggleBtn || !drawer || !overlay) return;

    function openMobileMenu() {
        drawer.classList.add('active');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    function closeMobileMenu() {
        drawer.classList.remove('active');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    toggleBtn.addEventListener('click', (e) => {
        e.preventDefault();
        openMobileMenu();
    });
    closeBtn && closeBtn.addEventListener('click', closeMobileMenu);
    overlay.addEventListener('click', closeMobileMenu);

    // Close when clicking any link inside drawer
    drawer.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', () => {
            closeMobileMenu();
        });
    });
}
function openCart() {
    const cartSidebar = document.getElementById('cart-sidebar');
    const cartOverlay = document.getElementById('cart-overlay');
    if (cartSidebar && cartOverlay) {
        cartSidebar.classList.add('active');
        cartOverlay.classList.add('active');
        renderCartDrawerItems();
    }
}
function closeCart() {
    const cartSidebar = document.getElementById('cart-sidebar');
    const cartOverlay = document.getElementById('cart-overlay');
    if (cartSidebar && cartOverlay) {
        cartSidebar.classList.remove('active');
        cartOverlay.classList.remove('active');
    }
}
function getCart() {
    let data = localStorage.getItem('obliv_cart');
    if (!data) {
        data = localStorage.getItem('OBLIV_cart') || localStorage.getItem('duke_cart') || '[]';
    }
    try {
        return JSON.parse(data);
    } catch(e) {
        return [];
    }
}
function saveCart(cart) {
    localStorage.setItem('obliv_cart', JSON.stringify(cart));
    localStorage.setItem('OBLIV_cart', JSON.stringify(cart));
    updateCartCount();
    renderCartDrawerItems();
}
function addToCart(productId, name, price, color, size, imageUrl) {
    let cart = getCart();
    const existingIndex = cart.findIndex(item => item.id === productId && item.size === size);
    if (existingIndex > -1) {
        cart[existingIndex].quantity += 1;
    } else {
        cart.push({
            id: productId,
            name: name,
            price: parseFloat(price),
            color: color || 'OBLIV Raw',
            size: size || 'M',
            imageUrl: imageUrl || '/static/images/tshirt_black.svg',
            quantity: 1
        });
    }
    saveCart(cart);
    openCart();
}
window.addToCart = addToCart;
window.openCart = openCart;
window.closeCart = closeCart;
window.getCart = getCart;
window.saveCart = saveCart;
window.updateCartCount = updateCartCount;

function removeFromCart(index) {
    let cart = getCart();
    cart.splice(index, 1);
    saveCart(cart);
}
function updateQuantity(index, delta) {
    let cart = getCart();
    if (cart[index]) {
        cart[index].quantity += delta;
        if (cart[index].quantity <= 0) {
            cart.splice(index, 1);
        }
        saveCart(cart);
    }
}
function updateCartCount() {
    const badges = document.querySelectorAll('.cart-count-badge');
    const counters = document.querySelectorAll('.cart-sheet-counter');
    const cart = getCart();
    const totalCount = cart.reduce((sum, item) => sum + item.quantity, 0);
    badges.forEach(badge => {
        badge.textContent = totalCount;
        badge.style.display = totalCount > 0 ? 'flex' : 'none';
    });
    counters.forEach(counter => {
        counter.textContent = totalCount;
    });
}
function renderCartDrawerItems() {
    const container = document.getElementById('cart-items-container');
    const totalElem = document.getElementById('cart-subtotal');
    if (!container) return;
    const cart = getCart();
    if (cart.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 60px 10px; color: var(--text-dim);">
                <div style="margin-bottom: 14px; opacity: 0.35;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="display: inline-block;">
                        <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
                        <line x1="3" y1="6" x2="21" y2="6"></line>
                        <path d="M16 10a4 4 0 0 1-8 0"></path>
                    </svg>
                </div>
                <div style="font-family: var(--font-display); font-weight: 900; font-size: 24px; color: #FFFFFF; text-transform: uppercase; margin-bottom: 6px;">
                    SEPETİNİZ BOŞ
                </div>
                <p style="font-size: 13px; color: var(--text-muted);">Koleksiyondan ürün ekleyerek başlayabilirsiniz.</p>
            </div>
        `;
        if (totalElem) totalElem.textContent = '0.00 ₺';
        updateShippingMeter(0);
        return;
    }
    let total = 0;
    let html = '';
    cart.forEach((item, index) => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        html += `
            <div style="display: flex; gap: 14px; background: #131419; border: 1px solid var(--border-hairline); padding: 14px; border-radius: 12px; align-items: center;">
                <div style="width: 60px; height: 60px; background: #080809; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                    <img src="${item.imageUrl}" alt="${item.name}" style="height: 50px; width: auto; object-fit: contain;">
                </div>
                <div style="flex-grow: 1; min-width: 0;">
                    <div style="font-family: var(--font-display); font-weight: 900; font-size: 18px; text-transform: uppercase; line-height: 1.15; color: #FFFFFF; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        ${item.name}
                    </div>
                    <div style="font-family: var(--font-mono); font-size: 10px; color: var(--text-dim); margin-top: 4px; letter-spacing: 0.08em; text-transform: uppercase;">
                        BEDEN: <span style="color: #FFFFFF; font-weight: 700;">${item.size}</span> | ADET: ${item.quantity}
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                        <div style="display: flex; align-items: center; gap: 6px; background: #0A0A0C; border: 1px solid var(--border-hairline); border-radius: 999px; padding: 2px 8px;">
                            <button onclick="updateQuantity(${index}, -1)" style="background: none; border: none; color: #FFFFFF; cursor: pointer; font-family: var(--font-mono); font-size: 12px; padding: 0 4px;">-</button>
                            <span style="font-family: var(--font-mono); font-size: 11px; font-weight: 700; min-width: 16px; text-align: center;">${item.quantity}</span>
                            <button onclick="updateQuantity(${index}, 1)" style="background: none; border: none; color: #FFFFFF; cursor: pointer; font-family: var(--font-mono); font-size: 12px; padding: 0 4px;">+</button>
                        </div>
                        <div style="font-family: var(--font-mono); font-weight: 800; font-size: 14px; color: var(--electric-blue);">
                            ${Math.round(itemTotal)} ₺
                        </div>
                    </div>
                </div>
                <button onclick="removeFromCart(${index})" title="Kaldır" style="background:none; border:none; color: var(--text-muted); cursor: pointer; font-size: 20px; padding: 0 6px;">&times;</button>
            </div>
        `;
    });
    container.innerHTML = html;
    if (totalElem) {
        totalElem.textContent = `${Math.round(total)} ₺`;
    }
    updateShippingMeter(total);
}

function updateShippingMeter(subtotal) {
    // Ücretsiz kargo ibaresi kullanıcı talebiyle kaldırıldı
    return;
}
function filterCategory(categoryName) {
    const buttons = document.querySelectorAll('.catalog-header button');
    buttons.forEach(btn => {
        if (btn.textContent.trim().toUpperCase() === categoryName.toUpperCase() || (categoryName === 'ALL' && btn.textContent.includes('TÜMÜ'))) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    const products = document.querySelectorAll('.product-grid-item');
    products.forEach(p => {
        if (categoryName === 'ALL' || p.getAttribute('data-category') === categoryName) {
            p.style.display = 'flex';
        } else {
            p.style.display = 'none';
        }
    });
}
document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('live-chat-toggle-btn');
    const closeBtn = document.getElementById('live-chat-close-btn');
    const chatModal = document.getElementById('live-chat-window');
    const chatForm = document.getElementById('live-chat-form');
    const chatInput = document.getElementById('live-chat-input');
    const chatMessages = document.getElementById('live-chat-messages');
    const chips = document.querySelectorAll('.chat-chip-btn');
    if (!toggleBtn || !chatModal) return;
    function openChat() {
        chatModal.style.display = 'flex';
        chatInput && chatInput.focus();
        scrollChatToBottom();
    }
    function closeChat() {
        chatModal.style.display = 'none';
    }
    toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (chatModal.style.display === 'none' || !chatModal.style.display) {
            openChat();
        } else {
            closeChat();
        }
    });
    closeBtn && closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        closeChat();
    });
    function scrollChatToBottom() {
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    function formatCurrentTime() {
        const d = new Date();
        return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
    }
    function appendUserMessage(text) {
        const div = document.createElement('div');
        div.className = 'chat-bubble chat-bubble-user';
        div.innerHTML = `
            <div class="bubble-sender">SİZ</div>
            <div class="bubble-text">${escapeHtml(text)}</div>
            <div class="bubble-time">${formatCurrentTime()}</div>
        `;
        chatMessages.appendChild(div);
        scrollChatToBottom();
    }
    function appendAgentMessage(text) {
        const div = document.createElement('div');
        div.className = 'chat-bubble chat-bubble-agent';
        div.innerHTML = `
            <div class="bubble-sender">UMUT • DESTEK ASİSTANI</div>
            <div class="bubble-text">${escapeHtml(text)}</div>
            <div class="bubble-time">${formatCurrentTime()}</div>
        `;
        chatMessages.appendChild(div);
        scrollChatToBottom();
    }
    function escapeHtml(string) {
        const entityMap = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        };
        return String(string).replace(/[&<>"']/g, s => entityMap[s]);
    }
    async function sendQuestion(text) {
        if (!text || !text.trim()) return;
        const msg = text.trim();
        appendUserMessage(msg);
        // Show typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-bubble chat-bubble-agent typing-indicator-bubble';
        typingDiv.innerHTML = `
            <div class="bubble-sender">UMUT YAZIYOR...</div>
            <div style="font-size: 11px; color: var(--text-dim);">Düşünüyor...</div>
        `;
        chatMessages.appendChild(typingDiv);
        scrollChatToBottom();
        try {
            const res = await fetch('/api/live-chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg })
            });
            const data = await res.json();
            typingDiv.remove();
            appendAgentMessage(data.reply || "Sorunuz için teşekkürler! Ekibimizle oblivwear@gmail.com adresinden de iletişim kurabilirsiniz.");
        } catch (err) {
            typingDiv.remove();
            appendAgentMessage("Bağlantı hatası oluştu. Lütfen tekrar deneyin veya oblivwear@gmail.com adresinden bizimle iletişime geçin.");
        }
    }
    chatForm && chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = chatInput.value;
        if (!text.trim()) return;
        chatInput.value = '';
        sendQuestion(text);
    });
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const question = chip.getAttribute('data-ask');
            if (question) {
                sendQuestion(question);
            }
        });
    });
    const chipsContainer = document.getElementById('live-chat-chips-container');
    const scrollLeftBtn = document.getElementById('chips-scroll-left');
    const scrollRightBtn = document.getElementById('chips-scroll-right');
    if (chipsContainer) {
        scrollLeftBtn && scrollLeftBtn.addEventListener('click', () => {
            chipsContainer.scrollBy({ left: -140, behavior: 'smooth' });
        });
        scrollRightBtn && scrollRightBtn.addEventListener('click', () => {
            chipsContainer.scrollBy({ left: 140, behavior: 'smooth' });
        });
        chipsContainer.addEventListener('wheel', (e) => {
            if (e.deltaY !== 0) {
                e.preventDefault();
                chipsContainer.scrollLeft += e.deltaY;
            }
        });
    }
});

// ==========================================================================
// 8. NEXT DROP GERİ SAYIM SAYACI
// ==========================================================================
(function initNextDropTimer() {
    const timerEl1 = document.getElementById('next-drop-timer');
    const timerEl2 = document.getElementById('next-drop-timer-2');
    if (!timerEl1 && !timerEl2) return;

    // Hedef: 3 gün 14 saat sonrası
    let targetTime = Date.now() + (3 * 24 * 3600 + 14 * 3600 + 22 * 60) * 1000;

    function updateTimer() {
        const diff = Math.max(0, targetTime - Date.now());
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
        const mins = Math.floor((diff / 1000 / 60) % 60);
        const secs = Math.floor((diff / 1000) % 60);

        const pad = (n) => String(n).padStart(2, '0');
        const text = `${pad(days)}G ${pad(hours)}S ${pad(mins)}D ${pad(secs)}S`;
        if (timerEl1) timerEl1.textContent = text;
        if (timerEl2) timerEl2.textContent = text;
    }
    updateTimer();
    setInterval(updateTimer, 1000);
})();

// ==========================================================================
// 9. CANLI TAHMİNLİ ARAMA (INSTANT PREDICTIVE SEARCH)
// ==========================================================================
(function initInstantSearch() {
    const input = document.getElementById('instant-search-input');
    const resultsBox = document.getElementById('instant-search-results');
    if (!input || !resultsBox) return;

    let debounceTimer;
    input.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        const q = this.value.trim();
        if (q.length < 2) {
            resultsBox.style.display = 'none';
            resultsBox.innerHTML = '';
            return;
        }

        debounceTimer = setTimeout(async () => {
            try {
                const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
                const products = await res.json();
                if (products.length === 0) {
                    resultsBox.innerHTML = `<div style="padding: 12px; font-size: 11px; color: var(--text-muted); font-family: var(--font-mono); text-align: center;">Eşleşen ürün bulunamadı.</div>`;
                    resultsBox.style.display = 'block';
                    return;
                }

                resultsBox.innerHTML = products.map(p => `
                    <a href="/product/${p.id}" style="display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 8px; text-decoration: none; color: #FFF; transition: background 0.15s;" onmouseover="this.style.background='rgba(255,255,255,0.06)'" onmouseout="this.style.background='transparent'">
                        <img src="${p.image_url}" alt="${p.name}" style="width: 38px; height: 38px; object-fit: contain; border-radius: 6px; background: #07080B; padding: 2px;">
                        <div style="flex-grow: 1; min-width: 0;">
                            <div style="font-family: var(--font-display); font-size: 14px; font-weight: 800; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${p.name}</div>
                            <div style="font-family: var(--font-mono); font-size: 10px; color: var(--electric-blue); font-weight: 700;">${parseFloat(p.price).toFixed(2)} ₺</div>
                        </div>
                    </a>
                `).join('');
                resultsBox.style.display = 'block';
            } catch (err) {
                console.error(err);
            }
        }, 200);
    });
})();

// Logo single-pass animation controller (plays once on fresh load / navigation, then stays still)
(function() {
    window.addEventListener('pageshow', function() {
        const logoImgs = document.querySelectorAll('.top-brand img, .dock-logo img, .admin-brand img');
        const ts = Date.now();
        logoImgs.forEach(img => {
            if (img && img.src && img.src.includes('obliv_animated.gif')) {
                const base = img.src.split('?')[0];
                img.src = base + '?t=' + ts;
            }
        });
    });
})();


// ==========================================================================
// 10. İSTEK LİSTESİ MODU (WISHLIST / WAITLIST ENGINE)
// ==========================================================================
let globalWishlistSet = new Set();

async function initWishlistStatus() {
    try {
        const res = await fetch('/api/wishlist/status');
        if (res.ok) {
            const data = await res.json();
            const list = data.product_ids || data.wishlist || [];
            if (Array.isArray(list)) {
                globalWishlistSet = new Set(list.map(Number));
                updateAllWishlistButtons();
            }
        }
    } catch (e) {
        console.error('Wishlist status sync error:', e);
    }
}

function updateWishlistButtonVisual(btn, isWishlisted) {
    const icon = btn.querySelector('.wishlist-icon');
    const label = btn.querySelector('.wishlist-btn-label');
    if (isWishlisted) {
        btn.classList.add('wishlisted');
        btn.style.background = '#FFFFFF';
        btn.style.color = '#000000';
        btn.style.borderColor = '#FFFFFF';
        btn.style.boxShadow = '0 0 15px rgba(255, 255, 255, 0.4)';
        if (icon) icon.textContent = '★';
        if (label) label.textContent = 'LİSTEYE EKLENDİ';
    } else {
        btn.classList.remove('wishlisted');
        btn.style.background = '#FFFFFF';
        btn.style.color = '#000000';
        btn.style.borderColor = '#FFFFFF';
        btn.style.boxShadow = '0 4px 14px rgba(255, 255, 255, 0.15)';
        if (icon) icon.textContent = '☆';
        if (label) label.textContent = 'İSTEK LİSTESİ';
    }
}

function updateAllWishlistButtons() {
    document.querySelectorAll('.btn-wishlist-toggle-action').forEach(btn => {
        const pId = parseInt(btn.dataset.id || btn.getAttribute('data-id'), 10);
        if (pId) {
            updateWishlistButtonVisual(btn, globalWishlistSet.has(pId));
        }
    });
}

function showWishlistToast(msg, isAdded) {
    let toast = document.getElementById('obliv-wishlist-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'obliv-wishlist-toast';
        toast.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 99999;
            background: #FFFFFF;
            border: 1px solid rgba(0, 0, 0, 0.1);
            border-radius: 12px;
            padding: 14px 22px;
            color: #000000;
            font-family: var(--font-mono, monospace);
            font-size: 13px;
            font-weight: 800;
            box-shadow: 0 10px 35px rgba(0,0,0,0.4), 0 0 25px rgba(255, 255, 255, 0.5);
            display: flex;
            align-items: center;
            gap: 12px;
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            pointer-events: none;
        `;
        document.body.appendChild(toast);
    }
    toast.style.background = '#FFFFFF';
    toast.style.color = '#000000';
    toast.style.boxShadow = '0 10px 35px rgba(0,0,0,0.4), 0 0 25px rgba(255, 255, 255, 0.5)';
    toast.innerHTML = `
        <span style="font-size: 18px; color: #000000; font-weight: 900;">${isAdded ? '★' : '✓'}</span>
        <span style="color: #000000; font-weight: 800; letter-spacing: 0.02em;">${msg}</span>
    `;
    toast.style.transform = 'translateY(0)';
    toast.style.opacity = '1';

    clearTimeout(toast.hideTimeout);
    toast.hideTimeout = setTimeout(() => {
        toast.style.transform = 'translateY(100px)';
        toast.style.opacity = '0';
    }, 2800);
}

async function toggleWishlist(productId, productName, buttonEl) {
    const pId = parseInt(productId, 10);
    const pName = productName || 'Ürün';
    if (!pId) return;

    // Optimistic UI Update (Anında 0 milisaniyede görsel tepki)
    const wasInWishlist = globalWishlistSet.has(pId);
    if (wasInWishlist) {
        globalWishlistSet.delete(pId);
        showWishlistToast(`${pName} istek listenizden çıkarıldı.`, false);
    } else {
        globalWishlistSet.add(pId);
        showWishlistToast(`${pName} istek listenize eklendi!`, true);
    }
    updateAllWishlistButtons();

    try {
        const res = await fetch('/api/wishlist/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: pId })
        });
        const result = await res.json();
        if (!result.success) {
            // Rollback if server errored
            if (wasInWishlist) globalWishlistSet.add(pId);
            else globalWishlistSet.delete(pId);
            updateAllWishlistButtons();
            alert(result.error || 'Bir hata oluştu.');
        }
    } catch (err) {
        console.error('Wishlist toggle error:', err);
        // Rollback on network failure
        if (wasInWishlist) globalWishlistSet.add(pId);
        else globalWishlistSet.delete(pId);
        updateAllWishlistButtons();
    }
}
window.toggleWishlist = toggleWishlist;

// Global Delegated Handler
document.addEventListener('click', function(e) {
    const wishBtn = e.target.closest('.btn-wishlist-toggle-action');
    if (wishBtn) {
        e.preventDefault();
        e.stopPropagation();
        toggleWishlist(wishBtn.dataset.id, wishBtn.dataset.name, wishBtn);
        return;
    }

    const cartBtn = e.target.closest('.btn-add-cart-action');
    if (cartBtn) {
        e.preventDefault();
        e.stopPropagation();
        const id = parseInt(cartBtn.dataset.id, 10);
        const name = cartBtn.dataset.name || 'OBLIV T-Shirt';
        const price = parseFloat(cartBtn.dataset.price) || 0;
        const color = cartBtn.dataset.color || 'Standart';
        const size = cartBtn.dataset.size || 'M';
        const image = cartBtn.dataset.image || '/static/images/obliv_brand_official.png';
        addToCart(id, name, price, color, size, image);
    }
});

document.addEventListener('DOMContentLoaded', () => {
    initWishlistStatus();
});
