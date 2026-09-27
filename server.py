import os

from flask import Flask, Response,jsonify, request, render_template, redirect, url_for, session
from flask.views import MethodView

from dotenv import load_dotenv

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from db import Session, Ads, User
from errors import HttpError
from schema import validate, RegisterUser, CreateAds, UpdateAds, LoginUser


class IndexView(MethodView):
    def get(self):
        return redirect(url_for("ads_list"))


class AdsList(MethodView):
    def get(self):
        ads = request.session.query(Ads).all()
        return render_template(
            "index.html",
            ads=[ads.dict for ads in ads]
        )

    def post(self):
        user_id = session.get("user_id")
        if user_id is None:
            return jsonify({"error": "You must be logged in"}), 401
        json_data = validate(request.get_json(), CreateAds)
        if not json_data or "title" not in json_data:
            return jsonify({"error": "Missing title"}), 400
        ad = Ads(title=json_data["title"],owner_id=user_id)
        add_ads(ad)
        return jsonify(ad.id_dict), 201


class AdsDetail(MethodView):
    def get(self, ads_id):
        ads = get_ads(ads_id)
        return jsonify(ads.dict)

    def patch(self, ads_id):
        json_data = validate(request.get_json(), UpdateAds)
        if not json_data:
            return jsonify({"error": "Empty request"}), 400
        user_id = session.get("user_id")
        if user_id is None:
            return jsonify({"error": "You must be logged in"}), 401
        ads = get_ads(ads_id)
        if ads.owner_id != user_id:
            return jsonify({"error": "You cannot edit this ad"}), 403
        if "title" in json_data:
            ads.title = json_data["title"]
        add_ads(ads)
        return jsonify(ads.dict)

    def delete(self, ads_id):
        user_id = session.get("user_id")
        if user_id is None:
            return jsonify({"error": "You must be logged in"}), 401
        ads = get_ads(ads_id)
        if ads.owner_id != user_id:
            return jsonify({"error": "You cannot delete this ad"}), 403
        request.session.delete(ads)
        request.session.commit()
        return jsonify({"message": "deleted"})


class RegisterView(MethodView):
    def post(self):
        data = validate(request.get_json(), RegisterUser)
        if not data:
            return jsonify({"error": "Empty request"}), 400
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        if not username or not email or not password:
            return jsonify({"error": "username, email and password are required"}), 400
        user = User(username=username,email=email)
        user.hash_password(password)
        add_user(user)
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email
        }), 201

class LoginView(MethodView):
    def post(self):
        data = validate(request.get_json(), LoginUser)
        username = data.get("username")
        password = data.get("password")
        user = request.session.scalar(
            select(User).where(
                User.username == username
            )
        )
        if user is None:
            return jsonify({
                "error": "Invalid username or password"
            }), 401
        if not user.check_password(password):
            return jsonify({
                "error": "Invalid username or password"
            }), 401

        session["user_id"] = user.id

        return jsonify({
            "message": "Login successful",
            "user_id": user.id
        })

class LogoutView(MethodView):
    def post(self):
        session.pop("user_id", None)
        return jsonify({
            "message": "Logout successful"
        })


app = Flask(__name__)

load_dotenv()
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "dev-secret-key"
)

app.json.ensure_ascii = False

@app.before_request
def before_request():
    session = Session()
    request.session = session

@app.after_request
def after_requests(response: Response):
    request.session.close()
    return response

@app.errorhandler(HttpError)
def error_handler(err: HttpError):
    response = jsonify({"error": err.message})
    response.status_code = err.status_code
    return response

def get_user(user_id: int) -> User:
    user = request.session.get(User, user_id)
    if user is None:
        raise HttpError("user not found", 404)
    return user

def add_user(user: User):
    request.session.add(user)
    try:
        request.session.commit()
    except IntegrityError:
        raise HttpError("user already exists", 400)

def get_ads(ads_id: int) -> User:
    ads = request.session.get(Ads, ads_id)
    if ads is None:
        raise HttpError("ads not found", 404)
    return ads

def add_ads(ads: Ads):
    request.session.add(ads)
    try:
        request.session.commit()
    except IntegrityError:
        raise HttpError("user already exists", 400)

app.add_url_rule('/', view_func=IndexView.as_view('to_ads'), methods=['GET'])
app.add_url_rule('/ads', view_func=AdsList.as_view('ads_list'), methods=['GET', 'POST'])
app.add_url_rule('/ads/<int:ads_id>', view_func=AdsDetail.as_view('ads_detail'), methods=['GET', 'PATCH', 'DELETE'])
app.add_url_rule('/register', view_func=RegisterView.as_view('register'), methods=['POST'])
app.add_url_rule('/login', view_func=LoginView.as_view('login'), methods=['POST'])
app.add_url_rule('/logout', view_func=LogoutView.as_view('logout'), methods=['POST'])

if __name__ == '__main__':
    app.run()