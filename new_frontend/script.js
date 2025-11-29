document.addEventListener('DOMContentLoaded', function() {
    // Initialize date picker with tomorrow's date as default
    const dateInput = document.querySelector('input[type="date"]');
    if (dateInput) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        const formattedDate = tomorrow.toISOString().split('T')[0];
        dateInput.value = formattedDate;
        dateInput.min = formattedDate;
    }

    // Toggle mobile menu (new header)
    const mobileMenuBtn = document.querySelector('custom-navbar')?.shadowRoot?.getElementById('mobileMenuBtn');
    const mobileNav = document.querySelector('custom-navbar')?.shadowRoot?.getElementById('mobileNav');
    if (mobileMenuBtn && mobileNav) {
        mobileMenuBtn.addEventListener('click', () => {
            const isOpen = mobileNav.classList.toggle('open');
            mobileMenuBtn.setAttribute('aria-expanded', String(isOpen));
            mobileNav.setAttribute('aria-hidden', String(!isOpen));
        });
    }

    // Open auth modal from header
    const openAuth = document.querySelector('custom-navbar')?.shadowRoot?.getElementById('openAuth');
    const openAuthMobile = document.querySelector('custom-navbar')?.shadowRoot?.getElementById('openAuthMobile');
    const authModal = document.getElementById('authModal');
    if (openAuth) openAuth.addEventListener('click', () => { authModal.hidden = false; authModal.setAttribute('aria-hidden','false'); });
    if (openAuthMobile) openAuthMobile.addEventListener('click', () => { authModal.hidden = false; authModal.setAttribute('aria-hidden','false'); });
    const closeAuth = document.getElementById('closeAuth');
    if (closeAuth) closeAuth.addEventListener('click', () => { authModal.hidden = true; authModal.setAttribute('aria-hidden','true'); });

    // Dark mode toggle
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            document.documentElement.classList.toggle('dark');
            localStorage.setItem('darkMode', document.documentElement.classList.contains('dark'));
        });
    }

    // Check for saved dark mode preference
    if (localStorage.getItem('darkMode') === 'false') {
        document.documentElement.classList.remove('dark');
    }

    // Station autocomplete functionality with dropdown UI
    const stationInputs = document.querySelectorAll('input[placeholder*="station"]');
    stationInputs.forEach(input => {
        const dropdown = document.createElement('div');
        dropdown.className = 'autocomplete';
        input.parentElement.appendChild(dropdown);

        input.addEventListener('input', debounce(async function(e) {
            const query = e.target.value.trim();
            if (query.length < 2) { dropdown.innerHTML = ''; return; }
            try {
                const response = await fetch(`http://localhost:5001/api/stations?search=${encodeURIComponent(query)}`);
                const stations = await response.json();
                dropdown.innerHTML = stations.slice(0, 8).map(s => `
                    <div class="autocomplete__item" data-code="${s.code}" data-name="${s.name}">
                        ${s.name} <span style="color:#9fb3c8">(${s.code})</span>
                    </div>
                `).join('');
            } catch (error) {
                dropdown.innerHTML = '';
                console.error('Error fetching stations:', error);
            }
        }, 300));

        dropdown.addEventListener('click', (ev) => {
            const item = ev.target.closest('.autocomplete__item');
            if (!item) return;
            input.value = `${item.dataset.name}`;
            dropdown.innerHTML = '';
        });

        document.addEventListener('click', (ev) => {
            if (!input.contains(ev.target) && !dropdown.contains(ev.target)) {
                dropdown.innerHTML = '';
            }
        });
    });

    // Debounce function for search inputs
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    // Form submission for search
    // Basic submission handler for search widget
    const searchWidget = document.querySelector('.search-widget');
    if (searchWidget) {
        searchWidget.addEventListener('submit', function(e) {
            e.preventDefault();
        });
        const searchBtn = searchWidget.querySelector('.btn--primary');
        if (searchBtn) {
            searchBtn.addEventListener('click', async () => {
                const fromStation = document.querySelector('input[placeholder="Departure station"]').value;
                const toStation = document.querySelector('input[placeholder="Arrival station"]').value;
                const date = document.querySelector('input[type="date"]').value;
                if (!fromStation || !toStation || !date) { showToast('Please fill all fields', 'error'); return; }
                await runSearch(fromStation, toStation, date);
            });
        }

        // Edit search button
        const editBtn = document.getElementById('editSearchBtn');
        if (editBtn) {
            editBtn.addEventListener('click', () => {
                document.getElementById('resultsSection').hidden = true;
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }
    }

    // Auth: login/register forms
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const switchToRegister = document.getElementById('switchToRegister');
    const switchToLogin = document.getElementById('switchToLogin');
    if (switchToRegister) switchToRegister.onclick = () => { loginForm.hidden = true; registerForm.hidden = false; };
    if (switchToLogin) switchToLogin.onclick = () => { registerForm.hidden = true; loginForm.hidden = false; };

    if (loginForm) loginForm.onsubmit = async (e) => {
        e.preventDefault();
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;
        try {
            const res = await fetch('http://localhost:5001/api/auth/login', {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username, password })
            });
            if (!res.ok) throw new Error('Login failed');
            const data = await res.json();
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            authModal.hidden = true;
            authModal.setAttribute('aria-hidden','true');
            showToast('Signed in successfully', 'success');
        } catch (e) { console.error(e); showToast('Login failed', 'error'); }
    };

    if (registerForm) registerForm.onsubmit = async (e) => {
        e.preventDefault();
        const payload = {
            email: document.getElementById('regEmail').value,
            username: document.getElementById('regUsername').value,
            password: document.getElementById('regPassword').value,
            full_name: document.getElementById('regFullName').value,
            phone: document.getElementById('regPhone').value
        };
        try {
            const res = await fetch('http://localhost:5001/api/auth/register', {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
            });
            if (!res.ok) throw new Error('Register failed');
            const data = await res.json();
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            authModal.hidden = true;
            authModal.setAttribute('aria-hidden','true');
            showToast('Account created and signed in', 'success');
        } catch (e) { console.error(e); showToast('Register failed', 'error'); }
    };
});

