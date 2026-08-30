import os  # ファイル保存先のパス作成やファイル操作を行うためにosモジュールを読み込む

import uuid  # 同じ名前の画像が保存されても重複しない一意なファイル名を作るためにuuidモジュールを読み込む

import sqlite3  # Python標準のSQLiteを操作するためのsqlite3モジュールを読み込む

import random  # ホーム画面のダミー表示データをペットごとに再現性を持って生成するためにrandomモジュールを読み込む

from datetime import date, timedelta  # 記録画面のダミー日付を計算するためにdateとtimedeltaを読み込む

from flask import Flask, render_template, request, redirect, url_for, flash  # Flask本体、HTML表示、フォーム受信、画面移動、URL生成、一時メッセージ表示に必要な機能を読み込む

from werkzeug.utils import secure_filename  # アップロードされたファイル名を安全な形式へ変換する関数を読み込む

app = Flask(__name__)  # このPythonファイルをもとにFlaskアプリを作成する
app.secret_key = "team-tyodai-secret-key"  # flashメッセージを一時的に保存するセッション機能を使うための秘密鍵を設定する

DATABASE = "pets.db"  # ペット情報を保存するSQLiteデータベースのファイル名を設定する

def get_db_connection():  # SQLiteデータベースへ接続するための関数を定義する

    connection = sqlite3.connect(DATABASE)  # pets.dbというSQLiteデータベースへ接続する

    connection.row_factory = sqlite3.Row  # SQLで取得したデータを列名を使って扱えるようにする

    return connection  # 作成したデータベース接続を呼び出し元へ返す

UPLOAD_FOLDER = os.path.join("static", "images", "pets")  # ペット画像を保存するフォルダの場所を設定する

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}  # アップロードを許可する画像ファイルの拡張子を設定する

def allowed_file(filename):  # アップロードされたファイルが許可された画像形式か確認する関数を定義する

    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS  # 拡張子が存在し、許可された形式に含まれている場合だけTrueを返す

def init_db():  # ペット情報を保存するテーブルを準備する関数を定義する

    connection = get_db_connection()  # SQLiteデータベースへ接続する

    connection.execute(  # petsテーブルが存在しない場合に新しく作成するSQLを実行する

        """
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            age INTEGER,
            weight REAL,
            note TEXT,
            photo TEXT
        )
        """  # ペット情報と画像ファイル名を保存できるpetsテーブルを定義する

    )  # petsテーブル作成処理を終了する

    columns = connection.execute("PRAGMA table_info(pets)").fetchall()  # 現在のpetsテーブルに存在する列情報を取得する

    column_names = [column["name"] for column in columns]  # 取得した列情報から列名だけを一覧として取り出す

    if "photo" not in column_names:  # 既存のpetsテーブルにphoto列がまだ存在しない場合

        connection.execute("ALTER TABLE pets ADD COLUMN photo TEXT")  # 既存テーブルに画像ファイル名保存用のphoto列を追加する

    connection.commit()  # テーブル作成や列追加の変更内容をSQLiteへ確定する

    connection.close()  # データベースとの接続を終了する

TASK_POOL = [  # ホーム画面の「今日のやること」に使うダミーの予定候補一覧を用意する

    {"icon": "🏥", "label": "通院"},
    {"icon": "💊", "label": "お薬"},
    {"icon": "✂️", "label": "トリミング予約"},
    {"icon": "🛒", "label": "フードの買い足し"},
    {"icon": "🧴", "label": "トイレ用品の補充"},

]  # 「今日のやること」ダミー候補の定義を終了する

SCHEDULE_POOL = [  # ホーム画面の「次の予定」に使うダミーの予定候補一覧を用意する

    "予防接種",
    "健康診断",
    "トリミング",

]  # 「次の予定」ダミー候補の定義を終了する

FOOD_BAR_MAX_DAYS = 30  # フード残量バーが満タン表示になる日数のしきい値を設定する

