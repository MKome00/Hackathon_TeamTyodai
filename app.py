from flask import Flask, render_template  # Flask本体を作るFlaskクラスと、HTMLを表示するrender_template関数を読み込む

app = Flask(__name__)  # このPythonファイルをもとにFlaskアプリを作成する


@app.route("/")  # ルートURL「/」にアクセスされたときの処理を指定する
@app.route("/home")  # 「/home」にアクセスされたときも同じ処理を実行する
def home():  # ホーム画面を表示する関数を定義する
    return render_template("home.html")  # templatesフォルダ内のhome.htmlを表示する


@app.route("/pets")  # 「/pets」にアクセスされたときの処理を指定する
def pets():  # ペット画面を表示する関数を定義する
    return render_template("pets.html")  # templatesフォルダ内のpets.htmlを表示する


@app.route("/schedule")  # 「/schedule」にアクセスされたときの処理を指定する
def schedule():  # 予定画面を表示する関数を定義する
    return render_template("schedule.html")  # templatesフォルダ内のschedule.htmlを表示する


@app.route("/records")  # 「/records」にアクセスされたときの処理を指定する
def records():  # 記録画面を表示する関数を定義する
    return render_template("records.html")  # templatesフォルダ内のrecords.htmlを表示する


@app.route("/mypage")  # 「/mypage」にアクセスされたときの処理を指定する
def mypage():  # マイページを表示する関数を定義する
    return render_template("mypage.html")  # templatesフォルダ内のmypage.htmlを表示する


if __name__ == "__main__":  # このapp.pyが直接実行された場合だけ、以下の処理を実行する
    app.run(debug=True)  # Flaskの開発用サーバーをデバッグモードで起動する