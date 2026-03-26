from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
import os

app = Flask(__name__)

# ========== DATABASE CONFIGURATION ==========
# Use SQLite for local development, PostgreSQL for production
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///analytics.db')

# Handle SQLite path for local development
if DATABASE_URL == 'sqlite:///analytics.db':
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(os.path.dirname(__file__), "analytics.db")}'
else:
    # For production (e.g., PostgreSQL on Render)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)
CORS(app)

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== DATABASE MODELS ==========
class Visit(db.Model):
    """Track all website visits"""
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4 or IPv6
    user_agent = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat()
        }

class Click(db.Model):
    """Track all button clicks"""
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('visit.id'), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'visit_id': self.visit_id,
            'timestamp': self.timestamp.isoformat()
        }

# ========== HELPER FUNCTIONS ==========
def get_client_ip():
    """Get client IP address, handling proxies"""
    if request.environ.get('HTTP_CF_CONNECTING_IP'):
        return request.environ.get('HTTP_CF_CONNECTING_IP')
    elif request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ.get('HTTP_X_FORWARDED_FOR').split(',')[0]
    return request.remote_addr

def get_user_agent():
    """Get user agent string"""
    return request.headers.get('User-Agent', 'Unknown')

# ========== API ENDPOINTS ==========
@app.route("/track-visit", methods=["GET", "POST"])
def track_visit():
    """Track a new page visit"""
    try:
        visit = Visit(
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )
        db.session.add(visit)
        db.session.commit()
        
        total_visits = Visit.query.count()
        logger.info(f"✅ VISIT TRACKED! Total visits: {total_visits}")
        print(f"✅ VISIT TRACKED! Total visits: {total_visits}")
        
        return jsonify({
            "status": "ok",
            "visits": total_visits,
            "id": visit.id
        }), 200
    except Exception as e:
        logger.error(f"❌ Error tracking visit: {str(e)}")
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/track-click", methods=["GET", "POST"])
def track_click():
    """Track a button click"""
    try:
        visit_id = request.args.get('visit_id', type=int)
        
        click = Click(
            visit_id=visit_id,
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )
        db.session.add(click)
        db.session.commit()
        
        total_clicks = Click.query.count()
        logger.info(f"✅ CLICK TRACKED! Total clicks: {total_clicks}")
        print(f"✅ CLICK TRACKED! Total clicks: {total_clicks}")
        
        return jsonify({
            "status": "ok",
            "clicks": total_clicks,
            "id": click.id
        }), 200
    except Exception as e:
        logger.error(f"❌ Error tracking click: {str(e)}")
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/analytics", methods=["GET"])
def analytics():
    """Get analytics data"""
    try:
        total_visits = Visit.query.count()
        total_clicks = Click.query.count()
        
        # Calculate conversion rate
        conversion = (total_clicks / total_visits * 100) if total_visits > 0 else 0
        conversion = min(conversion, 100)  # Cap at 100%
        
        return jsonify({
            "visits": total_visits,
            "clicks": total_clicks,
            "conversion": round(conversion, 2),
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"❌ Error fetching analytics: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/analytics/detailed", methods=["GET"])
def analytics_detailed():
    """Get detailed analytics with timestamps"""
    try:
        visits = Visit.query.all()
        clicks = Click.query.all()
        
        total_visits = len(visits)
        total_clicks = len(clicks)
        conversion = (total_clicks / total_visits * 100) if total_visits > 0 else 0
        conversion = min(conversion, 100)
        
        return jsonify({
            "summary": {
                "visits": total_visits,
                "clicks": total_clicks,
                "conversion": round(conversion, 2)
            },
            "visits": [v.to_dict() for v in visits[-100:]],  # Last 100 visits
            "clicks": [c.to_dict() for c in clicks[-100:]],  # Last 100 clicks
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"❌ Error fetching detailed analytics: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    """Health check endpoint"""
    total_visits = Visit.query.count()
    total_clicks = Click.query.count()
    return jsonify({
        "status": "ok",
        "message": "Backend is running!",
        "visits": total_visits,
        "clicks": total_clicks,
        "endpoints": {
            "track_visit": "/track-visit",
            "track_click": "/track-click",
            "analytics": "/analytics",
            "analytics_detailed": "/analytics/detailed"
        }
    }), 200

# ========== DATABASE INITIALIZATION ==========
def init_db():
    """Initialize the database"""
    with app.app_context():
        db.create_all()
        logger.info("✅ Database initialized successfully")
        print("✅ Database initialized successfully")

# ========== ERROR HANDLERS ==========
@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"status": "error", "message": "Internal server error"}), 500

# ========== MAIN ==========
if __name__ == "__main__":
    init_db()
    
    # For production, use gunicorn
    # For local development, use Flask dev server
    is_production = os.environ.get('ENVIRONMENT') == 'production'
    
    if is_production:
        logger.info("🚀 Running in PRODUCTION mode")
        # In production, gunicorn will run this
        app.run()
    else:
        logger.info("🔧 Running in DEVELOPMENT mode")
        app.run(debug=True, port=5000, host='0.0.0.0')
