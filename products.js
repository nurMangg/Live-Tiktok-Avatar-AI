// Product Management Module for TikTok Live Shopping

class ProductManager {
    constructor(app) {
        this.app = app;
        this.products = [];
        this.currentProduct = null;
        this.flashSaleTimers = new Map();
        this.salesStats = {
            orders: 0,
            revenue: 0
        };
        
        this.scriptTemplates = {
            opening: "Halo semuanya! Selamat datang di live shopping hari ini! Hari ini kita ada produk-produk menarik dengan harga spesial khusus live shopping. Jangan sampai kehabisan ya!",
            product_intro: "Okay, sekarang aku mau introduce produk yang luar biasa ini. {productName}. Produk ini tuh cocok banget untuk kamu yang {benefit}.",
            benefits: "Keunggulan dari {productName} ini adalah: kualitas premium, hasil maksimal, dan yang penting harga sangat terjangkau! Sudah ribuan customer puas dengan produk ini.",
            price: "Harga normalnya {normalPrice}, tapi khusus live hari ini, kalian bisa dapetin dengan harga cuma {promoPrice}! Hemat banget kan! Diskon sampai {discount}%!",
            testimonial: "Banyak banget customer yang sudah buktiin sendiri hasilnya. Review-nya 5 bintang semua! Mereka bilang produk ini benar-benar worth it dan hasil terlihat cepat.",
            closing: "Jadi tunggu apa lagi? Langsung klik link di bawah ya untuk checkout! Stok terbatas loh, siapa cepat dia dapat! Jangan sampai nyesel nanti kehabisan!",
            promo: "FLASH SALE DIMULAI! Dalam {duration} menit ke depan, harga special banget! Buruan checkout sebelum waktunya habis! Limited stock!"
        };
        
        this.init();
    }
    
    init() {
        // Product Modal Events
        document.getElementById('addProduct').addEventListener('click', () => {
            this.openProductModal();
        });
        
        document.getElementById('productForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addProduct();
        });
        
        // Flash Sale Toggle
        document.getElementById('flashSale').addEventListener('change', (e) => {
            document.getElementById('flashSaleTime').style.display = 
                e.target.checked ? 'block' : 'none';
        });
        
        // Script Template Selection
        document.getElementById('scriptTemplate').addEventListener('change', (e) => {
            this.loadScriptTemplate(e.target.value);
        });
        
        // Product Image Preview
        document.getElementById('productImage').addEventListener('change', (e) => {
            this.previewImage(e.target.files[0]);
        });
        