FOOD_DANGER_DAYS = 10  # この日数を切ったらフード残量バーを赤色にするしきい値を設定する

FOOD_WARNING_DAYS = 20  # この日数を切ったらフード残量バーを黄色にするしきい値を設定する

def build_home_dummy_data(pet):  # ペット1匹分のホーム画面用ダミー情報を組み立てる関数を定義する

    rng = random.Random(pet["id"])  # ペットIDを種にして、同じペットなら毎回同じダミー内容になるようにする

    today_tasks = rng.sample(TASK_POOL, k=rng.randint(0, 2))  # 「今日のやること」候補からランダムに0〜2件を選ぶ

    food_days_left = rng.randint(1, 35)  # フードがなくなるまでの残り日数をダミーで決める(満タン表示になるケースも試せるよう30日を超える値も含める)

    food_percent = min(round(food_days_left / FOOD_BAR_MAX_DAYS * 100), 100)  # 残り日数をもとにバーの表示割合を計算し、実際の日数と矛盾しないようにする

    if food_days_left < FOOD_DANGER_DAYS:  # 残り日数がしきい値を切って少ない場合

        food_level = "danger"  # フード残量バーを赤色にする

    elif food_days_left < FOOD_WARNING_DAYS:  # 残り日数がまだ危険域ではないが少なめの場合

        food_level = "warning"  # フード残量バーを黄色にする

    else:  # 残り日数に十分な余裕がある場合

        food_level = "safe"  # フード残量バーを青色にする

    next_schedule_label = rng.choice(SCHEDULE_POOL)  # 次に控えている予定の種類をダミーで決める

    next_schedule_days = rng.randint(1, 30)  # 次の予定までの残り日数をダミーで決める

    weight_diff = round(rng.uniform(-0.3, 0.3), 1)  # 前回記録からの体重の増減をダミーで決める

    return {  # 組み立てたダミー情報をまとめて返す

        "pet": pet,  # 表示対象のペット情報
        "today_tasks": today_tasks,  # 今日のやることリスト
        "food_days_left": food_days_left,  # フードが残っている日数
        "food_percent": food_percent,  # フードの残量バーの表示割合(0〜100)
        "food_max_days": FOOD_BAR_MAX_DAYS,  # フード残量バーが満タンとして扱う日数
        "food_level": food_level,  # フード残量バーの色分け("danger" / "warning" / "safe")
        "next_schedule_label": next_schedule_label,  # 次の予定の種類
        "next_schedule_days": next_schedule_days,  # 次の予定までの残り日数
        "next_schedule_urgent": next_schedule_days <= 3,  # 次の予定が近く目立たせるべきかどうか
        "weight_diff": weight_diff,  # 前回からの体重の増減

    }  # ペット1匹分のダミー情報組み立てを終了する

RECORD_TYPE_POOL = [  # 記録画面の通院・健康履歴に使うダミーの種類一覧を用意する

    {"icon": "⚖️", "label": "体重"},
    {"icon": "💉", "label": "予防接種"},
    {"icon": "🩺", "label": "健康診断"},
    {"icon": "🏥", "label": "通院"},
    {"icon": "💊", "label": "お薬"},

]  # 記録の種類ダミー候補の定義を終了する

RECORD_DETAIL_POOL = {  # 記録の種類ごとに使うダミーの詳細文言を用意する

    "体重": ["定期測定", "健康診断時に測定", "自宅で測定"],
    "予防接種": ["混合ワクチン接種", "狂犬病ワクチン接種", "ノミ・マダニ予防接種"],
    "健康診断": ["異常なし", "経過観察", "血液検査を実施"],
    "通院": ["皮膚のかゆみで受診", "嘔吐のため受診", "定期健診で来院", "怪我の治療で来院"],
    "お薬": ["抗生剤を処方", "痒み止めを処方", "整腸剤を処方"],

}  # 記録の詳細ダミー候補の定義を終了する

