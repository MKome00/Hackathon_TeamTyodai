document.addEventListener("DOMContentLoaded", () => { // HTML全体の読み込みが完了してからカレンダーを作成する

    const calendarElement = document.getElementById("calendar"); // FullCalendarを表示するHTML要素を取得する

    const eventModal = document.getElementById("event-modal"); // 予定追加画面として使用するモーダル全体を取得する

    const modalCloseButton = document.getElementById("event-modal-close"); // モーダル右上の閉じるボタンを取得する

    const cancelButton = document.getElementById("event-cancel-button"); // モーダル下部のキャンセルボタンを取得する

    const modalOverlay = document.querySelector(".event-modal-overlay"); // モーダル表示中の背景部分を取得する

    const eventDateInput = document.getElementById("event-date"); // 予定の日付を入力する欄を取得する

    const calendarEventsData = document.getElementById("calendar-events-data"); // FlaskがHTMLへ埋め込んだ保存済み予定のJSONデータを取得する

    const calendarEvents = calendarEventsData // 予定JSONを保持する要素が存在するか確認する

        ? JSON.parse(calendarEventsData.textContent) // 存在する場合はJSON文字列をJavaScriptの配列へ変換する

        : []; // 存在しない場合は空の予定一覧として扱う

    const calendar = new FullCalendar.Calendar(calendarElement, { // calendar要素を使ってFullCalendar本体を作成する

        initialView: "dayGridMonth", // 最初は1か月分のカレンダーを表示する

        themeSystem: "classic", // FullCalendarのclassicテーマを使用して升目や罫線を表示する

        locale: "ja", // 月名や曜日などを日本語表示にする

        firstDay: 0, // 1週間の最初を日曜日にする

        height: "auto", // カレンダーの高さを内容に合わせて自動調整する

        events: calendarEvents,


        headerToolbar: { // カレンダー上部の操作ボタンと年月タイトルの配置を設定する

            start: "title", // 左側に現在表示している年月を表示する

            center: "", // 中央には何も表示しない

            end: "prev today next" // 右側に「前月・今日・次月」の順で表示する

        }, // ヘッダー設定を終了する


        buttons: { // FullCalendar v7で各ボタンの表示内容を設定する

            prev: { // 前月へ移動するボタンを設定する

                text: "＜" // 前月ボタンの文字を左向き記号にする

            }, // 前月ボタン設定を終了する


            today: { // 今日へ戻るボタンを設定する

                text: "今日" // Todayではなく日本語の「今日」と表示する

            }, // 今日ボタン設定を終了する


            next: { // 次月へ移動するボタンを設定する

                text: "＞" // 次月ボタンの文字を右向き記号にする

            } // 次月ボタン設定を終了する

        }, // ボタン設定を終了する

        dayHeaderInnerClass: (info) => { // 「日・月・火…」の文字部分だけにクラスを付ける

            const day = info.date.getDay(); // 曜日を0～6で取得する。0が日曜日、6が土曜日


            if (day === 0) { // 日曜日の場合

                return "calendar-sunday-text"; // 日曜日の文字専用クラスを付ける

            }


            if (day === 6) { // 土曜日の場合

                return "calendar-saturday-text"; // 土曜日の文字専用クラスを付ける

            }


            return ""; // 平日は特別なクラスを付けない

        }, // 曜日文字のクラス設定を終了する


        dayCellTopInnerClass: (info) => { // 各日付番号の文字部分だけにクラスを付ける

            const day = info.date.getDay(); // その日付の曜日を0～6で取得する


            if (day === 0) { // 日曜日の場合

                return "calendar-sunday-text"; // 日曜日の日付文字専用クラスを付ける

            }


            if (day === 6) { // 土曜日の場合

                return "calendar-saturday-text"; // 土曜日の日付文字専用クラスを付ける

            }


            return ""; // 平日は特別なクラスを付けない

        }, // 日付文字のクラス設定を終了する

        dayCellClass: (info) => { // 各日付セル全体に必要なクラスを付ける

            if (info.isToday) { // この日付が今日の場合

                return "calendar-today"; // 今日専用のクラスを付ける

            }


            return ""; // 今日以外は特別なクラスを付けない

        }, // 今日のセル強調用クラス設定を終了する


        selectable: true, // カレンダー上の日付を選択できるようにする


        dateClick: (info) => { // カレンダーの日付がクリックされたときの処理を設定する

            eventDateInput.value = info.dateStr; // クリックされた日付を予定入力欄へ自動で設定する

            eventModal.classList.add("open"); // 予定追加モーダルにopenクラスを付けて表示する

        } // 日付クリック時の処理を終了する

    }); // FullCalendar本体の設定を終了する


    calendar.render(); // 設定したカレンダーを実際に画面へ表示する


    const closeModal = () => { // 予定追加モーダルを閉じる共通処理を定義する

        eventModal.classList.remove("open"); // openクラスを外してモーダルを非表示にする

    }; // モーダルを閉じる処理の定義を終了する


    modalCloseButton.addEventListener("click", () => { // 右上の×ボタンがクリックされた場合

        closeModal(); // 予定追加モーダルを閉じる

    }); // ×ボタンのクリック処理を終了する


    cancelButton.addEventListener("click", () => { // キャンセルボタンがクリックされた場合

        closeModal(); // 予定追加モーダルを閉じる

    }); // キャンセルボタンのクリック処理を終了する


    modalOverlay.addEventListener("click", () => { // モーダル外側の暗い部分がクリックされた場合

        closeModal(); // 予定追加モーダルを閉じる

    }); // 背景クリック処理を終了する

}); // HTML読み込み完了後の処理を終了する