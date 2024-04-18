from fastapi import FastAPI, HTTPException, Depends
import models
from pydantic import BaseModel, Field
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import select

app = FastAPI()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class Employee(BaseModel):
    name: str
    department: str

@app.on_event("startup")
def startup():
    models.Base.metadata.create_all(bind=engine)

@app.get("/employees/")
async def return_employees(db: Session = Depends(get_db)):
    return db.query(models.Employee).all()

@app.get("/employees/{employee_id}")
async def return_employee(employee_id: int, db: Session = Depends(get_db)):
    employee_obj = db.query(models.Employee).filter(models.Employee.id==employee_id).first()

    if employee_obj is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {employee_id} : Does not exist"
        )
    return employee_obj

@app.post("/add-employees/")
async def create_employee(employee: Employee, db: Session = Depends(get_db)):
    employee_obj = models.Employee()
    employee_obj.name = employee.name
    employee_obj.department = employee.department

    db.add(employee_obj)
    db.commit()

    return employee

@app.delete("/employees/{employee_id}")
async def return_employee(employee_id: int, db: Session = Depends(get_db)):
    employee_obj = db.query(models.Employee).filter(models.Employee.id==employee_id).first()

    if employee_obj is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {employee_id} : Does not exist"
        )

    db.query(models.Employee).filter(models.Employee.id==employee_id).delete()
    db.commit()

@app.put("/employees/{employee_id}/{column}/{new_value}")
async def update_table(employee_id: int, column: str, new_value: str, db: Session = Depends(get_db)):
    employee_obj = db.query(models.Employee).filter(models.Employee.id == employee_id).first()

    if employee_obj is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {employee_id} : Does not exist"
        )

    if hasattr(employee_obj, column):
        setattr(employee_obj, column, new_value)
        db.commit()
    else:
        raise HTTPException(status_code=400, detail=f"Column {column} does not exist")

    return employee_obj