def build_pet_records(pet):  # 選択中のペット1匹分の健康・通院履歴ダミーデータを組み立てる関数を定義する

    rng = random.Random(pet["id"] * 31 + 7)  # ホーム画面のダミーと重複しない乱数の流れになるよう、ペットIDから別の種を作る

    record_count = rng.randint(4, 7)  # 表示する記録の件数をダミーで決める

    today = date.today()  # 今日の日付を基準に過去の記録日を計算する

    records = []  # 組み立てた記録を1件ずつ追加していくリストを用意する

    for _ in range(record_count):  # 決めた件数だけ記録を1件ずつ作成する

        record_type = rng.choice(RECORD_TYPE_POOL)  # 記録の種類(体重・通院など)をダミーで選ぶ

        detail = rng.choice(RECORD_DETAIL_POOL[record_type["label"]])  # 選んだ種類に合った詳細文言をダミーで選ぶ

        record_date = today - timedelta(days=rng.randint(1, 180))  # 過去180日以内のどこかの日付をダミーで決める

        weight_value = None  # 体重の記録でない場合は体重の値を持たせない

        if record_type["label"] == "体重":  # 体重の記録だった場合

            base_weight = pet["weight"] if pet["weight"] is not None else 5.0  # 登録済みの体重を基準にし、未登録なら5.0kgを仮の基準にする

            weight_value = round(base_weight + rng.uniform(-0.5, 0.5), 1)  # 基準の体重から前後0.5kgほど変動させたダミー値を作る

        records.append({  # 1件分の記録をリストへ追加する

            "date": record_date,  # 記録した日付
            "icon": record_type["icon"],  # 記録の種類を表す絵文字
            "label": record_type["label"],  # 記録の種類名
            "detail": detail,  # 記録の詳細文言
            "weight_value": weight_value,  # 体重の記録の場合だけ入る具体的な数値

        })  # 1件分の記録追加を終了する

    records.sort(key=lambda record: record["date"], reverse=True)  # 新しい記録が上に来るよう日付の新しい順に並べ替える

    return records  # 組み立てた記録一覧を返す

@app.route("/")  # ルートURL「/」にアクセスされたときの処理を指定する
@app.route("/home")  # 「/home」にアクセスされたときも同じホーム画面を表示する
def home():  # ホーム画面を表示する関数を定義する

    connection = get_db_connection()  # 登録済みのペット情報を取得するためSQLiteへ接続する

    pet_list = connection.execute(  # petsテーブルから登録されているすべてのペットを取得する

        """
        SELECT id, name, type, age, weight, note, photo
        FROM pets
        ORDER BY id
        """  # 登録された順番でペット情報を取得するSQLを書く

    ).fetchall()  # SQLの検索結果をすべて取得する

    connection.close()  # ペット情報を取得し終わったのでSQLiteとの接続を終了する

    home_pets = [build_home_dummy_data(pet) for pet in pet_list]  # 登録済みペットごとに表示用のダミー情報を組み立てる

    return render_template("home.html", home_pets=home_pets)  # templatesフォルダ内のhome.htmlへペットごとの表示データを渡す

