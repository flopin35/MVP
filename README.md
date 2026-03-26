# Website Business Landing Page - MVP

A simple, modern landing page with built-in analytics tracking for small business websites.

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Installation & Setup

1. **Install Python dependencies:**

```bash
pip install -r requirements.txt
```

2. **Run the Flask backend:**

```bash
python app.py
```

The backend will start on `http://localhost:5000`

3. **Open the frontend:**
   Open `index.html` in your browser (or use a local server)

### 📊 Viewing Analytics

Once the backend is running, visit:

```
http://localhost:5000/analytics
```

You'll see JSON data with:

- `visits`: Total page visits
- `clicks`: Total button clicks
- `conversion`: Click-to-visit conversion percentage

## 🧪 Testing Locally

1. Refresh the page multiple times → visits should increase
2. Click the button multiple times → clicks should increase
3. Check `/analytics` → conversion % should update

## 🔧 Project Structure

```
├── index.html       # Frontend landing page
├── app.py           # Flask backend with tracking
└── requirements.txt # Python dependencies
```

## 📱 Features

✅ Modern, responsive design
✅ Real-time visit tracking
✅ Button click tracking
✅ Conversion rate calculation
✅ CORS enabled for frontend/backend communication
✅ Clean JSON API

## 🚀 Deployment

### Backend (Render.com)

1. Push to GitHub
2. Create new Web Service on Render
3. Connect your GitHub repo
4. Set start command: `pip install -r requirements.txt && gunicorn app:app`
5. Copy your Render URL

### Frontend (Vercel)

1. Push to GitHub
2. Import project in Vercel
3. No build config needed
4. Update `fetch()` URLs in `index.html` to use your Render backend URL

### Update Frontend API Calls

In `index.html`, replace:

```javascript
fetch("/track-visit");
```

With:

```javascript
fetch("https://your-backend-url/track-visit");
```

## 📈 Next Steps

1. Share the link with friends
2. Track visits and clicks
3. Analyze conversion rate
4. Iterate and improve

---

Built with ❤️ for small business owners
