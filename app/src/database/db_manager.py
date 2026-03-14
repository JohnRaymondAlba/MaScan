"""Database manager for PostgreSQL/Supabase using SQLAlchemy ORM."""

import os
import time
import random
import bcrypt
import json
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

# Database Models
class Event(Base):
    """Event model"""
    __tablename__ = 'events'
    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    date = Column(String(50), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    attendances = relationship('Attendance', back_populates='event', cascade='all, delete-orphan')

class Attendance(Base):
    """Attendance model"""
    __tablename__ = 'attendance'
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(50), ForeignKey('events.id'), nullable=False)
    user_id = Column(String(50), nullable=False)
    user_name = Column(String(255), nullable=False)
    timestamp = Column(String(50), nullable=False)
    status = Column(String(50), default='Checked In')
    time_slot = Column(String(50), default='morning')
    created_at = Column(DateTime, default=datetime.utcnow)
    event = relationship('Event', back_populates='attendances')

class User(Base):
    """User model"""
    __tablename__ = 'users'
    username = Column(String(50), primary_key=True)
    password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default='scanner')
    created_at = Column(DateTime, default=datetime.utcnow)

class ActivityLog(Base):
    """Activity log model"""
    __tablename__ = 'activity_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String(50), nullable=False)
    action = Column(String(255), nullable=False)
    user = Column(String(50), nullable=False)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class LoginHistory(Base):
    """Login history model"""
    __tablename__ = 'login_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), ForeignKey('users.username'))
    login_time = Column(String(50), nullable=False)
    logout_time = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class ScanHistory(Base):
    """Scan history model"""
    __tablename__ = 'scan_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    scanner_username = Column(String(50), ForeignKey('users.username'))
    scanned_user_id = Column(String(50), nullable=False)
    scanned_user_name = Column(String(255), nullable=False)
    event_id = Column(String(50), ForeignKey('events.id'))
    scan_time = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class StudentQRCode(Base):
    """Student QR code model"""
    __tablename__ = 'students_qrcodes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    school_id = Column(String(50), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    last_name = Column(String(255))
    first_name = Column(String(255))
    middle_initial = Column(String(5))
    year_level = Column(String(50))
    section = Column(String(50))
    course = Column(String(255))
    qr_data = Column(Text, nullable=False, unique=True)
    qr_data_encoded = Column(Text, nullable=False)
    csv_data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class AttendanceTimeslot(Base):
    """Attendance with multiple time slots"""
    __tablename__ = 'attendance_timeslots'
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(50), ForeignKey('events.id'), nullable=False)
    user_id = Column(String(50), nullable=False)
    morning_time = Column(String(50))
    morning_status = Column(String(50), default='Absent')
    lunch_time = Column(String(50))
    lunch_status = Column(String(50), default='Absent')
    afternoon_time = Column(String(50))
    afternoon_status = Column(String(50), default='Absent')
    date_recorded = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Database:
    """Database manager for PostgreSQL/Supabase using SQLAlchemy."""
    
    def __init__(self, db_url: str = None):
        """Initialize database connection."""
        if db_url is None:
            db_url = os.getenv('DATABASE_URL')
        
        if not db_url:
            # Fallback to SQLite for local development
            db_path = os.path.join(os.path.dirname(__file__), '../..', 'mascan_attendance.db')
            db_url = f'sqlite:///{db_path}'
            print(f"Using SQLite fallback: {db_path}")
        else:
            # Fix psycopg2 driver prefix for standard postgresql:// URLs
            if db_url.startswith('postgresql://'):
                db_url = db_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
            print("Using Supabase/PostgreSQL database")
        
        # Create engine with no connection pooling for serverless
        try:
            self.engine = create_engine(
                db_url,
                poolclass=NullPool,
                echo=False,
                connect_args={'connect_timeout': 10} if 'postgresql' in db_url else {}
            )
        except Exception as e:
            print(f"Error creating engine: {e}")
            self.engine = create_engine('sqlite:///mascan_attendance.db', poolclass=NullPool)
        
        # Create all tables
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        self._ensure_admin_role()
    
    def _get_session(self):
        """Get a new database session."""
        return self.Session()
    
    def _ensure_admin_role(self):
        """Ensure admin user exists."""
        try:
            session = self._get_session()
            admin = session.query(User).filter_by(username='admin').first()
            
            if not admin:
                hashed = self.hash_password('Admin@123')
                admin = User(username='admin', password=hashed, full_name='Administrator', role='admin')
                session.add(admin)
                session.commit()
                print("Admin user created")
            elif admin.role != 'admin':
                admin.role = 'admin'
                session.commit()
                print("Admin role updated")
            
            session.close()
        except Exception as e:
            print(f"Error ensuring admin: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        except:
            return False
    
    # Event operations
    def get_all_events(self) -> List:
        """Get all events."""
        try:
            session = self._get_session()
            events = session.query(Event).order_by(Event.date.desc()).all()
            result = [(e.id, e.name, e.date, e.description) for e in events]
            session.close()
            return result
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    def get_event_by_id(self, event_id: str) -> Optional[Dict]:
        """Get event by ID."""
        try:
            session = self._get_session()
            event = session.query(Event).filter_by(id=event_id).first()
            result = None
            if event:
                result = {"id": event.id, "name": event.name, "date": event.date, "desc": event.description or "No description"}
            session.close()
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def create_event(self, name: str, date: str, description: str) -> str:
        """Create event."""
        try:
            new_id = f"EID{int(time.time())}{random.randint(10, 99)}"
            session = self._get_session()
            event = Event(id=new_id, name=name, date=date, description=description)
            session.add(event)
            session.commit()
            session.close()
            return new_id
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def delete_event(self, event_id: str) -> bool:
        """Delete event."""
        try:
            session = self._get_session()
            event = session.query(Event).filter_by(id=event_id).first()
            if event:
                session.delete(event)
                session.commit()
                session.close()
                return True
            session.close()
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    # User operations
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user."""
        try:
            session = self._get_session()
            user = session.query(User).filter_by(username=username).first()
            if user and self.verify_password(password, user.password):
                session.close()
                return username
            session.close()
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_user_role(self, username: str) -> Optional[str]:
        """Get user role."""
        try:
            session = self._get_session()
            user = session.query(User).filter_by(username=username).first()
            role = user.role if user else None
            session.close()
            return role
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_all_users(self) -> List[Tuple]:
        """Get all users."""
        try:
            session = self._get_session()
            users = session.query(User).order_by(User.username).all()
            result = [(u.username, u.full_name, u.role) for u in users]
            session.close()
            return result
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    def create_user(self, username: str, password: str, full_name: str, role: str = 'scanner') -> bool:
        """Create user."""
        try:
            session = self._get_session()
            if session.query(User).filter_by(username=username).first():
                session.close()
                return False
            hashed = self.hash_password(password)
            user = User(username=username, password=hashed, full_name=full_name, role=role)
            session.add(user)
            session.commit()
            session.close()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def update_user(self, username: str, password: str = None, full_name: str = None, role: str = None) -> bool:
        """Update user."""
        try:
            session = self._get_session()
            user = session.query(User).filter_by(username=username).first()
            if not user:
                session.close()
                return False
            if password:
                user.password = self.hash_password(password)
            if full_name:
                user.full_name = full_name
            if role:
                user.role = role
            session.commit()
            session.close()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def delete_user(self, username: str) -> bool:
        """Delete user."""
        try:
            session = self._get_session()
            user = session.query(User).filter_by(username=username).first()
            if user:
                session.delete(user)
                session.commit()
                session.close()
                return True
            session.close()
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    # Attendance operations
    def record_attendance(self, event_id: str, user_id: str, user_name: str, timestamp: str, status: str = "Checked In") -> bool:
        """Record attendance (backward compatible)."""
        return self.record_attendance_with_timeslot(event_id, user_id, user_name, timestamp, "morning", status)
    
    def record_attendance_with_timeslot(self, event_id: str, user_id: str, user_name: str, timestamp: str, time_slot: str = "morning", status: str = "Checked In") -> bool:
        """Record attendance with time slot."""
        try:
            session = self._get_session()
            attendance = Attendance(event_id=event_id, user_id=user_id, user_name=user_name, timestamp=timestamp, time_slot=time_slot, status=status)
            session.add(attendance)
            session.commit()
            session.close()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def is_user_checked_in(self, event_id: str, user_id: str) -> Optional[str]:
        """Check if user checked in."""
        try:
            session = self._get_session()
            record = session.query(Attendance).filter_by(event_id=event_id, user_id=user_id).first()
            result = record.timestamp if record else None
            session.close()
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def is_checked_in_for_slot(self, event_id: str, user_id: str, time_slot: str) -> Optional[str]:
        """Check if checked in for slot."""
        try:
            session = self._get_session()
            record = session.query(Attendance).filter_by(event_id=event_id, user_id=user_id, time_slot=time_slot).first()
            result = record.timestamp if record else None
            session.close()
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_attendance_by_event(self, event_id: str) -> Dict:
        """Get attendance by event."""
        try:
            session = self._get_session()
            records = session.query(Attendance).filter_by(event_id=event_id).all()
            attendance_log = {}
            for record in records:
                key = f"{record.user_id}_{record.time_slot}"
                attendance_log[key] = {"name": record.user_name, "time": record.timestamp, "status": record.status, "time_slot": record.time_slot}
            session.close()
            return attendance_log
        except Exception as e:
            print(f"Error: {e}")
            return {}
    
    def get_attendance_summary(self, event_id: str) -> Dict:
        """Get attendance summary."""
        try:
            session = self._get_session()
            records = session.query(Attendance).filter_by(event_id=event_id).all()
            morning_count = sum(1 for r in records if r.time_slot == 'morning')
            afternoon_count = sum(1 for r in records if r.time_slot == 'afternoon')
            session.close()
            return {'morning': morning_count, 'afternoon': afternoon_count}
        except Exception as e:
            print(f"Error: {e}")
            return {'morning': 0, 'afternoon': 0}
    
    # Student QR Code operations
    def get_student_by_id(self, school_id: str) -> Optional[Dict]:
        """Get student by ID."""
        try:
            session = self._get_session()
            student = session.query(StudentQRCode).filter_by(school_id=school_id).first()
            result = None
            if student:
                result = {'school_id': student.school_id, 'name': student.name, 'year_level': student.year_level, 'section': student.section}
            session.close()
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def create_student(self, school_id: str, name: str, qr_data: str, qr_data_encoded: str, csv_data: str = None, last_name: str = None, first_name: str = None, middle_initial: str = None, year_level: str = None, section: str = None, course: str = None) -> bool:
        """Create student."""
        try:
            session = self._get_session()
            student = StudentQRCode(school_id=school_id, name=name, qr_data=qr_data, qr_data_encoded=qr_data_encoded, csv_data=csv_data, last_name=last_name, first_name=first_name, middle_initial=middle_initial, year_level=year_level, section=section, course=course)
            session.add(student)
            session.commit()
            session.close()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def update_student(self, school_id: str, name: str, qr_data: str, qr_data_encoded: str, csv_data: str = None, last_name: str = None, first_name: str = None, middle_initial: str = None, year_level: str = None, section: str = None, course: str = None) -> bool:
        """Update student."""
        try:
            session = self._get_session()
            student = session.query(StudentQRCode).filter_by(school_id=school_id).first()
            if not student:
                session.close()
                return False
            student.name = name
            student.qr_data = qr_data
            student.qr_data_encoded = qr_data_encoded
            student.csv_data = csv_data
            student.last_name = last_name
            student.first_name = first_name
            student.middle_initial = middle_initial
            student.year_level = year_level
            student.section = section
            student.course = course
            session.commit()
            session.close()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    # Login and scan tracking
    def record_login(self, username: str) -> bool:
        """Record login."""
        try:
            session = self._get_session()
            log = LoginHistory(username=username, login_time=datetime.now().isoformat())
            session.add(log)
            session.commit()
            session.close()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def record_logout(self, username: str) -> bool:
        """Record logout."""
        try:
            session = self._get_session()
            login = session.query(LoginHistory).filter_by(username=username).filter(LoginHistory.logout_time == None).order_by(LoginHistory.login_time.desc()).first()
            if login:
                login.logout_time = datetime.now().isoformat()
                session.commit()
                session.close()
                return True
            session.close()
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def record_scan(self, scanner_username: str, scanned_user_id: str, scanned_user_name: str, event_id: str) -> bool:
        """Record scan."""
        try:
            session = self._get_session()
            scan = ScanHistory(scanner_username=scanner_username, scanned_user_id=scanned_user_id, scanned_user_name=scanned_user_name, event_id=event_id, scan_time=datetime.now().isoformat())
            session.add(scan)
            session.commit()
            session.close()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def get_recent_logins(self, limit: int = 20) -> List[Dict]:
        """Get recent logins."""
        try:
            session = self._get_session()
            logins = session.query(LoginHistory).order_by(LoginHistory.login_time.desc()).limit(limit).all()
            result = [{'username': l.username, 'login_time': l.login_time, 'logout_time': l.logout_time} for l in logins]
            session.close()
            return result
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    def get_recent_scans(self, limit: int = 20) -> List[Dict]:
        """Get recent scans."""
        try:
            session = self._get_session()
            scans = session.query(ScanHistory).order_by(ScanHistory.scan_time.desc()).limit(limit).all()
            result = [{'scanner_username': s.scanner_username, 'scanned_user_id': s.scanned_user_id, 'scanned_user_name': s.scanned_user_name, 'event_id': s.event_id, 'scan_time': s.scan_time} for s in scans]
            session.close()
            return result
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    def get_scans_by_scanner(self, username: str, limit: int = 20) -> List[Dict]:
        """Get scans by scanner."""
        try:
            session = self._get_session()
            scans = session.query(ScanHistory).filter_by(scanner_username=username).order_by(ScanHistory.scan_time.desc()).limit(limit).all()
            result = [{'scanner_username': s.scanner_username, 'scanned_user_id': s.scanned_user_id, 'scanned_user_name': s.scanned_user_name, 'event_id': s.event_id, 'scan_time': s.scan_time} for s in scans]
            session.close()
            return result
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    # Activity logging
    def log_activity(self, action: str, user: str, details: str = None) -> bool:
        """Log activity."""
        try:
            session = self._get_session()
            log = ActivityLog(timestamp=datetime.now().isoformat(), action=action, user=user, details=details)
            session.add(log)
            session.commit()
            session.close()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def get_activity_log(self, limit: int = 100) -> List[Tuple]:
        """Get activity log."""
        try:
            session = self._get_session()
            logs = session.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(limit).all()
            result = [(l.timestamp, l.action, l.user, l.details) for l in logs]
            session.close()
            return result
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    # Compatibility/wrapper methods
    def get_user(self, username: str):
        """Get user (Flask wrapper)."""
        try:
            session = self._get_session()
            user = session.query(User).filter_by(username=username).first()
            result = (user.username, user.password, user.full_name, user.role) if user else None
            session.close()
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def add_user(self, username: str, password: str, full_name: str, role: str = 'scanner') -> bool:
        """Add user (Flask wrapper)."""
        return self.create_user(username, password, full_name, role)
    
    def add_event(self, event_id: str, name: str, date: str, description: str = "") -> bool:
        """Add event (Flask wrapper)."""
        try:
            session = self._get_session()
            event = Event(id=event_id, name=name, date=date, description=description)
            session.add(event)
            session.commit()
            session.close()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def get_event(self, event_id: str):
        """Get event (Flask wrapper)."""
        try:
            session = self._get_session()
            event = session.query(Event).filter_by(id=event_id).first()
            result = (event.id, event.name, event.date, event.description) if event else None
            session.close()
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None