@app.route("/pets", methods=["GET", "POST"])  # ペットページで画面表示のGETと保存処理のPOSTを受け付ける
def pets():  # ペット画面の表示、新規登録、既存情報の更新を行う関数を定義する

    if request.method == "POST":  # 「保存する」ボタンからPOSTでデータが送信された場合だけ以下を実行する

        pet_id = request.form.get("pet_id")  # フォームから現在編集中のペットIDを取得する

        name = request.form.get("name", "").strip()  # 名前を取得し、前後に入力された余分な空白を削除する

        pet_type = request.form.get("type", "").strip()  # 種類を取得し、前後の余分な空白を削除する

        age_text = request.form.get("age", "").strip()  # 年齢をまず文字列として取得する

        weight_text = request.form.get("weight", "").strip()  # 体重をまず文字列として取得する

        note = request.form.get("note", "").strip()  # その他の基本情報を取得し、前後の余分な空白を削除する

        photo = request.files.get("photo")  # フォームから送信されたペット写真ファイルを取得する

        photo_filename = None  # 新しい画像が送信されなかった場合に備えて画像ファイル名を空の状態にする

        error_message = None  # 入力内容に問題があった場合のエラーメッセージを保存する変数を用意する

        if not name:  # 名前が空欄の場合

            error_message = "ペットの名前を入力してください。"  # 名前が必要であることをエラーメッセージとして設定する

        elif len(name) > 30:  # 名前が30文字を超えている場合

            error_message = "ペットの名前は30文字以内で入力してください。"  # 名前の文字数制限を知らせる

        elif len(pet_type) > 50:  # 種類が50文字を超えている場合

            error_message = "ペットの種類は50文字以内で入力してください。"  # 種類の文字数制限を知らせる

        elif len(note) > 500:  # その他の基本情報が500文字を超えている場合

            error_message = "その他の基本情報は500文字以内で入力してください。"  # その他情報の文字数制限を知らせる

        age = None  # 年齢が未入力の場合はデータベースへNULLとして保存するためNoneを初期値にする

        if not error_message and age_text:  # ここまでエラーがなく、年齢が入力されている場合

            try:  # 年齢を整数へ変換できるか確認する

                age = int(age_text)  # 入力された年齢を整数へ変換する

            except ValueError:  # 整数へ変換できない値が入力されていた場合

                error_message = "年齢は整数で入力してください。"  # 年齢の入力形式が不正であることを知らせる

            if error_message is None and (age < 0 or age > 100):  # 変換できた年齢が許可範囲外だった場合

                error_message = "年齢は0歳以上100歳以下で入力してください。"  # 年齢の範囲を知らせる

        weight = None  # 体重が未入力の場合はデータベースへNULLとして保存するためNoneを初期値にする

        if not error_message and weight_text:  # ここまでエラーがなく、体重が入力されている場合

            try:  # 体重を小数へ変換できるか確認する

                weight = float(weight_text)  # 入力された体重を小数へ変換する

            except ValueError:  # 小数へ変換できない値が入力されていた場合

                error_message = "体重は数値で入力してください。"  # 体重の入力形式が不正であることを知らせる

            if error_message is None and (weight < 0 or weight > 500):  # 変換できた体重が許可範囲外だった場合

                error_message = "体重は0kg以上500kg以下で入力してください。"  # 体重の範囲を知らせる

        if error_message:  # 入力内容に何らかのエラーが存在する場合

            connection = get_db_connection()  # ペット一覧を再表示するためSQLiteへ接続する

            pet_list = connection.execute(  # 登録済みのペットをすべて取得する

                """
                SELECT id, name, type, age, weight, note, photo
                FROM pets
                ORDER BY id
                """  # ペット一覧を登録順に取得するSQLを書く

            ).fetchall()  # SQLの検索結果をすべて取得する

            selected_pet = None  # 新規登録の場合に備えて、選択中ペットを一度空にする

            if pet_id:  # 既存ペットの編集中だった場合

                selected_pet = connection.execute(  # 編集していたペット情報をもう一度取得する

                    """
                    SELECT id, name, type, age, weight, note, photo
                    FROM pets
                    WHERE id = ?
                    """,  # 編集対象のペット1匹を取得するSQLを書く

                    (pet_id,)  # フォームから送られたペットIDをSQLへ渡す

                ).fetchone()  # 条件に一致するペット1匹分を取得する

            connection.close()  # SQLiteとの接続を終了する

            return render_template(
                "pets.html",  # ペットページを再表示する
                pets=pet_list,  # 登録済みペット一覧をHTMLへ渡す
                selected_pet=selected_pet,  # 編集中だったペット情報をHTMLへ渡す
                error_message=error_message  # 入力エラーメッセージをHTMLへ渡す
            )  # DBへの保存処理は行わず、ペットページへ戻る

        connection = get_db_connection()  # SQLiteへ接続する

        if photo and photo.filename and allowed_file(photo.filename):  # 画像が選択されていて、許可された拡張子の場合だけ保存処理を行う

            original_filename = secure_filename(photo.filename)  # アップロードされた元のファイル名を安全な形式に変換する

            extension = original_filename.rsplit(".", 1)[1].lower()  # ファイル名から拡張子部分だけを取得する

            photo_filename = f"{uuid.uuid4().hex}.{extension}"  # 他の画像と名前が重複しないようランダムな一意のファイル名を作る

            save_path = os.path.join(UPLOAD_FOLDER, photo_filename)  # 実際に画像を保存するファイルパスを作成する

            photo.save(save_path)  # アップロードされた画像をstatic/images/petsフォルダへ保存する

        if pet_id:  # ペットIDが存在する場合は既存ペットの更新処理を行う

            if photo_filename:  # 新しい画像がアップロードされた場合

                connection.execute(  # プロフィール情報と新しい画像ファイル名をまとめて更新する

                    """
                    UPDATE pets
                    SET name = ?, type = ?, age = ?, weight = ?, note = ?, photo = ?
                    WHERE id = ?
                    """,  # 指定されたIDのペット情報と写真を更新するSQLを書く

                    (name, pet_type, age, weight, note, photo_filename, pet_id)  # 更新する値と対象ペットIDをSQLへ渡す

                )  # 写真を含むUPDATE処理を終了する

            else:  # 新しい画像が選択されていない場合

                connection.execute(  # 現在の写真は変更せず、文字情報だけを更新する

                    """
                    UPDATE pets
                    SET name = ?, type = ?, age = ?, weight = ?, note = ?
                    WHERE id = ?
                    """,  # 写真列には触れずプロフィール情報だけ更新するSQLを書く

                    (name, pet_type, age, weight, note, pet_id)  # 更新する文字情報と対象ペットIDをSQLへ渡す

                )  # 写真を変更しないUPDATE処理を終了する

        else:  # ペットIDが存在しない場合は新規登録する

            cursor = connection.execute(  # 新しいペット情報をpetsテーブルへ登録し、新しく作られたIDも取得できるようにする

                """
                INSERT INTO pets (name, type, age, weight, note, photo)
                VALUES (?, ?, ?, ?, ?, ?)
                """,  # 新しいペットの基本情報と画像ファイル名を保存するSQLを書く

                (name, pet_type, age, weight, note, photo_filename)  # 入力されたプロフィール情報と画像ファイル名をSQLへ渡す

            )  # INSERT処理を終了する

            pet_id = cursor.lastrowid  # 今追加したペットのIDを取得する

        connection.commit()  # INSERTまたはUPDATEした内容をSQLiteへ確定する

        connection.close()  # SQLiteとの接続を終了する

        flash("ペット情報を保存しました。", "success")  # 保存完了メッセージをsuccessという種類で次の画面表示まで一時保存する
        
        return redirect(url_for("pets", pet_id=pet_id))  # 保存したペットIDをURLへ付けてペットページへ戻る

    connection = get_db_connection()  # 登録済みのペット情報を取得するためSQLiteへ接続する

    pet_list = connection.execute(  # petsテーブルから登録されているすべてのペットを取得する

        """
        SELECT id, name, type, age, weight, note, photo
        FROM pets
        ORDER BY id
        """  # 登録された順番でペット情報を取得するSQLを書く

    ).fetchall()  # SQLの検索結果をすべて取得する

    selected_pet_id = request.args.get("pet_id")  # URLの?pet_id=〇から現在表示するペットIDを取得する

    mode = request.args.get("mode")  # 新規ペット追加画面かどうかを判定するためURLのmodeを取得する

    selected_pet = None  # 最初は選択中のペットが存在しない状態にしておく

    if mode != "new":  # 「ペットを追加」から開いた新規登録画面ではない場合

        if selected_pet_id:  # URLにペットIDが指定されている場合

            selected_pet = connection.execute(  # 指定されたIDのペット情報を取得する

                """
                SELECT id, name, type, age, weight, note, photo
                FROM pets
                WHERE id = ?
                """,  # URLで指定されたペット1匹を取得するSQLを書く

                (selected_pet_id,)  # URLから取得したペットIDをSQLへ渡す

            ).fetchone()  # 条件に一致したペット1匹分を取得する

        else:  # URLにpet_idが指定されていない場合

            selected_pet = connection.execute(  # 登録されている中で最もIDが小さいペットを取得する

                """
                SELECT id, name, type, age, weight, note, photo
                FROM pets
                ORDER BY id ASC
                LIMIT 1
                """  # IDの小さい順に並べ、最初の1匹だけ取得するSQLを書く

            ).fetchone()  # 最初のペット1匹分を取得する

    connection.close()  # ペット情報を取得し終わったのでSQLiteとの接続を終了する

    return render_template(
        "pets.html",  # pets.htmlを表示する
        pets=pet_list,  # 登録済みペット一覧をHTMLへ渡す
        selected_pet=selected_pet  # 現在選択されているペット情報をHTMLへ渡す
    )  # HTML表示処理を終了する

