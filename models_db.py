"""
Database models - Single file to avoid circular imports
"""

from app import db
from datetime import datetime

class Image(db.Model):
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(512), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    culture_type = db.Column(db.String(50), default='unknown')
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=True)
    
    manual_counts = db.relationship('ManualCount', backref='image', lazy=True, cascade='all, delete-orphan')
    automatic_counts = db.relationship('AutomaticCount', backref='image', lazy=True, cascade='all, delete-orphan')

class Batch(db.Model):
    __tablename__ = 'batches'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100), nullable=False)
    total_images = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    images = db.relationship('Image', backref='batch', lazy=True)
    counting_sessions = db.relationship('BatchCountingSession', backref='batch', lazy=True)

class BatchCountingSession(db.Model):
    __tablename__ = 'batch_counting_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    technician_name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    total_time_seconds = db.Column(db.Float, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    
    image_counts = db.relationship('BatchImageCount', backref='session', lazy=True, cascade='all, delete-orphan')

class BatchImageCount(db.Model):
    __tablename__ = 'batch_image_counts'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('batch_counting_sessions.id'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=False)
    manual_count = db.Column(db.Integer, nullable=False)
    time_taken_seconds = db.Column(db.Float, nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

class AutomaticBatchResult(db.Model):
    __tablename__ = 'automatic_batch_results'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    model_used = db.Column(db.String(100), nullable=False)
    model_type = db.Column(db.String(50), default='default')
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_time_seconds = db.Column(db.Float, nullable=True)
    results = db.Column(db.JSON, nullable=True)
    
    image_results = db.relationship('AutomaticImageResult', backref='batch_result', lazy=True, cascade='all, delete-orphan')

class AutomaticImageResult(db.Model):
    __tablename__ = 'automatic_image_results'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_result_id = db.Column(db.Integer, db.ForeignKey('automatic_batch_results.id'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    processing_time = db.Column(db.Float, nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    confidence = db.Column(db.Float, nullable=True)
    detection_details = db.Column(db.JSON, nullable=True)

class CountSession(db.Model):
    __tablename__ = 'count_sessions'
    id = db.Column(db.Integer, primary_key=True)
    technician_name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    culture_type = db.Column(db.String(50), default='unknown')
    manual_counts = db.relationship('ManualCount', backref='session', lazy=True, cascade='all, delete-orphan')

class ManualCount(db.Model):
    __tablename__ = 'manual_counts'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('count_sessions.id'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    time_taken_seconds = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    culture_type = db.Column(db.String(50), default='unknown')

class AutomaticCount(db.Model):
    __tablename__ = 'automatic_counts'
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    processing_time = db.Column(db.Float, nullable=False)
    model_version = db.Column(db.String(100), default='yolo11m')
    model_type = db.Column(db.String(50), default='default')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    detection_details = db.Column(db.JSON, nullable=True)