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

    connection.execute(  # recordsテーブルが存在しない場合に新しく作成するSQLを実行する

        """
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            detail TEXT,
            weight_value REAL,
            record_date TEXT NOT NULL,
            FOREIGN KEY (pet_id) REFERENCES pets (id)
        )
        """  # ペットごとの健康・通院記録を保存できるrecordsテーブルを定義する

    )  # recordsテーブル作成処理を終了する

    connection.execute(  # calendar_eventsテーブルが存在しない場合に新しく作成する

        """
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            event_date TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            note TEXT,
            FOREIGN KEY (pet_id) REFERENCES pets (id)
        )
        """  # ペットごとの病院・トリミングなどの予定を保存するテーブルを定義する

    )  # calendar_eventsテーブル作成処理を終了する

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

RECORD_TYPE_ICONS = {record_type["label"]: record_type["icon"] for record_type in RECORD_TYPE_POOL}  # 種類名から絵文字を引けるようにしておく

def fetch_pet_records(pet_id):  # 選択中のペット1匹分の健康・通院履歴をrecordsテーブルから取得する関数を定義する

    connection = get_db_connection()  # recordsテーブルを読み取るためSQLiteへ接続する

    rows = connection.execute(  # 指定されたペットの記録を新しい順に取得する

        """
        SELECT id, type, detail, weight_value, record_date
        FROM records
        WHERE pet_id = ?
        ORDER BY record_date DESC, id DESC
        """,  # 記録日の新しい順(同じ日付ならID順)に並べて取得するSQLを書く

        (pet_id,)  # 対象のペットIDをSQLへ渡す

    ).fetchall()  # SQLの検索結果をすべて取得する

    connection.close()  # SQLiteとの接続を終了する

    records = []  # DBの行を表示用の形へ組み立てて追加していくリストを用意する

    for row in rows:  # 取得した記録を1件ずつ処理する

        records.append({  # 1件分の記録を表示用の形へ変換してリストへ追加する

            "id": row["id"],  # 記録のID
            "date": date.fromisoformat(row["record_date"]),  # 保存されている日付の文字列をdate型に変換する
            "icon": RECORD_TYPE_ICONS.get(row["type"], "📝"),  # 種類名に対応する絵文字(未知の種類なら📝)
            "label": row["type"],  # 記録の種類名
            "detail": row["detail"],  # 記録の詳細文言
            "weight_value": row["weight_value"],  # 体重の記録の場合だけ入る具体的な数値

        })  # 1件分の記録変換の追加を終了する

    return records  # 組み立てた記録一覧を返す

def fetch_all_records():  # 登録されているすべてのペットの健康・通院履歴をペット名付きでrecordsテーブルから取得する関数を定義する

    connection = get_db_connection()  # recordsテーブルとpetsテーブルを読み取るためSQLiteへ接続する

    rows = connection.execute(  # すべてのペットの記録を、どのペットのものかも含めて新しい順に取得する

        """
        SELECT records.id, records.pet_id, pets.name AS pet_name, records.type, records.detail, records.weight_value, records.record_date
        FROM records
        JOIN pets ON pets.id = records.pet_id
        ORDER BY records.record_date DESC, records.id DESC
        """,  # recordsテーブルとpetsテーブルを結びつけ、記録日の新しい順に取得するSQLを書く

    ).fetchall()  # SQLの検索結果をすべて取得する

    connection.close()  # SQLiteとの接続を終了する

    records = []  # DBの行を表示用の形へ組み立てて追加していくリストを用意する

    for row in rows:  # 取得した記録を1件ずつ処理する

        records.append({  # 1件分の記録を表示用の形へ変換してリストへ追加する

            "id": row["id"],  # 記録のID
            "pet_id": row["pet_id"],  # この記録がどのペットのものかを表すID
            "pet_name": row["pet_name"],  # この記録がどのペットのものかを表す名前
            "date": date.fromisoformat(row["record_date"]),  # 保存されている日付の文字列をdate型に変換する
            "icon": RECORD_TYPE_ICONS.get(row["type"], "📝"),  # 種類名に対応する絵文字(未知の種類なら📝)
            "label": row["type"],  # 記録の種類名
            "detail": row["detail"],  # 記録の詳細文言
            "weight_value": row["weight_value"],  # 体重の記録の場合だけ入る具体的な数値

        })  # 1件分の記録変換の追加を終了する

    return records  # 組み立てた記録一覧を返す