@app.route("/pets/delete/<int:pet_id>", methods=["POST"])  # 指定されたIDのペットを削除するPOST専用URLを設定する
def delete_pet(pet_id):  # ペット削除処理を行う関数を定義する

    connection = get_db_connection()  # 削除するペット情報を取得するためSQLiteへ接続する

    pet = connection.execute(  # 指定されたIDのペット情報をデータベースから取得する

        """
        SELECT id, photo
        FROM pets
        WHERE id = ?
        """,  # 削除対象ペットのIDと写真ファイル名だけを取得するSQLを書く

        (pet_id,)  # URLから受け取ったペットIDをSQLの「?」へ渡す

    ).fetchone()  # 条件に一致したペット1匹分の情報を取得する

    previous_pet = None  # 削除対象より前のペット情報を保存する変数を用意する

    next_pet = None  # 削除対象より後のペット情報を保存する変数を用意する

    if pet:  # 指定されたIDのペットが実際に存在する場合だけ削除処理を行う

        previous_pet = connection.execute(  # 削除するペットよりIDが小さい中で最も近いペットを探す

            """
            SELECT id
            FROM pets
            WHERE id < ?
            ORDER BY id DESC
            LIMIT 1
            """,  # 削除対象より小さいIDを大きい順に並べ、最初の1匹だけ取得する

            (pet_id,)  # 削除するペットIDをSQLへ渡す

        ).fetchone()  # 条件に一致する直前のペットを取得する

        if previous_pet is None:  # 削除するペットより前のペットが存在しない場合

            next_pet = connection.execute(  # 削除するペットよりIDが大きい中で最も近いペットを探す

                """
                SELECT id
                FROM pets
                WHERE id > ?
                ORDER BY id ASC
                LIMIT 1
                """,  # 削除対象より大きいIDを小さい順に並べ、最初の1匹だけ取得する

                (pet_id,)  # 削除するペットIDをSQLへ渡す

            ).fetchone()  # 条件に一致する次のペットを取得する

        if pet["photo"]:  # 削除するペットにプロフィール写真が登録されている場合

            photo_path = os.path.join(UPLOAD_FOLDER, pet["photo"])  # 保存されている写真ファイルの場所を作成する

            if os.path.exists(photo_path):  # 実際に写真ファイルが存在する場合

                os.remove(photo_path)  # static/images/pets内の写真ファイルを削除する

        connection.execute(  # petsテーブルから指定されたペットを削除する

            """
            DELETE FROM pets
            WHERE id = ?
            """,  # 指定されたIDのペットだけを削除するSQLを書く

            (pet_id,)  # 削除対象のペットIDをSQLへ渡す

        )  # DELETE処理を終了する

        connection.commit()  # ペット削除の変更内容をSQLiteへ正式に保存する

        flash("ペットを削除しました。", "success")  # 削除完了メッセージを一時保存する

    connection.close()  # SQLiteとの接続を終了する

    if previous_pet:  # 削除したペットより前に別のペットが存在した場合

        return redirect(url_for("pets", pet_id=previous_pet["id"]))  # 直前のペットを表示する

    if next_pet:  # 前のペットが存在せず、後ろに別のペットが存在した場合

        return redirect(url_for("pets", pet_id=next_pet["id"]))  # 直後のペットを表示する

    return redirect(url_for("pets", mode="new"))  # ペットが1匹も残っていない場合は新規登録画面を表示する

