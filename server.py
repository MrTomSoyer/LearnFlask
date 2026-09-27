from flask import Flask, session
from views import AdsList, AdsDetail, IndexView

app = Flask(__name__)
app.secret_key = 'fgv'
app.json.ensure_ascii = False
app.add_url_rule('/', view_func=IndexView.as_view('to_ads'), methods=['GET', 'POST'])
app.add_url_rule('/ads', view_func=AdsList.as_view('ads_list'), methods=['GET', 'POST'])
app.add_url_rule('/ads/<int:ads_id>', view_func=AdsDetail.as_view('ads_detail'), methods=['GET', 'PATCH', 'DELETE'])

if __name__ == '__main__':
    app.run()