RECORD_GROUP_PREVIEW_COUNT = 5  # 項目ごとのまとめカードに常に表示する最新件数を設定する

def group_records_by_type(records):  # 時系列の記録一覧を種類ごとにまとめ直す関数を定義する

    groups = []  # 種類ごとにまとめた結果を追加していくリストを用意する

    for record_type in RECORD_TYPE_POOL:  # 体重・予防接種・健康診断・通院・お薬の順に処理する

        matching_records = [  # この種類に該当する記録だけを抜き出す

            record for record in records if record["label"] == record_type["label"]

        ]  # 該当する記録の抜き出しを終了する

        if not matching_records:  # この種類の記録が1件も無い場合

            continue  # まとめカードを作らずに次の種類へ進む

        groups.append({  # 1種類分のまとめ情報をリストへ追加する

            "label": record_type["label"],  # 種類名
            "icon": record_type["icon"],  # 種類を表す絵文字
            "count": len(matching_records),  # この種類の記録の総件数
            "preview": matching_records[:RECORD_GROUP_PREVIEW_COUNT],  # 常に表示する最新分の記録
            "rest": matching_records[RECORD_GROUP_PREVIEW_COUNT:],  # 「すべて見る」を開いたときだけ表示する残りの記録

        })  # 1種類分のまとめ追加を終了する

    return groups  # 種類ごとにまとめた結果を返す

def group_records_by_pet(records, pets):  # 全ペット分の記録一覧をペットごとにまとめ直す関数を定義する

    groups = []  # ペットごとにまとめた結果を追加していくリストを用意する

    for pet in pets:  # 登録順(ID順)にペットを1匹ずつ処理する

        matching_records = [  # このペットに該当する記録だけを抜き出す

            record for record in records if record["pet_id"] == pet["id"]

        ]  # 該当する記録の抜き出しを終了する

        if not matching_records:  # このペットの記録が1件も無い場合

            continue  # まとめカードを作らずに次のペットへ進む

        groups.append({  # 1匹分のまとめ情報をリストへ追加する

            "pet": pet,  # まとめ対象のペット情報
            "count": len(matching_records),  # このペットの記録の総件数
            "preview": matching_records[:RECORD_GROUP_PREVIEW_COUNT],  # 常に表示する最新分の記録
            "rest": matching_records[RECORD_GROUP_PREVIEW_COUNT:],  # 「すべて見る」を開いたときだけ表示する残りの記録

        })  # 1匹分のまとめ追加を終了する

    return groups  # ペットごとにまとめた結果を返す

SCHEDULE_EVENT_TYPES = ["予防接種", "健康診断", "通院", "お薬"]  # カレンダー予定のうち、記録との突き合わせ対象にする種類を用意する(体重は予定として扱わない)

def build_dummy_schedule(pet):  # カレンダー機能が無いあいだ代わりに使う、ペット1匹分のダミー予定を組み立てる関数を定義する

    rng = random.Random(pet["id"] * 53 + 11)  # ホーム画面・記録のダミーと重複しない乱数の流れになるよう、ペットIDから別の種を作る

    event_count = rng.randint(1, 3)  # 予定の件数をダミーで決める

    today = date.today()  # 今日の日付を基準に予定日を計算する

    events = []  # 組み立てた予定を1件ずつ追加していくリストを用意する

    for _ in range(event_count):  # 決めた件数だけ予定を1件ずつ作成する

        events.append({  # 1件分の予定をリストへ追加する

            "type": rng.choice(SCHEDULE_EVENT_TYPES),  # 予定の種類をダミーで選ぶ
            "date": today + timedelta(days=rng.randint(-20, 20)),  # 過去20日〜未来20日のどこかをダミーの予定日にする(過去日は「過ぎた予定」を試すため)

        })  # 1件分の予定追加を終了する

    return events  # 組み立てた予定一覧を返す

