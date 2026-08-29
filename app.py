from flask import Flask, render_template  # Flask本体を作るFlaskクラスと、HTMLを表示するrender_template関数を読み込む

app = Flask(__name__)  # このPythonファイルをもとにFlaskアプリを作成する

@app.route("/")  # ルートURL「/」にアクセスされたときの処理を指定する
@app.route("/home")  # 「/home」にアクセスされたときも同じホーム画面を表示する
def home():  # ホーム画面を表示するhome関数を定義する
    return render_template("home.html")  # templatesフォルダ内のhome.htmlを表示する

@app.route("/reservation")  # 「/reservation」にアクセスされたときの処理を指定する
def reservation():  # 病院やトリミングなどの予約画面を表示するreservation関数を定義する
    return render_template("reservation.html")  # templatesフォルダ内のreservation.htmlを表示する

@app.route("/calendar")  # 「/calendar」にアクセスされたときの処理を指定する
def calendar():  # 予防接種や薬などの予定を確認するカレンダー画面を表示する関数を定義する
    return render_template("calendar.html")  # templatesフォルダ内のcalendar.htmlを表示する

@app.route("/records")  # 「/records」にアクセスされたときの処理を指定する
def records():  # 健康記録や通院履歴を表示するrecords関数を定義する
    return render_template("records.html")  # templatesフォルダ内のrecords.htmlを表示する

@app.route("/pets")  # 「/pets」にアクセスされたときの処理を指定する
def pets():  # 自分のペット情報を表示するpets関数を定義する
    return render_template("pets.html")  # templatesフォルダ内のpets.htmlを表示する

if __name__ == "__main__":  # このapp.pyが直接実行された場合だけ以下の処理を実行する
    app.run(debug=True)  # Flaskの開発用サーバーをデバッグモードで起動する