// Toast notification function
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    const colors = {
        success: 'bg-emerald-600',
        error: 'bg-red-600',
        info: 'bg-cyan-600'
    };
    
    toast.className = `fixed top-4 right-4 ${colors[type]} text-white px-4 py-2 rounded-lg shadow-lg flex items-center fade-in`;
    toast.innerHTML = `
        <i data-feather="${type === 'success' ? 'check-circle' : type === 'error' ? 'alert-circle' : 'info'}" class="mr-2"></i>
        ${message}
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('opacity-0', 'transition-opacity', 'duration-300');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Run search against backend and render results
async function runSearch(fromStation, toStation, date) {
    try {
        const url = new URL('http://localhost:5001/api/search/trains');
        url.searchParams.set('from_station', fromStation);
        url.searchParams.set('to_station', toStation);
        url.searchParams.set('date', date);
        const sort = document.getElementById('sortBy')?.value || 'price';
        url.searchParams.set('sort_by', sort);
        const res = await fetch(url.toString());
        if (!res.ok) throw new Error('Search failed');
        const data = await res.json();
        renderResults({ fromStation, toStation, date }, data);
    } catch (e) {
        console.error(e);
        showToast('Failed to fetch trains', 'error');
    }
}

function renderResults(meta, results) {
    const section = document.getElementById('resultsSection');
    const route = document.getElementById('resultsRoute');
    const date = document.getElementById('resultsDate');
    const list = document.getElementById('resultsList');
    route.textContent = `${meta.fromStation} → ${meta.toStation}`;
    date.textContent = new Date(meta.date).toDateString();
    // Filter by class chip
    const activeClass = document.querySelector('.chip.active')?.dataset.class;
    let filtered = Array.isArray(results) ? results.slice() : [];
    if (activeClass) {
        filtered = filtered.filter(r => {
            if (activeClass === 'economy') return r.base_fare != null;
            if (activeClass === 'ac') return r.ac_fare != null;
            if (activeClass === 'sleeper') return r.sleeper_fare != null;
            return true;
        });
    }

    list.innerHTML = filtered.map(r => {
        const prices = [
            { label: 'Economy', value: r.base_fare },
            { label: 'AC', value: r.ac_fare },
            { label: 'Sleeper', value: r.sleeper_fare },
        ]
        .filter(p => p.value != null)
        .map(p => `<div class="price"><strong>${p.label}</strong> Rs. ${Number(p.value).toLocaleString()}</div>`)
        .join('');

        return `
        <div class="card">
            <div>
                <div class="card__title">${r.train?.name || 'Train'} (${r.train?.train_number || ''})</div>
                <div class="status">${r.status || 'scheduled'} • ${r.distance_km ?? ''} km</div>
            </div>
            <div>
                <div class="card__times">${fmtTime(r.departure_time)} → ${fmtTime(r.arrival_time)}</div>
                <div class="status">${r.duration_minutes} min • Seats: ${r.available_seats}</div>
            </div>
            <div>
                <div class="card__prices">${prices}</div>
                <button class="btn btn--primary" data-schedule='${JSON.stringify(simpleSchedule(r))}' onclick="openBooking(this)">Select</button>
            </div>
        </div>`;
    }).join('');
    section.hidden = false;
    section.scrollIntoView({ behavior: 'smooth' });

    // Setup filters
    const sortSelect = document.getElementById('sortBy');
    if (sortSelect) {
        sortSelect.onchange = () => runSearch(meta.fromStation, meta.toStation, meta.date);
    }
    document.querySelectorAll('.chip').forEach(ch => {
        ch.onclick = () => {
            document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
            ch.classList.add('active');
            renderResults(meta, results);
        };
    });
}

function fmtTime(iso) {
    try { return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); } catch { return iso; }
}

function simpleSchedule(r) {
    return {
        id: r.id,
        train: r.train?.name,
        train_number: r.train?.train_number,
        departure_time: r.departure_time,
        arrival_time: r.arrival_time,
        departure_station: r.departure_station?.name,
        arrival_station: r.arrival_station?.name,
        fares: { base_fare: r.base_fare, ac_fare: r.ac_fare, sleeper_fare: r.sleeper_fare }
    };
}

window.openBooking = function(btn) {
    try {
        const schedule = JSON.parse(btn.getAttribute('data-schedule'));
        const modal = document.getElementById('bookingModal');
        const summary = document.getElementById('bookingSummary');
        const title = document.getElementById('bookingTitle');
        title.textContent = `Book ${schedule.train || 'Train'} (${schedule.train_number || ''})`;
        summary.innerHTML = `
            <div><strong>Route:</strong> ${schedule.departure_station} → ${schedule.arrival_station}</div>
            <div><strong>Time:</strong> ${fmtTime(schedule.departure_time)} → ${fmtTime(schedule.arrival_time)}</div>
            <div><strong>Fares:</strong> Economy Rs. ${Number(schedule.fares.base_fare||0)} • AC Rs. ${Number(schedule.fares.ac_fare||0)} • Sleeper Rs. ${Number(schedule.fares.sleeper_fare||0)}</div>
        `;
        modal.hidden = false;
        modal.setAttribute('aria-hidden', 'false');
        modal.dataset.scheduleId = schedule.id;
        document.getElementById('journeyDate').value = document.querySelector('input[type="date"]').value;
        // Close handlers
        document.getElementById('closeBooking').onclick = closeBooking;
        document.getElementById('cancelBooking').onclick = closeBooking;
        // Submit handler
        const form = document.getElementById('bookingForm');
        form.onsubmit = async (e) => {
            e.preventDefault();
            await submitBooking(schedule.id);
        };
    } catch (e) {
        console.error(e);
        showToast('Unable to open booking', 'error');
    }
}

function closeBooking() {
    const modal = document.getElementById('bookingModal');
    modal.hidden = true;
    modal.setAttribute('aria-hidden', 'true');
}

async function submitBooking(scheduleId) {
    const token = localStorage.getItem('access_token');
    if (!token) { showToast('Please sign in to book', 'error'); return; }
    const payload = {
        schedule_id: scheduleId,
        passenger_name: document.getElementById('passengerName').value,
        passenger_age: Number(document.getElementById('passengerAge').value),
        passenger_gender: document.getElementById('passengerGender').value,
        seat_class: document.getElementById('seatClass').value,
        seat_number: document.getElementById('seatNumber').value,
        journey_date: document.getElementById('journeyDate').value
    };
    // Basic validation
    if (!payload.passenger_name || !payload.seat_number) { showToast('Missing passenger details', 'error'); return; }
    try {
        const res = await fetch('http://localhost:5001/api/bookings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error('Booking failed');
        const data = await res.json();
        closeBooking();
        showToast(`Booked! Ref ${data.booking?.booking_reference || ''}`,'success');
        // Show confirmation panel
        showConfirmation(data.booking);
        // Optional: open payment step
        // await processPayment(data.booking.id, data.booking.total_amount);
    } catch (e) {
        console.error(e);
        showToast('Booking failed', 'error');
    }
}

function showConfirmation(booking) {
    const section = document.getElementById('resultsSection');
    const list = document.getElementById('resultsList');
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
        <div>
            <div class="card__title">Booking Confirmed</div>
            <div class="status">Ref: ${booking.booking_reference}</div>
        </div>
        <div>
            <div class="card__times">Seat ${booking.seat_number} • Class ${booking.seat_class.toUpperCase()}</div>
            <div class="status">Status: ${booking.status} • Amount: Rs. ${Number(booking.total_amount).toLocaleString()}</div>
        </div>
        <div>
            <button class="btn btn--primary" onclick="showToast('Ticket download coming soon','info')">Download Ticket</button>
        </div>
    `;
    list.prepend(card);
    section.scrollIntoView({ behavior: 'smooth' });
}

async function processPayment(bookingId, amount) {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    try {
        const res = await fetch('http://localhost:5001/api/payments/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ booking_id: bookingId, payment_method: 'credit_card', amount })
        });
        if (!res.ok) throw new Error('Payment failed');
        const data = await res.json();
        showToast('Payment completed','success');
    } catch (e) {
        console.error(e);
        showToast('Payment failed','error');
    }
}