        // Auto Product Pitch
        document.getElementById('autoProductPitch').addEventListener('change', (e) => {
            if (e.target.checked) {
                this.startAutoPitch();
            } else {
                this.stopAutoPitch();
            }
        });
    }
    
    openProductModal() {
        document.getElementById('productModal').classList.add('active');
        // Reset form
        document.getElementById('productForm').reset();
        document.getElementById('imagePreview').innerHTML = '';
    }
    
    previewImage(file) {
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                document.getElementById('imagePreview').innerHTML = 
                    `<img src="${e.target.result}" alt="Preview">`;
            };
            reader.readAsDataURL(file);
        }
    }
    
    async addProduct() {
        const name = document.getElementById('productName').value;
        const price = document.getElementById('productPrice').value || 0;
        const promoPrice = document.getElementById('productPromoPrice').value;
        const stock = document.getElementById('productStock').value;
        const category = document.getElementById('productCategory').value;
        const description = document.getElementById('productDescription').value;
        const isFlashSale = document.getElementById('flashSale').checked;
        const saleDuration = document.getElementById('saleDuration').value || 10;
        
        // Get image
        const imageFile = document.getElementById('productImage').files[0];
        let imageUrl = '';
        
        if (imageFile) {
            const reader = new FileReader();
            reader.onload = (e) => {
                imageUrl = e.target.result;
                
                const product = {
                    id: Date.now(),
                    name,
                    price: parseFloat(price),
                    promoPrice: parseFloat(promoPrice),
                    stock: parseInt(stock),
                    category,
                    description,
                    imageUrl,
                    isFlashSale,
                    saleDuration: parseInt(saleDuration),
                    sold: 0,
                    createdAt: Date.now()
                };
                
                this.products.push(product);
                this.renderProducts();
                this.closeModal('productModal');
                this.app.showNotification(`Produk "${name}" berhasil ditambahkan!`, 'success');
                
                // Send to server
                this.app.socket.emit('product_added', product);
            };
            reader.readAsDataURL(imageFile);
        }
    }
    
    renderProducts() {
        const showcase = document.getElementById('productShowcase');
        
        if (this.products.length === 0) {
            showcase.innerHTML = '<div class="product-empty">Tambah produk untuk ditampilkan</div>';
            return;
        }
        
        showcase.innerHTML = this.products.map(product => {
            const discount = product.price > 0 
                ? Math.round((1 - product.promoPrice / product.price) * 100) 
                : 0;
            const stockClass = product.stock < 10 ? 'low' : '';
            
            return `
                <div class="product-item" data-id="${product.id}" onclick="productManager.showProduct(${product.id})">
                    <img src="${product.imageUrl}" alt="${product.name}">
                    <div class="product-item-info">
                        <div class="product-item-name">${product.name}</div>
                        <div class="product-item-price">
                            ${product.price > 0 ? `<span class="old">Rp ${this.formatPrice(product.price)}</span>` : ''}
                            <span class="new">Rp ${this.formatPrice(product.promoPrice)}</span>
                            ${discount > 0 ? `<span class="discount">${discount}%</span>` : ''}
                        </div>
                        <div class="product-item-stock ${stockClass}">
                            Stok: ${product.stock} | Terjual: ${product.sold}
                        </div>
                    </div>
                    <div class="product-item-actions">
                        <button onclick="event.stopPropagation(); productManager.showProduct(${product.id})" title="Tampilkan">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button onclick="event.stopPropagation(); productManager.pitchProduct(${product.id})" title="Pitch">
                            <i class="fas fa-bullhorn"></i>
                        </button>
                        <button onclick="event.stopPropagation(); productManager.deleteProduct(${product.id})" title="Hapus">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    showProduct(productId) {
        const product = this.products.find(p => p.id === productId);
        if (!product) return;
        
        this.currentProduct = product;
        
        // Show on video overlay
        const overlay = document.getElementById('productOverlay');
        document.getElementById('overlayProductImage').src = product.imageUrl;
        document.getElementById('overlayProductName').textContent = product.name;
        
        if (product.price > 0) {
            document.getElementById('overlayOldPrice').textContent = `Rp ${this.formatPrice(product.price)}`;
            document.getElementById('overlayOldPrice').style.display = 'inline';
            const discount = Math.round((1 - product.promoPrice / product.price) * 100);
            document.getElementById('overlayDiscount').textContent = `-${discount}%`;
            document.getElementById('overlayDiscount').style.display = 'inline';
        } else {
            document.getElementById('overlayOldPrice').style.display = 'none';
            document.getElementById('overlayDiscount').style.display = 'none';
        }
        
        document.getElementById('overlayNewPrice').textContent = `Rp ${this.formatPrice(product.promoPrice)}`;
        document.getElementById('overlayStock').textContent = product.stock;
        
        // Flash sale timer
        if (product.isFlashSale && !this.flashSaleTimers.has(productId)) {
            this.startFlashSaleTimer(product);
        }
        
        overlay.style.display = 'block';
        
        // Auto hide after 15 seconds
        setTimeout(() => {
            overlay.style.display = 'none';
        }, 15000);
        
        this.app.showNotification(`Menampilkan: ${product.name}`, 'info');
    }
    
    startFlashSaleTimer(product) {
        const timerElement = document.getElementById('overlayTimer');
        const displayElement = document.getElementById('timerDisplay');
        timerElement.style.display = 'flex';
        
        let timeLeft = product.saleDuration * 60; // Convert to seconds
        
        const timer = setInterval(() => {
            timeLeft--;
            
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            displayElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            if (timeLeft <= 0) {
                clearInterval(timer);
                this.flashSaleTimers.delete(product.id);
                timerElement.style.display = 'none';
                this.app.showNotification(`Flash sale ${product.name} berakhir!`, 'warning');
            }
        }, 1000);
        
        this.flashSaleTimers.set(product.id, timer);
    }
    
    pitchProduct(productId) {
        const product = this.products.find(p => p.id === productId);
        if (!product) return;
        
        // Show product overlay
        this.showProduct(productId);
        
        // Generate pitch script
        const discount = product.price > 0 
            ? Math.round((1 - product.promoPrice / product.price) * 100) 
            : 0;
        
        const scripts = [
            this.scriptTemplates.product_intro
                .replace('{productName}', product.name)
                .replace('{benefit}', product.description || 'butuh produk berkualitas'),
            this.scriptTemplates.price
                .replace('{normalPrice}', `Rp ${this.formatPrice(product.price)}`)
                .replace('{promoPrice}', `Rp ${this.formatPrice(product.promoPrice)}`)
                .replace('{discount}', discount)
        ];
        
        if (product.isFlashSale) {
            scripts.unshift(
                this.scriptTemplates.promo.replace('{duration}', product.saleDuration)
            );
        }
        
        scripts.push(this.scriptTemplates.closing);
        
        // Add scripts to queue
        scripts.forEach(script => {
            this.app.chatQueue.push({
                id: Date.now() + Math.random(),
                text: script
            });
        });
        
        this.app.updateQueueDisplay();
        this.app.showNotification(`Pitch produk "${product.name}" ditambahkan ke queue`, 'success');
        
        // Auto process if streaming
        if (this.app.isStreaming) {
            this.app.processQueue();
        }
    }
    
    deleteProduct(productId) {
        if (confirm('Hapus produk ini?')) {
            this.products = this.products.filter(p => p.id !== productId);
            this.renderProducts();
            
            // Clear flash sale timer if exists
            if (this.flashSaleTimers.has(productId)) {
                clearInterval(this.flashSaleTimers.get(productId));
                this.flashSaleTimers.delete(productId);
            }
            
            this.app.showNotification('Produk dihapus', 'info');
        }
    }
    
    loadScriptTemplate(templateName) {
        if (!templateName) return;
        
        let script = this.scriptTemplates[templateName];
        
        // Replace placeholders with current product if available
        if (this.currentProduct) {
            const product = this.currentProduct;
            const discount = product.price > 0 
                ? Math.round((1 - product.promoPrice / product.price) * 100) 
                : 0;
            
            script = script
                .replace('{productName}', product.name)
                .replace('{normalPrice}', `Rp ${this.formatPrice(product.price)}`)
                .replace('{promoPrice}', `Rp ${this.formatPrice(product.promoPrice)}`)
                .replace('{discount}', discount)
                .replace('{benefit}', product.description || 'butuh produk berkualitas')
                .replace('{duration}', product.saleDuration || 10);
        }
        
        document.getElementById('scriptInput').value = script;
    }
    
    addOrder(orderData) {
        this.salesStats.orders++;
        this.salesStats.revenue += orderData.amount;
        
        // Update UI
        document.getElementById('ordersCount').textContent = this.salesStats.orders;
        document.getElementById('totalRevenue').textContent = `Rp ${this.formatPrice(this.salesStats.revenue)}`;
        
        // Add to orders list
        const ordersList = document.getElementById('ordersList');
        const emptyMsg = ordersList.querySelector('.orders-empty');
        if (emptyMsg) emptyMsg.remove();
        
        const orderDiv = document.createElement('div');
        orderDiv.className = 'order-item';
        orderDiv.innerHTML = `
            <div class="order-header">
                <span class="customer-name">${orderData.customer}</span>
                <span class="order-time">Baru saja</span>
            </div>
            <div class="product-name">${orderData.product}</div>
            <div class="order-total">Rp ${this.formatPrice(orderData.amount)}</div>
        `;
        
        ordersList.insertBefore(orderDiv, ordersList.firstChild);
        
        // Update product stock
        const product = this.products.find(p => p.name === orderData.product);
        if (product) {
            product.stock -= orderData.quantity;
            product.sold += orderData.quantity;
            this.renderProducts();
        }
        
        // Auto thank if enabled
        if (document.getElementById('autoOrderConfirm').checked) {
            const thankScript = `Terima kasih @${orderData.customer} sudah order ${orderData.product}! Pesanan akan segera diproses. Thank you for shopping! 🛍️`;
            this.app.chatQueue.push({
                id: Date.now(),
                text: thankScript
            });
            this.app.updateQueueDisplay();
        }
        
        this.app.showNotification(`Order baru dari ${orderData.customer}! 🎉`, 'success');
    }
    
    startAutoPitch() {
        this.autoPitchInterval = setInterval(() => {
            if (this.products.length > 0 && this.app.isStreaming) {
                // Pick random product
                const randomProduct = this.products[Math.floor(Math.random() * this.products.length)];
                this.pitchProduct(randomProduct.id);
            }
        }, 5 * 60 * 1000); // Every 5 minutes
    }
    
    stopAutoPitch() {
        if (this.autoPitchInterval) {
            clearInterval(this.autoPitchInterval);
        }
    }
    
    formatPrice(price) {
        return new Intl.NumberFormat('id-ID').format(price);
    }
}

// Helper function for closing modals
function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Will be initialized by main app
let productManager = null;

