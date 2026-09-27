from flask import jsonify, request, render_template, redirect, url_for, session
from flask.views import MethodView
from sqlalchemy import select

from db import  Ads, User
from server import get_ads, add_ads, add_user


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
        json_data = request.get_json()
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
        json_data = request.get_json()
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
        print("CONTENT TYPE:", request.content_type)
        print("RAW DATA:", request.get_data(as_text=True))
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Invalid JSON"}), 400
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
        data = request.get_json()
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