def build_record_reminders(pet, pet_records):  # 予定日を過ぎても記録が無いものを探し、リマインダー一覧を組み立てる関数を定義する

    today = date.today()  # 「予定日を過ぎているか」を判定する基準の日付を取得する

    reminders = []  # 記録を促す必要がある予定を追加していくリストを用意する

    for event in build_dummy_schedule(pet):  # ダミーの予定を1件ずつ確認する

        if event["date"] >= today:  # 予定日がまだ来ていない、または今日の場合

            continue  # 記録を促す必要はまだ無いので次の予定へ進む

        has_matching_record = any(  # 予定日以降に、同じ種類の記録がすでに登録されているか確認する

            record["label"] == event["type"] and record["date"] >= event["date"]

            for record in pet_records

        )  # 一致する記録があるかどうかの確認を終了する

        if not has_matching_record:  # 予定日を過ぎているのに対応する記録がまだ無い場合

            reminders.append(event)  # この予定をリマインダーとして追加する

    reminders.sort(key=lambda event: event["date"])  # 予定日が古い(=より過ぎている)ものから並べる

    return reminders  # 組み立てたリマインダー一覧を返す

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

    home_pets = []  # ホーム画面に表示するペットごとの情報を追加していくリストを用意する

    for pet in pet_list:  # 登録済みペットを1匹ずつ処理する

        home_pet = build_home_dummy_data(pet)  # 今日のやること・フード残量などの表示用ダミー情報を組み立てる

        home_pet["record_reminders"] = build_record_reminders(pet, fetch_pet_records(pet["id"]))  # 予定日を過ぎても記録が無い項目のリマインダーを組み立てて追加する

        home_pets.append(home_pet)  # 組み立てた1匹分の情報をリストへ追加する

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

