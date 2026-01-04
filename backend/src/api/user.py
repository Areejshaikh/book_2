from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.database.session import engine
from src.models.user_profile import UserProfile

# Create SessionLocal using the engine from database.session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


router = APIRouter()


@router.put("/{user_id}")
def update_user_profile(user_id: int, profile_data: dict):
    db = SessionLocal()
    try:
        # Check if profile exists
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

        if profile:
            # Update existing profile
            for field, value in profile_data.items():
                if hasattr(profile, field):
                    setattr(profile, field, value)
        else:
            # Create new profile
            profile = UserProfile(user_id=user_id, **{k: v for k, v in profile_data.items() if hasattr(UserProfile, k)})
            db.add(profile)

        db.commit()
        db.refresh(profile)

        return {"message": "User profile updated successfully", "profile_id": profile.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user profile: {str(e)}")
    finally:
        db.close()