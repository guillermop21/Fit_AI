from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    height = db.Column(db.Float, nullable=True)
    goal = db.Column(db.String(50), nullable=True)
    activity_level = db.Column(db.String(50), nullable=True)
    dietary_restrictions = db.Column(db.Text, nullable=True)  # JSON string
    equipment_available = db.Column(db.Text, nullable=True)  # JSON string
    experience_level = db.Column(db.String(20), default='beginner')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    workout_plans = db.relationship('WorkoutPlan', backref='user', lazy=True, cascade='all, delete-orphan')
    nutrition_plans = db.relationship('NutritionPlan', backref='user', lazy=True, cascade='all, delete-orphan')
    progress_entries = db.relationship('ProgressEntry', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'age': self.age,
            'weight': self.weight,
            'height': self.height,
            'goal': self.goal,
            'activity_level': self.activity_level,
            'dietary_restrictions': json.loads(self.dietary_restrictions) if self.dietary_restrictions else [],
            'equipment_available': json.loads(self.equipment_available) if self.equipment_available else [],
            'experience_level': self.experience_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class WorkoutPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    duration_weeks = db.Column(db.Integer, nullable=False)
    difficulty_level = db.Column(db.String(20), nullable=False)
    plan_data = db.Column(db.Text, nullable=False)  # JSON string with workout details
    ai_generated = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'duration_weeks': self.duration_weeks,
            'difficulty_level': self.difficulty_level,
            'plan_data': json.loads(self.plan_data) if self.plan_data else {},
            'ai_generated': self.ai_generated,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

class NutritionPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    duration_weeks = db.Column(db.Integer, nullable=False)
    daily_calories = db.Column(db.Integer, nullable=False)
    macros = db.Column(db.Text, nullable=False)  # JSON string with macronutrient breakdown
    meal_plan = db.Column(db.Text, nullable=False)  # JSON string with meal details
    ai_generated = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'duration_weeks': self.duration_weeks,
            'daily_calories': self.daily_calories,
            'macros': json.loads(self.macros) if self.macros else {},
            'meal_plan': json.loads(self.meal_plan) if self.meal_plan else {},
            'ai_generated': self.ai_generated,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

class ProgressEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    weight = db.Column(db.Float, nullable=True)
    body_fat_percentage = db.Column(db.Float, nullable=True)
    measurements = db.Column(db.Text, nullable=True)  # JSON string with body measurements
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'weight': self.weight,
            'body_fat_percentage': self.body_fat_percentage,
            'measurements': json.loads(self.measurements) if self.measurements else {},
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PlanFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_type = db.Column(db.String(20), nullable=False)  # 'workout' or 'nutrition'
    plan_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 scale
    feedback_text = db.Column(db.Text, nullable=True)
    difficulty_rating = db.Column(db.Integer, nullable=True)  # 1-5 scale
    satisfaction_rating = db.Column(db.Integer, nullable=True)  # 1-5 scale
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_type': self.plan_type,
            'plan_id': self.plan_id,
            'rating': self.rating,
            'feedback_text': self.feedback_text,
            'difficulty_rating': self.difficulty_rating,
            'satisfaction_rating': self.satisfaction_rating,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

