from flask import Flask, request
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)

client = MongoClient("mongodb+srv://rishukumar2201180_db_user:YOUR_NEW_PASSWORD@YOUR_CLUSTER.mongodb.net/")
db = client["blog_database"]

users = db["users"]
blogs = db["blogs"]

app.config["JWT_SECRET_KEY"] = "secret"
jwt = JWTManager(app)


@app.route("/register", methods=["POST"])
def register():

    data = request.json

    name = data["name"]
    email = data["email"]
    password = data["password"]

    if users.find_one({"email": email}):
        return {"message": "Email already exists"}, 409

    password = generate_password_hash(password)

    users.insert_one({
        "name": name,
        "email": email,
        "password": password
    })

    return {"message": "User registered"}, 201


@app.route("/login", methods=["POST"])
def login():

    data = request.json

    email = data["email"]
    password = data["password"]

    user = users.find_one({"email": email})

    if not user:
        return {"message": "Invalid email or password"}, 401

    if not check_password_hash(user["password"], password):
        return {"message": "Invalid email or password"}, 401

    token = create_access_token(identity=str(user["_id"]))

    return {"token": token}, 200


@app.route("/blogs", methods=["POST"])
@jwt_required()
def create_blog():

    data = request.json

    title = data["title"]
    content = data["content"]

    user_id = get_jwt_identity()

    blogs.insert_one({
        "title": title,
        "content": content,
        "user_id": user_id
    })

    return {"message": "Blog created"}, 201


if __name__ == "__main__":
    app.run(debug=True)