@app.route("/calendar", methods=["GET", "POST"])  # カレンダー画面の表示と予定保存の両方を受け付ける
def calendar():  # カレンダー画面の表示と予定追加を行う関数を定義する

    if request.method == "POST":  # 予定追加フォームからPOSTで送信された場合

        pet_id = request.form.get("pet_id")  # 予定対象として選択されたペットIDを取得する

        category = request.form.get("category", "").strip()  # 病院・トリミング・その他の予定種類を取得する

        event_date_text = request.form.get("event_date", "").strip()  # 予定日を文字列として取得する

        start_time = request.form.get("start_time", "").strip()  # 開始時間を取得する

        end_time = request.form.get("end_time", "").strip()  # 終了時間を取得する

        note = request.form.get("note", "").strip()  # 詳細メモを取得し、前後の余分な空白を削除する


        error_message = None  # 入力内容に問題がある場合のエラーメッセージを保存する変数を用意する


        allowed_categories = [  # カレンダーで登録可能な予定種類を定義する

            "hospital",  # 病院

            "trimming",  # トリミング

            "other"  # その他

        ]  # 予定種類一覧の定義を終了する


        if not pet_id:  # ペットが選択されていない場合

            error_message = "予定を登録するペットを選択してください。"  # ペット選択を促す


        elif category not in allowed_categories:  # 予定種類が未選択または不正な値の場合

            error_message = "予定の種類を選択してください。"  # 予定種類の選択を促す


        elif not event_date_text:  # 予定日が入力されていない場合

            error_message = "予定の日付を選択してください。"  # 日付入力を促す


        elif len(note) > 500:  # 詳細メモが500文字を超えている場合

            error_message = "詳細メモは500文字以内で入力してください。"  # メモの文字数制限を知らせる


        event_date = None  # 正しく変換できた予定日を保存する変数を用意する


        if not error_message:  # ここまで入力エラーがない場合

            try:  # 日付をPythonの日付型へ変換できるか確認する

                event_date = date.fromisoformat(event_date_text)  # YYYY-MM-DD形式の文字列をdate型へ変換する

            except ValueError:  # 日付として解釈できなかった場合

                error_message = "予定の日付を正しく選択してください。"  # 日付入力が不正であることを知らせる


        if not error_message and start_time and end_time:  # 開始時間と終了時間の両方が入力されている場合

            if end_time <= start_time:  # 終了時間が開始時間以前になっている場合

                error_message = "終了時間は開始時間より後にしてください。"  # 時間の順序が不正であることを知らせる


        if not error_message:  # ここまで入力エラーがない場合

            connection = get_db_connection()  # ペットIDが実際に存在するか確認するためSQLiteへ接続する


            pet = connection.execute(  # 選択されたペットIDに一致するペットを取得する

                """
                SELECT id
                FROM pets
                WHERE id = ?
                """,  # 指定されたIDのペットが存在するか確認するSQLを書く

                (pet_id,)  # フォームから送られたペットIDをSQLへ渡す

            ).fetchone()  # 条件に一致するペットを1件取得する


            connection.close()  # ペット存在確認が終わったのでSQLiteとの接続を終了する


            if pet is None:  # 指定されたペットIDがデータベースに存在しなかった場合

                error_message = "選択されたペットが見つかりません。"  # 不正なペットIDであることを知らせる


        if error_message:  # 入力内容にエラーがあった場合

            connection = get_db_connection()  # カレンダー画面を再表示するためSQLiteへ接続する


            pet_list = connection.execute(  # ペット選択欄を再表示するため登録済みペットを取得する

                """
                SELECT id, name
                FROM pets
                ORDER BY id
                """

            ).fetchall()  # 登録済みペットをすべて取得する


            connection.close()  # SQLiteとの接続を終了する


            return render_template(
                "calendar.html",  # カレンダー画面を再表示する
                pets=pet_list,  # 登録済みペット一覧をHTMLへ渡す
                calendar_events=[],  # 入力エラー時はいったん予定表示用データを空にする
                error_message=error_message  # 入力エラーをHTMLへ渡す
            )  # 保存せずカレンダー画面へ戻る


        connection = get_db_connection()  # 新しい予定を保存するためSQLiteへ接続する


        connection.execute(  # 入力された予定をcalendar_eventsテーブルへ登録する

            """
            INSERT INTO calendar_events (
                pet_id,
                category,
                event_date,
                start_time,
                end_time,
                note
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,  # 1件分の予定を保存するSQLを書く

            (
                pet_id,  # 予定対象のペットID
                category,  # 病院・トリミング・その他
                event_date.isoformat(),  # YYYY-MM-DD形式の予定日
                start_time if start_time else None,  # 開始時間が未入力ならNULL
                end_time if end_time else None,  # 終了時間が未入力ならNULL
                note if note else None  # メモが未入力ならNULL
            )

        )  # 予定追加のINSERT処理を終了する


        connection.commit()  # 新しい予定をSQLiteへ正式に保存する

        connection.close()  # SQLiteとの接続を終了する


        flash("予定を保存しました。", "success")  # 保存完了メッセージを次の画面表示まで一時保存する


        return redirect(url_for("calendar"))  # POST後にカレンダー画面へ戻る


    connection = get_db_connection()  # GETでカレンダーを表示するためSQLiteへ接続する


    pet_list = connection.execute(  # 予定追加画面のペット選択欄に表示するペットを取得する

        """
        SELECT id, name
        FROM pets
        ORDER BY id
        """

    ).fetchall()  # 登録済みペットをすべて取得する


    event_rows = connection.execute(  # 保存済み予定とペット名をまとめて取得する

        """
        SELECT
            calendar_events.id,
            calendar_events.pet_id,
            calendar_events.category,
            calendar_events.event_date,
            calendar_events.start_time,
            calendar_events.end_time,
            calendar_events.note,
            pets.name AS pet_name
        FROM calendar_events
        INNER JOIN pets
            ON calendar_events.pet_id = pets.id
        ORDER BY
            calendar_events.event_date ASC,
            calendar_events.start_time ASC
        """

    ).fetchall()  # 保存されている予定をすべて取得する


    connection.close()  # 必要なデータを取得し終わったのでSQLiteとの接続を終了する


    category_labels = {  # データベースに保存している英語値を画面表示用の日本語へ変換する

        "hospital": "病院",

        "trimming": "トリミング",

        "other": "その他"

    }  # 種類名変換表の定義を終了する


    calendar_events = []  # FullCalendarへ渡す予定データを追加していくリストを用意する


    for event in event_rows:  # データベースから取得した予定を1件ずつ処理する

        event_title = f"{event['pet_name']}・{category_labels.get(event['category'], '予定')}"  # カレンダー上に表示する予定名を作る


        if event["start_time"]:  # 開始時間が登録されている場合

            event_start = f"{event['event_date']}T{event['start_time']}"  # 日付と開始時間をFullCalendar用の形式につなげる

        else:  # 開始時間が登録されていない場合

            event_start = event["event_date"]  # 日付だけを開始日時として使用する


        calendar_event = {  # FullCalendarへ渡す1件分の予定データを作る

            "id": event["id"],  # calendar_eventsテーブルの予定ID

            "title": event_title,  # 「ペット名・病院」のような予定名

            "start": event_start,  # 予定の開始日時

            "allDay": not bool(event["start_time"]),  # 開始時間が無い予定は終日予定として扱う

            "extendedProps": {  # FullCalendar標準項目以外の追加情報を保存する

                "petId": event["pet_id"],  # 予定対象のペットID

                "petName": event["pet_name"],  # ペット名

                "category": event["category"],  # 予定種類

                "note": event["note"] or ""  # 詳細メモ

            }

        }  # 1件分のFullCalendar予定データ作成を終了する


        if event["end_time"]:  # 終了時間が登録されている場合

            calendar_event["end"] = f"{event['event_date']}T{event['end_time']}"  # FullCalendar用の終了日時を追加する


        calendar_events.append(calendar_event)  # 作成した予定を表示用リストへ追加する


    return render_template(
        "calendar.html",  # templatesフォルダ内のcalendar.htmlを表示する
        pets=pet_list,  # 予定追加画面用の登録済みペット一覧を渡す
        calendar_events=calendar_events,  # FullCalendarへ表示する保存済み予定を渡す
        error_message=None  # 通常表示では入力エラーは無い
    )  # カレンダー画面表示処理を終了する

def fetch_pets_and_selected(pet_id_text):  # 登録済みペット一覧と、指定されたIDから選択中のペットを取得する共通処理を定義する

    connection = get_db_connection()  # ペット情報を取得するためSQLiteへ接続する

    pet_list = connection.execute(  # petsテーブルから登録されているすべてのペットを取得する

        """
        SELECT id, name, type, age, weight, note, photo
        FROM pets
        ORDER BY id
        """  # 登録された順番でペット情報を取得するSQLを書く

    ).fetchall()  # SQLの検索結果をすべて取得する

    selected_pet = None  # 最初は選択中のペットが存在しない状態にしておく

    if pet_id_text:  # ペットIDが指定されている場合

        selected_pet = connection.execute(  # 指定されたIDのペット情報を取得する

            """
            SELECT id, name, type, age, weight, note, photo
            FROM pets
            WHERE id = ?
            """,  # 指定されたペット1匹を取得するSQLを書く

            (pet_id_text,)  # 指定されたペットIDをSQLへ渡す

        ).fetchone()  # 条件に一致したペット1匹分を取得する

    elif pet_list:  # ペットIDが指定されておらず、ペットが1匹以上登録されている場合

        selected_pet = connection.execute(  # 登録されている中で最もIDが小さいペットを取得する

            """
            SELECT id, name, type, age, weight, note, photo
            FROM pets
            ORDER BY id ASC
            LIMIT 1
            """  # IDの小さい順に並べ、最初の1匹だけ取得するSQLを書く

        ).fetchone()  # 最初のペット1匹分を取得する

    connection.close()  # ペット情報を取得し終わったのでSQLiteとの接続を終了する

    return pet_list, selected_pet  # ペット一覧と選択中のペットを返す

@app.route("/records", methods=["GET", "POST"])  # 記録画面で表示のGETと記録追加のPOSTを受け付ける
def records():  # 記録画面の表示と、健康・通院記録の新規追加を行う関数を定義する

    if request.method == "POST":  # 「記録を追加」フォームからPOSTでデータが送信された場合だけ以下を実行する

        pet_id = request.form.get("pet_id")  # フォームから記録対象のペットIDを取得する

        record_type = request.form.get("type", "")  # フォームから記録の種類を取得する

        detail = request.form.get("detail", "").strip()  # 記録の内容を取得し、前後の余分な空白を削除する

        weight_text = request.form.get("weight_value", "").strip()  # 体重の値をまず文字列として取得する

        record_date_text = request.form.get("record_date", "").strip()  # 記録日を文字列として取得する

        error_message = None  # 入力内容に問題があった場合のエラーメッセージを保存する変数を用意する

        record_type_labels = [record_type_item["label"] for record_type_item in RECORD_TYPE_POOL]  # 選択できる記録の種類名だけを一覧として取り出す

        if not pet_id:  # 記録対象のペットが選ばれていない場合

            error_message = "記録するペットを選択してください。"  # ペット未選択であることをエラーメッセージとして設定する

        elif record_type not in record_type_labels:  # 記録の種類が選択肢に無い値だった場合

            error_message = "記録の種類を選択してください。"  # 種類が未選択・不正であることを知らせる

        elif not detail:  # 記録の内容が空欄の場合

            error_message = "記録の内容を入力してください。"  # 内容が必要であることを知らせる

        elif len(detail) > 200:  # 記録の内容が200文字を超えている場合

            error_message = "記録の内容は200文字以内で入力してください。"  # 内容の文字数制限を知らせる

        record_date = None  # 変換できた記録日を保存する変数を用意する

        if not error_message:  # ここまでエラーが無い場合

            try:  # 記録日を日付として解釈できるか確認する

                record_date = date.fromisoformat(record_date_text)  # 入力された記録日を日付型に変換する

            except ValueError:  # 日付として解釈できない値が入力されていた場合

                error_message = "記録日を正しく選択してください。"  # 記録日の入力形式が不正であることを知らせる

        weight_value = None  # 体重の記録でない場合は体重の値を持たせない

        if not error_message and record_type == "体重":  # ここまでエラーが無く、体重の記録を追加しようとしている場合

            if not weight_text:  # 体重の値が入力されていない場合

                error_message = "体重の値を入力してください。"  # 体重の入力が必要であることを知らせる

            else:  # 体重の値が入力されている場合

                try:  # 体重を小数へ変換できるか確認する

                    weight_value = float(weight_text)  # 入力された体重を小数へ変換する

                except ValueError:  # 小数へ変換できない値が入力されていた場合

                    error_message = "体重は数値で入力してください。"  # 体重の入力形式が不正であることを知らせる

                if error_message is None and (weight_value < 0 or weight_value > 500):  # 変換できた体重が許可範囲外だった場合

                    error_message = "体重は0kg以上500kg以下で入力してください。"  # 体重の範囲を知らせる

        if error_message:  # 入力内容に何らかのエラーが存在する場合

            pet_list, selected_pet = fetch_pets_and_selected(pet_id)  # 記録画面を再表示するためペット一覧と選択中のペットを取得する

            pet_records = fetch_pet_records(selected_pet["id"]) if selected_pet else []  # 選択中のペットの記録を取得する

            record_groups = group_records_by_type(pet_records) if pet_records else []  # 記録を種類ごとのまとめに組み立て直す

            record_reminders = build_record_reminders(selected_pet, pet_records) if selected_pet else []  # 記録を促すリマインダーを組み立て直す

            return render_template(
                "records.html",  # 記録画面を再表示する
                pets=pet_list,  # 登録済みペット一覧をHTMLへ渡す
                selected_pet=selected_pet,  # 現在選択されているペット情報をHTMLへ渡す
                view_all=False,  # 記録追加フォームは特定のペットに対する操作なので「全員」表示にはしない
                pet_records=pet_records,  # 選択中のペットの健康・通院履歴(時系列)をHTMLへ渡す
                record_groups=record_groups,  # 選択中のペットの健康・通院履歴(種類ごとのまとめ)をHTMLへ渡す
                record_reminders=record_reminders,  # 記録を促すリマインダーをHTMLへ渡す
                record_types=RECORD_TYPE_POOL,  # 記録の種類の選択肢をHTMLへ渡す
                all_records=[],  # 「全員」表示ではないため空のリストを渡す
                all_record_groups=[],  # 「全員」表示ではないため空のリストを渡す
                pet_record_groups=[],  # 「全員」表示ではないため空のリストを渡す
                error_message=error_message,  # 入力エラーメッセージをHTMLへ渡す
                form_type=record_type,  # 入力し直せるよう選んでいた種類をHTMLへ渡す
                form_detail=detail,  # 入力し直せるよう入力していた内容をHTMLへ渡す
                form_weight=weight_text,  # 入力し直せるよう入力していた体重をHTMLへ渡す
                form_date=record_date_text  # 入力し直せるよう選んでいた記録日をHTMLへ渡す
            )  # DBへの保存処理は行わず、記録画面へ戻る

        connection = get_db_connection()  # SQLiteへ接続する

        connection.execute(  # 新しい記録をrecordsテーブルへ登録する

            """
            INSERT INTO records (pet_id, type, detail, weight_value, record_date)
            VALUES (?, ?, ?, ?, ?)
            """,  # 新しい記録の内容を保存するSQLを書く

            (pet_id, record_type, detail, weight_value, record_date.isoformat())  # 入力された記録の内容をSQLへ渡す

        )  # INSERT処理を終了する

        connection.commit()  # 記録の追加をSQLiteへ確定する

        connection.close()  # SQLiteとの接続を終了する

        flash("記録を保存しました。", "success")  # 保存完了メッセージを一時保存する

        return redirect(url_for("records", pet_id=pet_id))  # 記録したペットのIDを付けて記録画面へ戻る

    view = request.args.get("view")  # URLの?view=allが指定されているか確認する

    pet_list, selected_pet = fetch_pets_and_selected(request.args.get("pet_id"))  # URLのpet_idからペット一覧と選択中のペットを取得する

    if view == "all":  # 「全員」タブが選ばれている場合

        all_records = fetch_all_records()  # 登録されているすべてのペットの記録をペット名付きで取得する

        return render_template(
            "records.html",  # templatesフォルダ内のrecords.htmlを表示する
            pets=pet_list,  # 登録済みペット一覧をHTMLへ渡す(切り替えチップの表示に使う)
            selected_pet=None,  # 「全員」表示では特定のペットは選択されていない状態にする
            view_all=True,  # 「全員」タブの内容を表示するようHTMLへ伝える
            pet_records=[],  # 個別ペット表示ではないため空のリストを渡す
            record_groups=[],  # 個別ペット表示ではないため空のリストを渡す
            record_reminders=[],  # 「全員」表示ではリマインダーはまとめて出さない
            record_types=RECORD_TYPE_POOL,  # 記録の種類の選択肢をHTMLへ渡す(未使用だが他の分岐と揃えておく)
            all_records=all_records,  # 全ペット分の記録(時系列用)をHTMLへ渡す
            all_record_groups=group_records_by_type(all_records) if all_records else [],  # 全ペット分の記録を種類ごとにまとめてHTMLへ渡す
            pet_record_groups=group_records_by_pet(all_records, pet_list) if all_records else [],  # 全ペット分の記録をペットごとにまとめてHTMLへ渡す
            error_message=None,  # 「全員」表示にフォームは無いのでエラーメッセージも無い
            form_type=None,  # 「全員」表示では記録追加フォームを使わない
            form_detail="",  # 「全員」表示では記録追加フォームを使わない
            form_weight="",  # 「全員」表示では記録追加フォームを使わない
            form_date=date.today().isoformat()  # 「全員」表示では記録追加フォームを使わない
        )  # 「全員」タブのHTML表示処理を終了する

    pet_records = fetch_pet_records(selected_pet["id"]) if selected_pet else []  # 選択中のペットがいる場合だけ健康・通院履歴を取得する

    record_groups = group_records_by_type(pet_records) if pet_records else []  # 時系列の記録を種類ごとのまとめにも組み立て直す

    record_reminders = build_record_reminders(selected_pet, pet_records) if selected_pet else []  # 予定日を過ぎても記録が無い項目のリマインダーを組み立てる

    return render_template(
        "records.html",  # templatesフォルダ内のrecords.htmlを表示する
        pets=pet_list,  # 登録済みペット一覧をHTMLへ渡す
        selected_pet=selected_pet,  # 現在選択されているペット情報をHTMLへ渡す
        view_all=False,  # 個別ペットの内容を表示するようHTMLへ伝える
        pet_records=pet_records,  # 選択中のペットの健康・通院履歴(時系列)をHTMLへ渡す
        record_groups=record_groups,  # 選択中のペットの健康・通院履歴(種類ごとのまとめ)をHTMLへ渡す
        record_reminders=record_reminders,  # 記録を促すリマインダーをHTMLへ渡す
        record_types=RECORD_TYPE_POOL,  # 記録の種類の選択肢をHTMLへ渡す
        all_records=[],  # 個別ペット表示ではないため空のリストを渡す
        all_record_groups=[],  # 個別ペット表示ではないため空のリストを渡す
        pet_record_groups=[],  # 個別ペット表示ではないため空のリストを渡す
        error_message=None,  # 初回表示ではエラーメッセージは無い
        form_type=None,  # 初回表示ではフォームの種類選択は空にする
        form_detail="",  # 初回表示ではフォームの内容欄は空にする
        form_weight="",  # 初回表示ではフォームの体重欄は空にする
        form_date=date.today().isoformat()  # 記録日の初期値は今日の日付にする
    )  # HTML表示処理を終了する

@app.route("/reservation")  # 「/reservation」にアクセスされたときの処理を指定する
def reservation():  # 予約画面を表示する関数を定義する

    return render_template("reservation.html")  # templatesフォルダ内のreservation.htmlを表示する

if __name__ == "__main__":  # このapp.pyが直接実行された場合だけ以下を実行する

    init_db()  # Flaskを起動する前にpetsテーブルが存在することを確認する

    app.run(debug=True)  # Flaskの開発用サーバーをデバッグモードで起動する