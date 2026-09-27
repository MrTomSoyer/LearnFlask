from flask import jsonify, request, render_template, redirect, url_for, session
from flask.views import MethodView

from db import Session, Ads


class IndexView(MethodView):
    def get(self):
        return redirect(url_for("ads_list"))


class AdsList(MethodView):
    def get(self):
        with Session() as session:
            ads = session.query(Ads).all()
            return render_template(
                "index.html",
                ads=[ads.dict for ads in ads]
            )

    def post(self):
        json_data = request.json
        if 'title' not in json_data or 'owner' not in json_data:
            response = jsonify({"error": "Missing title and owner"})
            response.status_code = 400
            return response
        with Session() as session:
            ads = Ads(title=json_data.get('title'), owner=json_data.get('owner'))
            session.add(ads)
            session.commit()
            return jsonify(ads.id_dict)


class AdsDetail(MethodView):
    def get(self, ads_id):
        with Session() as session:
            ads = session.get(Ads, ads_id)
            if ads is None:
                response = jsonify({"error": "No ads found"})
                response.status_code = 404
                return response
            return jsonify(ads.dict)

    def patch(self, ads_id):
        json_data = request.json
        with Session() as session:
            ads = session.get(Ads, ads_id)
            if ads is None:
                response = jsonify({"error": "No ads found"})
                response.status_code = 404
                return response
        if 'title' in json_data:
            ads.title = json_data.get('title')
        if 'owner' in json_data:
            ads.owner = json_data.get('owner')
        session.add(ads)
        session.commit()
        return jsonify(ads.dict)

    def delete(self, ads_id):
        with Session() as session:
            ads = session.get(Ads, ads_id)
            if ads is None:
                response = jsonify({"error": "No ads found"})
                response.status_code = 404
                return response
            session.delete(ads)
            session.commit()
            return jsonify({"message": "ads deleted"})