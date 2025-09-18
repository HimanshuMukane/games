from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, text
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session, relationship, Session
from fastapi import HTTPException, status
from .config import settings
from datetime import datetime

engine = create_engine(settings.DATABASE_URL, echo=True)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, username: str, real_name: str, gender: str = "male", role: str = "user"):
    try:
        # Check if user already exists
        existing_user = get_user_by_username(db, username)
        if existing_user:
            # Update the real_name, gender and role for existing user
            existing_user.real_name = real_name
            existing_user.gender = gender
            existing_user.role = role
            db.commit()
            db.refresh(existing_user)
            return existing_user
        
        # Create new user with gender-based avatar
        import random
        import requests
        
        # Use avatar API based on gender with random numbers
        if gender.lower() == "female":
            # Girl avatar numbers
            girl_numbers = [97, 84, 57, 80, 81, 64, 82, 74, 93, 91, 99, 94, 70, 56, 71, 69, 96, 66, 90, 61, 72, 89, 68, 67, 75, 65, 63, 62, 73, 86, 83, 79, 98, 92, 77, 55, 59, 76, 78, 95, 51, 54, 60, 100, 58, 85, 88, 52, 53, 87]
            avatar_number = random.choice(girl_numbers)
        else:
            # Boy avatar numbers
            boy_numbers = [30, 23, 15, 28, 50, 20, 29, 25, 36, 22, 33, 44, 1, 49, 12, 10, 45, 6, 37, 2, 40, 21, 8, 43, 7, 18, 16, 34, 13, 31, 38, 27, 14, 46, 48, 4, 19, 11, 9, 42, 47, 17, 5, 39, 32, 35, 26, 3, 24, 41]
            avatar_number = random.choice(boy_numbers)
        
        avatar_url = f"https://avatar.iran.liara.run/public/{avatar_number}"
        
        # Try to use API avatar first
        photo = avatar_url  # Default to API URL
        
        # Fallback to local avatars if API fails
        try:
            # Test if API is accessible
            response = requests.get(avatar_url, timeout=5)
            if response.status_code != 200:
                raise Exception(f"API returned status {response.status_code}")
            print(f"Successfully using API avatar: {avatar_url}")
        except Exception as e:
            # Fallback to local avatars
            print(f"API failed ({str(e)}), using local avatar")
            PROFILE_IMAGES = [f"/static/images/avatar{i}.png" for i in range(1, 41)]
            photo = random.choice(PROFILE_IMAGES)
        
        user = User(
            username=username, 
            real_name=real_name, 
            gender=gender,
            role=role,
            profile_photo=photo, 
            points=0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        print(f"Create user error: {str(e)}")  # Debug logging
        db.rollback()
        raise e


def verify_admin_access(db: Session, username: str) -> bool:
    user = get_user_by_username(db, username)
    return user and user.role == "admin"


def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to MySQL server without specifying database
        server_url = settings.DATABASE_URL.replace('/housie_game', '')
        server_engine = create_engine(server_url)
        
        with server_engine.connect() as conn:
            # Create database if it doesn't exist
            conn.execute(text("CREATE DATABASE IF NOT EXISTS housie_game"))
            conn.commit()
        
        server_engine.dispose()
        print("Database 'housie_game' created or already exists")
    except Exception as e:
        print(f"Error creating database: {str(e)}")
        raise e


def create_tables():
    """Create all tables in the database"""
    try:
        # Create database first
        create_database()
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Add gender column to existing users if it doesn't exist
        add_gender_column_if_not_exists()
        
        # Add sample treasure hunt data
        add_sample_treasure_hunt_data()
        
        print("All tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        raise e

def add_sample_treasure_hunt_data():
    """Add sample treasure hunt questions to the database"""
    try:
        db = SessionLocal()
        
        # Check if treasure hunt data already exists
        existing_count = db.query(TreasureHunt).count()
        if existing_count > 0:
            print(f"Treasure hunt data already exists ({existing_count} questions)")
            db.close()
            return
        
        # Sample treasure hunt questions with hints
        sample_questions = [
            {
                "question": "What is the capital of France?",
                "answer": "PARIS",
                "hint1": "It starts with P",
                "hint2": "It's known as the City of Light"
            },
            {
                "question": "What is 2 + 2?",
                "answer": "FOUR",
                "hint1": "It's a single digit number",
                "hint2": "It's the number after three"
            },
            {
                "question": "What color is the sky?",
                "answer": "BLUE",
                "hint1": "It's a primary color",
                "hint2": "It's the color of the ocean"
            },
            {
                "question": "What is the largest planet?",
                "answer": "JUPITER",
                "hint1": "It's a gas giant",
                "hint2": "It has a great red spot"
            },
            {
                "question": "What is the smallest country?",
                "answer": "VATICAN",
                "hint1": "It's located in Rome",
                "hint2": "It's the home of the Pope"
            }
        ]
        
        # Add questions to database
        for i, question in enumerate(sample_questions, 1):
            treasure_question = TreasureHunt(
                question=question["question"],
                answer=question["answer"],
                hint1=question["hint1"],
                hint2=question["hint2"],
                answered_by=0,
                hint1_shown=0,
                hint2_shown=0
            )
            db.add(treasure_question)
        
        db.commit()
        print(f"✅ Added {len(sample_questions)} sample treasure hunt questions")
        
    except Exception as e:
        print(f"❌ Error adding sample treasure hunt data: {str(e)}")
        db.rollback()
    finally:
        db.close()


def add_gender_column_if_not_exists():
    """Add gender column to users table if it doesn't exist"""
    try:
        with engine.connect() as conn:
            # Check if gender column exists
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'housie_game' 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'gender'
            """))
            
            if result.fetchone()[0] == 0:
                # Add gender column
                conn.execute(text("ALTER TABLE users ADD COLUMN gender VARCHAR(10) NOT NULL DEFAULT 'male'"))
                conn.commit()
                print("Gender column added to users table")
            else:
                print("Gender column already exists")
                
            # Update existing users with new avatars if they have old local paths
            update_existing_user_avatars()
    except Exception as e:
        print(f"Error adding gender column: {str(e)}")
        # Don't raise the error as this is not critical


def encrypt_answer(answer):
    """
    Encrypt answer using the specified algorithm:
    - Letters: A=0, B=1, ..., Z=25
    - Numbers are comma-separated
    - Space is represented as 100
    - Case insensitive
    - Punctuation marks are kept as is
    """
    if not answer:
        return ""
    
    encrypted = []
    for char in answer.upper():
        if char == ' ':
            encrypted.append('100')
        elif char.isalpha():
            # A=0, B=1, ..., Z=25 (no subtraction needed)
            num = ord(char) - ord('A')
            encrypted.append(str(num))
        else:
            # For non-alphabetic characters (punctuation), keep as is
            encrypted.append(char)
    
    return ','.join(encrypted)

def update_existing_user_avatars():
    """Update existing users with new gender-based avatars"""
    try:
        import random
        import requests
        db = SessionLocal()
        users = db.query(User).all()
        
        print(f"Found {len(users)} users to check for avatar updates")
        
        for user in users:
            # Update ALL users with new avatar system (not just old ones)
            print(f"Updating avatar for user {user.username} (gender: {user.gender})")
            
            if user.gender and user.gender.lower() == "female":
                # Girl avatar numbers
                girl_numbers = [97, 84, 57, 80, 81, 64, 82, 74, 93, 91, 99, 94, 70, 56, 71, 69, 96, 66, 90, 61, 72, 89, 68, 67, 75, 65, 63, 62, 73, 86, 83, 79, 98, 92, 77, 55, 59, 76, 78, 95, 51, 54, 60, 100, 58, 85, 88, 52, 53, 87]
                avatar_number = random.choice(girl_numbers)
            else:
                # Boy avatar numbers (default to male if gender not set)
                boy_numbers = [30, 23, 15, 28, 50, 20, 29, 25, 36, 22, 33, 44, 1, 49, 12, 10, 45, 6, 37, 2, 40, 21, 8, 43, 7, 18, 16, 34, 13, 31, 38, 27, 14, 46, 48, 4, 19, 11, 9, 42, 47, 17, 5, 39, 32, 35, 26, 3, 24, 41]
                avatar_number = random.choice(boy_numbers)
            
            avatar_url = f"https://avatar.iran.liara.run/public/{avatar_number}"
            
            # Test if API is accessible
            try:
                response = requests.get(avatar_url, timeout=5)
                if response.status_code == 200:
                    old_avatar = user.profile_photo
                    user.profile_photo = avatar_url
                    print(f"  ✅ Updated {user.username}: {old_avatar} -> {avatar_url}")
                else:
                    print(f"  ❌ API returned status {response.status_code} for user {user.username}")
            except Exception as e:
                print(f"  ❌ API error for user {user.username}: {str(e)}")
        
        db.commit()
        print(f"✅ Avatar update completed for {len(users)} users")
    except Exception as e:
        print(f"❌ Error updating existing user avatars: {str(e)}")
    finally:
        db.close()


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    role = Column(String(50), nullable=False, default="user")
    real_name = Column(String(100), nullable=False)
    gender = Column(String(10), nullable=False, default="male")  # male or female
    profile_photo = Column(String(255))
    points = Column(Integer, default=0)
    is_deleted = Column(Integer, default=0)  # 0 = active, 1 = soft deleted


class HousieNumber(Base):
    __tablename__ = "housie_numbers"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    number_drawn = Column(Integer, nullable=False)


class TreasureHunt(Base):
    __tablename__ = "treasurehunt"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hint = Column(String(1000), nullable=False)  # The hint/riddle
    answer = Column(String(255), nullable=False)  # Correct answer
    answered_by = Column(Integer, default=0)  # 0 = not answered, user_id = answered by user
    hint_shown = Column(Integer, default=1)  # 1 = always shown (hints are always visible)
