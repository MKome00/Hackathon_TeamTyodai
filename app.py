from flask import Flask, render_template  # Flask本体を作るためのFlaskクラスと、HTMLファイルを表示するためのrender_template関数を読み込む

app = Flask(__name__)  # このPythonファイルをもとにFlaskアプリを作成し、appという変数に保存する


@app.route("/")  # ブラウザでトップページ「/」にアクセスされたときに、直下のindex関数を実行するよう設定する
def index():  # トップページにアクセスされたときに実行されるindex関数を定義する
    return render_template("index.html")  # templatesフォルダ内のindex.htmlを読み込み、ブラウザに表示する


if __name__ == "__main__":  # このapp.pyファイルが直接実行された場合だけ、以下の処理を実行する
    app.run(debug=True)  # Flaskの開発用サーバーをデバッグモードで起動する