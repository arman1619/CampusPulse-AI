from sqlalchemy import select
from .config import settings
from .database import SessionLocal
from .models import User
from .service import create_user
DEMO=[("student@campuspulse.dev","Demo Student","Student123!","STUDENT"),("staff@campuspulse.dev","Demo Staff","Staff123!","STAFF"),("admin@campuspulse.dev","Demo Admin","Admin123!","ADMIN")]
def main():
    if not settings.seed_demo: return
    with SessionLocal() as db:
        for email,name,password,role in DEMO:
            if not db.scalar(select(User).where(User.email==email)): create_user(db,email,name,password,role)
if __name__=="__main__": main()
