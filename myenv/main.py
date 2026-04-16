from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from models import Product
from database import SessionLocal,engine
import database_models
from sqlalchemy.orm import Session

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
)

database_models.Base.metadata.create_all(bind=engine)



products = [
    Product(id=1, name="Laptop", price=999.99, quantity=10, description="A high-performance laptop"),
    Product(id=2, name="Smartphone", price=499.99, quantity=20, description="A latest model smartphone"),
    Product(id=3, name="Headphones", price=199.99, quantity=50, description="Wireless noise-canceling headphones"),
]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    db = SessionLocal()
    count = db.query(database_models.Product).count()
    if count == 0:
        for product in products:
            db.add(database_models.Product(**product.model_dump()))
    db.commit()
    db.close()
    
init_db()

@app.get("/")
def greetings():
    return {"message": "Hello, welcome to my environment!"}

@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(database_models.Product).all()

@app.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == product_id).first()
    if db_product:
        return db_product
    return {"error": "Product not found"}

@app.post("/products")
def add_product(product: Product, db: Session = Depends(get_db)):
    db.add(database_models.Product(**product.model_dump()))
    db.commit()
    return product

@app.put("/products/{product_id}")
def update_product(product_id: int, updated_product: Product ,db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == product_id).first()
    if db_product:
        db_product.name = updated_product.name
        db_product.price = updated_product.price
        db_product.quantity = updated_product.quantity
        db_product.description = updated_product.description
        db.commit()
        db.refresh(db_product)
        return {"message": "Product updated", "product": db_product}
    else:
        return {"error": "Product not found"}

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return {"message": "Product deleted"}
    return {"error": "Product not found"}