@app.route("/calendar")  # 「/calendar」にアクセスされたときの処理を指定する
def calendar():  # カレンダー画面を表示する関数を定義する

    return render_template("calendar.html")  # templatesフォルダ内のcalendar.htmlを表示する

@app.route("/records")  # 「/records」にアクセスされたときの処理を指定する
def records():  # 記録画面を表示する関数を定義する

    connection = get_db_connection()  # 登録済みのペット情報を取得するためSQLiteへ接続する

    pet_list = connection.execute(  # petsテーブルから登録されているすべてのペットを取得する

        """
        SELECT id, name, type, age, weight, note, photo
        FROM pets
        ORDER BY id
        """  # 登録された順番でペット情報を取得するSQLを書く

    ).fetchall()  # SQLの検索結果をすべて取得する

    selected_pet_id = request.args.get("pet_id")  # URLの?pet_id=〇から現在表示するペットIDを取得する

    selected_pet = None  # 最初は選択中のペットが存在しない状態にしておく

    if selected_pet_id:  # URLにペットIDが指定されている場合

        selected_pet = connection.execute(  # 指定されたIDのペット情報を取得する

            """
            SELECT id, name, type, age, weight, note, photo
            FROM pets
            WHERE id = ?
            """,  # URLで指定されたペット1匹を取得するSQLを書く

            (selected_pet_id,)  # URLから取得したペットIDをSQLへ渡す

        ).fetchone()  # 条件に一致したペット1匹分を取得する

    elif pet_list:  # URLにpet_idが指定されておらず、ペットが1匹以上登録されている場合

        selected_pet = connection.execute(  # 登録されている中で最もIDが小さいペットを取得する

            """
            SELECT id, name, type, age, weight, note, photo
            FROM pets
            ORDER BY id ASC
            LIMIT 1
            """  # IDの小さい順に並べ、最初の1匹だけ取得するSQLを書く

        ).fetchone()  # 最初のペット1匹分を取得する

    connection.close()  # ペット情報を取得し終わったのでSQLiteとの接続を終了する

    pet_records = build_pet_records(selected_pet) if selected_pet else []  # 選択中のペットがいる場合だけ健康・通院履歴のダミーデータを組み立てる

    return render_template(
        "records.html",  # templatesフォルダ内のrecords.htmlを表示する
        pets=pet_list,  # 登録済みペット一覧をHTMLへ渡す
        selected_pet=selected_pet,  # 現在選択されているペット情報をHTMLへ渡す
        pet_records=pet_records  # 選択中のペットの健康・通院履歴をHTMLへ渡す
    )  # HTML表示処理を終了する

@app.route("/reservation")  # 「/reservation」にアクセスされたときの処理を指定する
def reservation():  # 予約画面を表示する関数を定義する

    return render_template("reservation.html")  # templatesフォルダ内のreservation.htmlを表示する

if __name__ == "__main__":  # このapp.pyが直接実行された場合だけ以下を実行する

    init_db()  # Flaskを起動する前にpetsテーブルが存在することを確認する

    app.run(debug=True)  # Flaskの開発用サーバーをデバッグモードで起動する