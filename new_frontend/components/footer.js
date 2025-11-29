class CustomFooter extends HTMLElement {
    connectedCallback() {
        this.attachShadow({ mode: 'open' });
        this.shadowRoot.innerHTML = `
            <style>
                .footer-link:hover {
                    color: #06b6d4;
                }
            </style>
            <footer class="bg-gray-800 text-gray-400 py-12">
                <div class="container mx-auto px-4">
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
                        <div>
                            <h3 class="text-white text-lg font-semibold mb-4 flex items-center">
                                <i data-feather="train" class="text-cyan-500 mr-2"></i>
                                PakRail Express
                            </h3>
                            <p class="mb-4">Your trusted partner for train travel across Pakistan.</p>
                            <div class="flex space-x-4">
                                <a href="#" class="text-gray-400 hover:text-cyan-500">
                                    <i data-feather="facebook"></i>
                                </a>
                                <a href="#" class="text-gray-400 hover:text-cyan-500">
                                    <i data-feather="twitter"></i>
                                </a>
                                <a href="#" class="text-gray-400 hover:text-cyan-500">
                                    <i data-feather="instagram"></i>
                                </a>
                            </div>
                        </div>
                        
                        <div>
                            <h4 class="text-white text-lg font-semibold mb-4">Quick Links</h4>
                            <ul class="space-y-2">
                                <li><a href="/" class="footer-link">Home</a></li>
                                <li><a href="/search" class="footer-link">Search Trains</a></li>
                                <li><a href="/bookings" class="footer-link">My Bookings</a></li>
                                <li><a href="/contact" class="footer-link">Contact Us</a></li>
                            </ul>
                        </div>
                        
                        <div>
                            <h4 class="text-white text-lg font-semibold mb-4">Information</h4>
                            <ul class="space-y-2">
                                <li><a href="/about" class="footer-link">About Us</a></li>
                                <li><a href="/faq" class="footer-link">FAQs</a></li>
                                <li><a href="/privacy" class="footer-link">Privacy Policy</a></li>
                                <li><a href="/terms" class="footer-link">Terms & Conditions</a></li>
                            </ul>
                        </div>
                        
                        <div>
                            <h4 class="text-white text-lg font-semibold mb-4">Contact</h4>
                            <ul class="space-y-2">
                                <li class="flex items-center">
                                    <i data-feather="mail" class="w-4 h-4 mr-2"></i>
                                    <a href="mailto:info@pakrailexpress.com" class="footer-link">info@pakrailexpress.com</a>
                                </li>
                                <li class="flex items-center">
                                    <i data-feather="phone" class="w-4 h-4 mr-2"></i>
                                    <a href="tel:+92123456789" class="footer-link">+92 123 456789</a>
                                </li>
                                <li class="flex items-center">
                                    <i data-feather="map-pin" class="w-4 h-4 mr-2"></i>
                                    <span>Karachi, Pakistan</span>
                                </li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="border-t border-gray-700 mt-8 pt-8 text-sm text-center">
                        <p>&copy; ${new Date().getFullYear()} PakRail Express. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        `;
    }
}

customElements.define('custom-footer', CustomFooter);