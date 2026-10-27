
from typing import Annotated ,Optional

from fastapi import Depends, FastAPI, HTTPException , status
from pydantic import  EmailStr , Field as PydanticField
from sqlmodel import SQLModel , create_engine , Session , Field, select
from sqlalchemy.orm import sessionmaker

from pwdlib import PasswordHash


#------Request and Response Schema-----
class UserBaseModel(SQLModel):
    email : EmailStr 

class UserIn(UserBaseModel):
    password : str = PydanticField(min_length=8, description="Plain text user password")

class UserResponse(UserBaseModel):
    pass

#-------User Table Model----------
# Used SQLModel to avoid duplicating models in SQlAchemy and Pydantic
class Users(UserBaseModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True)
    password_hash : str 

#-------Set up SQLite db----
sqlite_file_name = "users.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# 'connect_args={"check_same_thread": False}' is required when using SQLite with multi-threaded frameworks like FastAPI
connect_args = {"check_same_thread": False} 
engine = create_engine(sqlite_url, connect_args=connect_args)
SQLModel.metadata.create_all(engine)
SessionLocal = sessionmaker(class_=Session, autocommit=False, autoflush=False, bind=engine)




app = FastAPI()



# Utility Funtions 
#  returns a passwordhash with recommended hasher , Argon2
password_hash = PasswordHash.recommended()

def get_hashed_password(password):
    return  password_hash.hash(password)

def verity_password(plain_password,hashed_password):
    return password_hash.verify(plain_password,hashed_password)


#----- Session dependency ----
def get_session():
    db = SessionLocal()
    try:
        yield db  # The session is injected into the route here
    finally:
        db.close()

SessionDep = Annotated[Session, Depends(get_session)]

@app.post("/auth/signup/",status_code=status.HTTP_201_CREATED ,response_model=UserResponse)
def sign_up(user:UserIn, session:SessionDep):

    user_in_db= session.exec(select(Users).where(Users.email == user.email)).first()
    if user_in_db is  None :    

        userdb = Users(
            email=user.email,
            password_hash = get_hashed_password(user.password)
        )
        session.add(userdb)
        session.commit()
        session.refresh(userdb)

        return UserResponse(email=userdb.email)
    
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email address already exists")







