# Railway Management System - Frontend Developer Guide

## Project Overview
Production-ready railway booking system for Pakistani routes. Backend is complete with REST APIs, MySQL database, and Docker deployment.

## Backend Architecture

### Technology Stack
- **Framework**: Flask 3.0.0 with Gunicorn (4 workers)
- **Database**: MySQL 8.0
- **Authentication**: JWT (Flask-JWT-Extended)
- **ORM**: SQLAlchemy 3.1.1
- **Container**: Docker (accessible at http://localhost:5001)

### Database Schema

#### Core Tables

**stations**
```sql
id: INTEGER (PK)
name: VARCHAR(100) - Station name (e.g., "Karachi Cantonment")
code: VARCHAR(10) - Station code (e.g., "KHI")
city: VARCHAR(100) - City name
```

**trains**
```sql
id: INTEGER (PK)
train_number: VARCHAR(20) - Unique identifier
name: VARCHAR(100) - Train name
train_type: VARCHAR(50) - Type: "Express", "Mail", "Passenger"
total_seats: INTEGER - Total capacity
```

**train_schedule**
```sql
id: INTEGER (PK)
train_id: INTEGER (FK → trains.id)
departure_station_id: INTEGER (FK → stations.id)
arrival_station_id: INTEGER (FK → stations.id)
departure_time: DATETIME
arrival_time: DATETIME
duration_minutes: INTEGER
distance_km: FLOAT
base_fare: DECIMAL(10,2)
ac_fare: DECIMAL(10,2)
sleeper_fare: DECIMAL(10,2)
available_seats: INTEGER
status: VARCHAR(20) - "scheduled", "delayed", "cancelled"
```

**users**
```sql
id: INTEGER (PK)
email: VARCHAR(120) - Unique
username: VARCHAR(80) - Unique
password_hash: VARCHAR(255)
full_name: VARCHAR(100)
phone: VARCHAR(20)
created_at: DATETIME
is_admin: BOOLEAN
```

**bookings**
```sql
id: INTEGER (PK)
user_id: INTEGER (FK → users.id)
schedule_id: INTEGER (FK → train_schedule.id)
booking_reference: VARCHAR(20) - Unique (e.g., "BK20231128001")
passenger_name: VARCHAR(100)
passenger_age: INTEGER
passenger_gender: VARCHAR(10)
seat_number: VARCHAR(10)
seat_class: VARCHAR(20) - "economy", "ac", "sleeper"
total_amount: DECIMAL(10,2)
booking_date: DATETIME
journey_date: DATE
status: VARCHAR(20) - "confirmed", "cancelled", "completed"
payment_status: VARCHAR(20) - "pending", "paid", "refunded"
```

### Seeded Data

**15 Stations** (Pakistani Railway Network):
- Karachi Cantonment (KHI)
- Lahore Junction (LHE)
- Rawalpindi (RWP)
- Faisalabad (FSD)
- Multan Cantonment (MUX)
- Hyderabad Junction (HYD)
- Peshawar Cantonment (PEW)
- Quetta (UET)
- Sukkur (SUK)
- Bahawalpur (BWP)
- Sargodha (SGD)
- Sialkot (SKT)
- Gujranwala (GJW)
- Sahiwal (SWL)
- Mardan (MRD)

**45 Trains** across 8 major routes with realistic pricing

**30,600 Total Seats** (680 seats per train: 300 economy, 250 AC, 130 sleeper)

## REST API Endpoints

### Base URL
```
http://localhost:5001/api
```

### Authentication Endpoints

**POST /api/auth/register**
```json
Request:
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "John Doe",
  "phone": "+92300000000"
}

Response: 201
{
  "message": "User registered successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "full_name": "John Doe"
  }
}
```

**POST /api/auth/login**
```json
Request:
{
  "username": "username",
  "password": "password123"
}

Response: 200
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "full_name": "John Doe",
    "is_admin": false
  }
}
```

**GET /api/auth/profile**
```
Headers: Authorization: Bearer {access_token}

Response: 200
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "John Doe",
  "phone": "+92300000000",
  "is_admin": false
}
```

### Station Endpoints

**GET /api/stations**
```json
Response: 200
[
  {
    "id": 1,
    "name": "Karachi Cantonment",
    "code": "KHI",
    "city": "Karachi"
  },
  ...
]
```

**GET /api/stations/{id}**
```json
Response: 200
{
  "id": 1,
  "name": "Karachi Cantonment",
  "code": "KHI",
  "city": "Karachi"
}
```

### Train Endpoints

**GET /api/trains**
```json
Response: 200
[
  {
    "id": 1,
    "train_number": "1UP",
    "name": "Karachi Express",
    "train_type": "Express",
    "total_seats": 680
  },
  ...
]
```

**GET /api/trains/{id}**
```json
Response: 200
{
  "id": 1,
  "train_number": "1UP",
  "name": "Karachi Express",
  "train_type": "Express",
  "total_seats": 680,
  "schedules": [...]
}
```

### Search Endpoint

**GET /api/search/trains**
```
Query Parameters:
- from_station: string (required) - Station code or city name
- to_station: string (required) - Station code or city name
- date: string (required) - Format: YYYY-MM-DD
- seat_class: string (optional) - "economy", "ac", "sleeper"
- sort_by: string (optional) - "departure_time", "price", "duration"

Example: /api/search/trains?from_station=Karachi&to_station=Lahore&date=2025-12-01

Response: 200
[
  {
    "id": 1,
    "train": {
      "id": 1,
      "train_number": "1UP",
      "name": "Karachi Express",
      "train_type": "Express"
    },
    "departure_station": {
      "name": "Karachi Cantonment",
      "code": "KHI",
      "city": "Karachi"
    },
    "arrival_station": {
      "name": "Lahore Junction",
      "code": "LHE",
      "city": "Lahore"
    },
    "departure_time": "2025-12-01T06:00:00",
    "arrival_time": "2025-12-01T20:30:00",
    "duration_minutes": 870,
    "distance_km": 1214.0,
    "base_fare": 1500.00,
    "ac_fare": 3300.00,
    "sleeper_fare": 5250.00,
    "available_seats": 680,
    "status": "scheduled"
  },
  ...
]
```

### Schedule Endpoints

**GET /api/schedules**
```
Query Parameters (all optional):
- train_id: integer
- departure_station_id: integer
- arrival_station_id: integer
- date: string (YYYY-MM-DD)
- status: string

Response: 200 (same format as search results)
```

**GET /api/schedules/{id}**
```json
Response: 200
{
  "id": 1,
  "train": {...},
  "departure_station": {...},
  "arrival_station": {...},
  "departure_time": "2025-12-01T06:00:00",
  "arrival_time": "2025-12-01T20:30:00",
  "duration_minutes": 870,
  "distance_km": 1214.0,
  "base_fare": 1500.00,
  "ac_fare": 3300.00,
  "sleeper_fare": 5250.00,
  "available_seats": 680,
  "status": "scheduled"
}
```

### Booking Endpoints (JWT Required)

**POST /api/bookings**
```json
Headers: Authorization: Bearer {access_token}

Request:
{
  "schedule_id": 1,
  "passenger_name": "John Doe",
  "passenger_age": 30,
  "passenger_gender": "Male",
  "seat_class": "ac",
  "seat_number": "A1",
  "journey_date": "2025-12-01"
}

Response: 201
{
  "message": "Booking created successfully",
  "booking": {
    "id": 1,
    "booking_reference": "BK20251128001",
    "passenger_name": "John Doe",
    "seat_number": "A1",
    "seat_class": "ac",
    "total_amount": 3300.00,
    "status": "confirmed",
    "payment_status": "pending",
    "schedule": {...}
  }
}
```

**GET /api/bookings**
```
Headers: Authorization: Bearer {access_token}

Response: 200
[
  {
    "id": 1,
    "booking_reference": "BK20251128001",
    "passenger_name": "John Doe",
    "total_amount": 3300.00,
    "status": "confirmed",
    "schedule": {...}
  },
  ...
]
```

**GET /api/bookings/{id}**
```
Headers: Authorization: Bearer {access_token}

Response: 200 (detailed booking object)
```

**DELETE /api/bookings/{id}**
```
Headers: Authorization: Bearer {access_token}

Response: 200
{
  "message": "Booking cancelled successfully"
}
```

### Payment Endpoints (JWT Required)

**POST /api/payments/process**
```json
Headers: Authorization: Bearer {access_token}

Request:
{
  "booking_id": 1,
  "payment_method": "credit_card",
  "amount": 3300.00
}

Response: 200
{
  "message": "Payment processed successfully",
  "payment": {
    "id": 1,
    "booking_id": 1,
    "amount": 3300.00,
    "status": "completed"
  }
}
```

**GET /api/payments/booking/{booking_id}**
```
Headers: Authorization: Bearer {access_token}

Response: 200
{
  "id": 1,
  "booking_id": 1,
  "amount": 3300.00,
  "payment_method": "credit_card",
  "status": "completed",
  "payment_date": "2025-11-28T10:30:00"
}
```

### Admin Endpoints (JWT Required + is_admin=true)

**GET /api/admin/bookings**
```
Headers: Authorization: Bearer {access_token}

Response: 200 (all bookings with user details)
```

**GET /api/admin/stats**
```json
Headers: Authorization: Bearer {access_token}

Response: 200
{
  "total_bookings": 150,
  "total_revenue": 450000.00,
  "active_users": 50,
  "trains_running": 45
}
```

## Error Responses

All endpoints return consistent error format:

```json
{
  "error": "Error message description"
}
```

Common HTTP Status Codes:
- **200**: Success
- **201**: Created
- **400**: Bad Request (validation error)
- **401**: Unauthorized (missing/invalid JWT)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found
- **500**: Internal Server Error

## Authentication Flow

1. User registers via `/api/auth/register`
2. User logs in via `/api/auth/login` → receives JWT token
3. Store token in localStorage/sessionStorage
4. Include token in all protected requests:
   ```javascript
   headers: {
     'Authorization': `Bearer ${token}`
   }
   ```
5. Token expires after 1 hour (configurable)

## Data Validation Rules

**Bookings:**
- `passenger_name`: Required, 2-100 characters
- `passenger_age`: Required, 1-120
- `passenger_gender`: Required, "Male"/"Female"/"Other"
- `seat_class`: Required, "economy"/"ac"/"sleeper"
- `seat_number`: Required, alphanumeric
- `journey_date`: Required, future date

**User Registration:**
- `email`: Valid email format, unique
- `username`: 3-80 characters, unique, alphanumeric
- `password`: Minimum 6 characters
- `phone`: Valid phone format

## Business Logic

1. **Seat Availability**: When booking, system checks `available_seats` > 0
2. **Booking Reference**: Auto-generated as "BK" + date + sequence
3. **Fare Calculation**: Based on `seat_class`:
   - economy → `base_fare`
   - ac → `ac_fare`
   - sleeper → `sleeper_fare`
4. **Status Transitions**:
   - Booking: confirmed → completed/cancelled
   - Payment: pending → paid/refunded

## Example Frontend Workflows

### Search & Book Flow
1. User searches trains (GET `/api/search/trains`)
2. Display results with filters (time, price, duration)
3. User selects train → show schedule details
4. User clicks "Book" → redirect to login if not authenticated
5. User fills passenger form → POST `/api/bookings`
6. Show booking confirmation with reference number
7. User proceeds to payment → POST `/api/payments/process`
8. Show success message with ticket details

### User Dashboard
1. Fetch user bookings (GET `/api/bookings`)
2. Display upcoming/past bookings
3. Allow cancellation for upcoming bookings (DELETE `/api/bookings/{id}`)
4. Show booking history with payment status

## Important Notes

- All datetime fields are in ISO 8601 format: `YYYY-MM-DDTHH:MM:SS`
- Prices are in Pakistani Rupees (PKR)
- Distance is in kilometers
- Duration is in minutes
- Phone numbers use Pakistani format (+92...)
- CORS is enabled for all origins in development

## Testing the Backend

Backend is running and accessible at:
```
http://localhost:5001/api
```

Health check endpoint:
```
GET http://localhost:5001/health
```

You can test APIs using:
- Postman
- cURL
- Browser fetch/axios

## Database Access (Optional)

If you need direct database access:
```bash
docker exec -it railway_mysql mysql -u railway_user -prailway_password railway_db
```

## UI/UX Design Reference: Trainline-Style Interface

Design the frontend to match the modern, clean aesthetic of [Trainline](https://www.thetrainline.com):

### Design Principles

**Visual Style:**
- Clean, minimalist interface with plenty of white space
- Modern sans-serif typography (similar to Trainline's font stack)
- Rounded corners on cards and buttons
- Subtle shadows for depth
- Mobile-first responsive design

**Color Palette:**
- Primary: Blue (#00D8A0 or similar teal/green for CTAs)
- Secondary: Dark blue/navy for text and headers
- Accent: Orange/yellow for highlights and deals
- Background: Light gray/white (#F7F8FA)
- Text: Dark gray (#333) for primary, lighter gray for secondary

### Homepage Layout

**Hero Section:**
```
┌─────────────────────────────────────────────┐
│  Navigation Bar (Logo | Bookings | Login)   │
├─────────────────────────────────────────────┤
│                                             │
│     PROMINENT SEARCH WIDGET (Center)        │
│                                             │
│   [From Station]  ⇄  [To Station]          │
│                                             │
│   [Date Picker]   [One-way/Return Toggle]   │
│                                             │
│      [Large Search Button]                  │
│                                             │
└─────────────────────────────────────────────┘
```

**Search Widget Details:**
- Large, centered, card-style form with subtle shadow
- Station inputs with autocomplete dropdown
- Swap button (⇄) between from/to stations
- Calendar picker showing month view with prices (if available)
- One-way/Return toggle buttons
- Prominent green/blue "Search Trains" button
- Optional: "Add voucher code" link below

**Below Hero:**
1. **Popular Routes Section**
   - Grid of clickable route cards (3-4 per row)
   - Each card shows: Route name, starting price, train type
   - Example: "Karachi → Lahore | From Rs. 1,500"

2. **Features Section** (3-column layout)
   - Icon + heading + description
   - Examples:
     * "Best Price Guarantee" - Compare all available trains
     * "Secure Payment" - Multiple payment options
     * "Real-time Updates" - Track your journey

3. **How It Works** (3-step process)
   - Search → Book → Travel
   - Each step with icon and brief description

4. **App Download Section**
   - Large visual of mobile app
   - App store badges
   - Features list (digital tickets, notifications, manage bookings)

### Search Results Page

**Layout:**
```
┌─────────────────────────────────────────────┐
│  [From] → [To] | [Date] | [Edit Search]    │
├───────────┬─────────────────────────────────┤
│           │                                 │
│ FILTERS   │   TRAIN RESULTS (Sorted)        │
│           │                                 │
│ Sort By   │   ┌─────────────────────────┐  │
│ ☐ Price   │   │ Train Name | Number     │  │
│ ☐ Time    │   │ 06:00 → 20:30 (14h 30m)│  │
│ ☐Duration │   │ Economy Rs. 1,500       │  │
│           │   │ AC Rs. 3,300            │  │
│ Departure │   │ [Select] buttons        │  │
│ ○ Morning │   └─────────────────────────┘  │
│ ○ Afternoon│                                │
│ ○ Evening │   [More results...]            │
│           │                                 │
│ Class     │                                 │
│ ☐ Economy │                                 │
│ ☐ AC      │                                 │
│ ☐ Sleeper │                                 │
└───────────┴─────────────────────────────────┘
```

**Train Result Cards:**
- Horizontal layout
- Left: Train name, number, type badge
- Middle: Departure/arrival times (large), duration, distance
- Right: Price options stacked (Economy/AC/Sleeper with prices)
- Bottom: "680 seats available" badge, status indicator
- Hover effect: subtle lift shadow
- "Select" or "View Details" button per class

**Features:**
- Sticky filters sidebar on desktop
- Mobile: filters collapse into modal/drawer
- Sort dropdown: "Cheapest", "Fastest", "Earliest departure"
- Loading skeletons while fetching
- Empty state with helpful message if no results

### Booking Flow

**Step 1: Train Selection**
- Highlighted selected train card
- "Continue to passenger details" button

**Step 2: Passenger Details Form**
```
┌────────────────────────────────────┐
│  Booking Summary (Sticky Sidebar)  │
│  ────────────────────────────────  │
│  Train: Karachi Express            │
│  Route: KHI → LHE                  │
│  Date: Dec 1, 2025                 │
│  Class: AC                         │
│  Price: Rs. 3,300                  │
└────────────────────────────────────┘

Main Form:
- Passenger Name (text input)
- Age (number input)
- Gender (radio buttons)
- Seat Number (text input or seat map selector)
- Contact Email (pre-filled if logged in)
- Contact Phone (pre-filled if logged in)

[Continue to Payment] button
```

**Step 3: Payment**
- Payment method selection (cards, icons)
- Credit/Debit card form
- Order summary (collapsible on mobile)
- Terms & conditions checkbox
- "Complete Booking" button (green, prominent)

**Step 4: Confirmation**
- Success message with checkmark animation
- Booking reference (large, copyable)
- Ticket details card
- "Download Ticket" button
- "View My Bookings" link
- Email confirmation message

### User Dashboard

**My Bookings Page:**
```
┌─────────────────────────────────────┐
│  Tabs: [Upcoming] [Past] [Cancelled]│
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Booking Ref: BK20251128001  │   │
│  │ Karachi → Lahore            │   │
│  │ Dec 1, 2025 • AC Class      │   │
│  │ Status: ✓ Confirmed         │   │
│  │                             │   │
│  │ [View Ticket] [Cancel]      │   │
│  └─────────────────────────────┘   │
│                                     │
│  [More bookings...]                 │
└─────────────────────────────────────┘
```

**Booking Detail Page:**
- Full ticket view (printable/downloadable)
- QR code for ticket
- Train journey timeline
- Passenger details
- Payment information
- Cancellation policy
- "Cancel Booking" button (with confirmation modal)

### Navigation & Header

**Desktop Header:**
- Logo (left) - clickable to homepage
- Search icon - opens quick search modal
- My Bookings link
- Sign In / Register buttons (if not logged in)
- User dropdown menu (if logged in):
  * Profile
  * My Bookings
  * Settings
  * Logout

**Mobile Header:**
- Hamburger menu (left)
- Logo (center)
- User icon (right)
- Bottom navigation bar (optional):
  * Home
  * Search
  * Bookings
  * Profile

### Component Specifications

**Buttons:**
- Primary: Solid background, white text, rounded corners (8px)
- Secondary: Outlined, colored text
- Sizes: Small (32px), Medium (40px), Large (48px)
- Hover: Slightly darker shade + subtle lift

**Cards:**
- Border radius: 12px
- Shadow: 0 2px 8px rgba(0,0,0,0.08)
- Hover: 0 4px 16px rgba(0,0,0,0.12)
- Padding: 16-24px

**Form Inputs:**
- Height: 48px
- Border: 1px solid #E0E0E0
- Border radius: 8px
- Focus: Blue border (2px), subtle shadow
- Error state: Red border with error message below

**Typography:**
- Headings: Bold, 24-32px
- Body: Regular, 16px, line-height 1.5
- Small text: 14px
- Large numbers (prices, times): 20-24px, semi-bold

**Icons:**
- Use icon library (Material Icons, Feather, or Heroicons)
- Consistent 20-24px size
- Stroke width: 2px
- Color matches text or primary color

### Responsive Breakpoints

- Mobile: < 640px (single column, stacked layouts)
- Tablet: 640px - 1024px (2 columns where appropriate)
- Desktop: > 1024px (full layout with sidebars)

### Interactive Elements

**Autocomplete Station Search:**
- Dropdown appears on focus/typing
- Highlights matching text
- Shows station code + city
- Keyboard navigation (arrow keys, enter)

**Date Picker:**
- Calendar view with month navigation
- Disable past dates
- Highlight selected date
- Show prices on dates (if available from API)
- Mobile: Native date picker option

**Loading States:**
- Skeleton screens for search results
- Spinner for form submissions
- Progress indicator for multi-step booking

**Notifications/Toasts:**
- Top-right corner
- Auto-dismiss after 5 seconds
- Types: Success (green), Error (red), Info (blue)
- Close button (X)

### Accessibility

- Semantic HTML (header, nav, main, footer)
- ARIA labels for icons and interactive elements
- Keyboard navigation support
- Focus indicators
- Alt text for images
- Color contrast ratio: at least 4.5:1
- Screen reader friendly

### Animations

- Page transitions: Fade in (300ms)
- Card hover: Scale 1.02, shadow increase (200ms)
- Button press: Scale 0.98 (150ms)
- Modal open: Slide up from bottom (400ms)
- Success checkmark: Draw animation (600ms)
- Keep animations subtle and performant

### Example Pages Priority

1. **Homepage** (with search)
2. **Search Results**
3. **Booking Form**
4. **Login/Register**
5. **User Dashboard (My Bookings)**
6. **Booking Confirmation**
7. **Train Details Page**
8. **User Profile/Settings**

### Additional Features (Nice to Have)

- Dark mode toggle
- Save favorite routes
- Price alerts
- Seat map visualization
- Print ticket functionality
- Share booking via email/WhatsApp
- Multi-language support (English/Urdu)
- Recent searches (stored in localStorage)
- Booking history export (PDF/CSV)

### Performance Tips

- Lazy load images
- Code splitting by route
- Cache station/train data in localStorage
- Debounce search input (300ms)
- Optimize images (WebP format)
- Minimize bundle size
- Use CDN for static assets

## Support

The backend is fully functional and tested. All endpoints return proper responses. Focus on building a clean, user-friendly interface that consumes these APIs effectively, following the Trainline-inspired design system outlined above.
