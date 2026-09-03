document.addEventListener("DOMContentLoaded", () => { // HTML全体の読み込みが完了してからカレンダーを作成する

    const calendarElement = document.getElementById("calendar"); // FullCalendarを表示するHTML要素を取得する

    const eventModal = document.getElementById("event-modal"); // 予定追加画面として使用するモーダル全体を取得する

    const modalCloseButton = document.getElementById("event-modal-close"); // モーダル右上の閉じるボタンを取得する

    const cancelButton = document.getElementById("event-cancel-button"); // モーダル下部のキャンセルボタンを取得する

    const modalOverlay = document.querySelector(".event-modal-overlay"); // モーダル表示中の背景部分を取得する

    const eventDateInput = document.getElementById("event-date"); // 予定の日付を入力する欄を取得する

    const floatingPrevButton = document.getElementById("floating-prev-button"); // 固定表示している前月ボタンを取得する

    const floatingTodayButton = document.getElementById("floating-today-button"); // 固定表示している今日ボタンを取得する

    const floatingNextButton = document.getElementById("floating-next-button"); // 固定表示している次月ボタンを取得する

    const dayEventsModal = document.getElementById("day-events-modal"); // 選択した日の予定一覧を表示するモーダルを取得する

    const dayEventsModalCloseButton = document.getElementById("day-events-modal-close"); // 予定一覧モーダル右上の×ボタンを取得する

    const dayEventsModalOverlay = document.querySelector(".day-events-modal-overlay"); // 予定一覧モーダルの暗い背景部分を取得する

    const dayEventsTitle = document.getElementById("day-events-title"); // 「9月3日の予定」などを表示するタイトル要素を取得する

    const dayEventsList = document.getElementById("day-events-list"); // その日の予定一覧を表示する領域を取得する

    const openAddEventButton = document.getElementById("open-add-event-button"); // 予定一覧から予定追加画面を開くボタンを取得する

    let selectedDate = ""; // 現在選択している日付を保存する変数を用意する

    const calendarEventsData = document.getElementById("calendar-events-data"); // FlaskがHTMLへ埋め込んだ保存済み予定のJSONデータを取得する

    const currentMonthInput = document.getElementById("calendar-current-month"); // 現在表示中の月を保存するhidden入力欄を取得する

    const calendarEvents = calendarEventsData // 予定JSONを保持する要素が存在するか確認する

        ? JSON.parse(calendarEventsData.textContent) // 存在する場合はJSON文字列をJavaScriptの配列へ変換する

        : []; // 存在しない場合は空の予定一覧として扱う

    const urlParams = new URLSearchParams(window.location.search); // 現在のURLに付いているクエリパラメータを取得する

    const monthParam = urlParams.get("month"); // URLの「?month=2026-09」のmonth部分を取得する

        const openDayEventsModal = (dateString) => { // 指定された日の予定一覧モーダルを開く処理を定義する

        selectedDate = dateString; // 現在選択している日付を保存する


        const selectedDateObject = new Date(`${dateString}T00:00:00`); // YYYY-MM-DD形式の日付をJavaScriptの日付型へ変換する

        const month = selectedDateObject.getMonth() + 1; // 月を1〜12の形で取得する

        const day = selectedDateObject.getDate(); // 日を取得する


        dayEventsTitle.textContent = `${month}月${day}日の予定`; // モーダルタイトルを「9月3日の予定」のように設定する


        const eventsForDay = calendarEvents.filter((event) => { // 保存済み予定から選択した日付の予定だけを抜き出す

            return event.start.slice(0, 10) === dateString; // startの先頭10文字の日付部分が選択日と一致する予定だけ残す

        }); // 選択日の予定抽出を終了する


        dayEventsList.innerHTML = ""; // 前に表示していた予定一覧を一度すべて削除する


        if (eventsForDay.length === 0) { // 選択した日に予定が1件もない場合

            const emptyMessage = document.createElement("p"); // 予定が無いことを表示するp要素を作る

            emptyMessage.className = "day-event-empty"; // CSSを適用するためクラス名を設定する

            emptyMessage.textContent = "この日の予定はありません。"; // 予定が無いことを知らせる

            dayEventsList.appendChild(emptyMessage); // メッセージを予定一覧領域へ追加する

        } else { // 選択した日に予定が存在する場合

            const eventList = document.createElement("div"); // 複数の予定カードをまとめる領域を作る

            eventList.className = "day-event-list"; // 予定一覧用CSSを適用する


            eventsForDay.forEach((event) => { // その日の予定を1件ずつ処理する

                const eventItem = document.createElement("div"); // 1件分の予定カードを作る

                eventItem.className = "day-event-item"; // 予定カード用CSSを適用する


                const title = document.createElement("p"); // ペット名と予定種類を表示する要素を作る

                title.className = "day-event-title"; // 予定タイトル用CSSを適用する

                title.textContent = event.title; // Flask側で作った「ポチ・病院」などを表示する

                eventItem.appendChild(title); // 予定タイトルをカードへ追加する


                const time = document.createElement("p"); // 開始・終了時間を表示する要素を作る

                time.className = "day-event-time"; // 時間表示用CSSを適用する


                if (event.allDay) { // 開始時間が設定されていない予定の場合

                    time.textContent = "時間指定なし"; // 時間指定が無いことを表示する

                } else { // 開始時間が設定されている場合

                    const startTime = event.start.slice(11, 16); // startからHH:MM部分だけを取得する


                    if (event.end) { // 終了時間も登録されている場合

                        const endTime = event.end.slice(11, 16); // endからHH:MM部分だけを取得する

                        time.textContent = `${startTime} ～ ${endTime}`; // 開始時間と終了時間を表示する

                    } else { // 終了時間が登録されていない場合

                        time.textContent = startTime; // 開始時間だけを表示する

                    }

                } // 時間表示の条件分岐を終了する


                eventItem.appendChild(time); // 時間表示を予定カードへ追加する


                if (event.extendedProps.note) { // 詳細メモが登録されている場合

                    const note = document.createElement("p"); // 詳細メモ表示用の要素を作る

                    note.className = "day-event-note"; // 詳細メモ用CSSを適用する

                    note.textContent = event.extendedProps.note; // 保存されている詳細メモを表示する

                    eventItem.appendChild(note); // 詳細メモを予定カードへ追加する

                } // 詳細メモがある場合の処理を終了する

                const deleteForm = document.createElement("form"); // 予定削除用のフォームを作成する

                deleteForm.method = "POST"; // 削除処理はPOSTで送信する

                deleteForm.action = event.extendedProps.deleteUrl; // Flaskから渡されたこの予定専用の削除URLを設定する

                deleteForm.className = "day-event-delete-form"; // 削除フォーム用のCSSクラスを設定する


                const currentMonthHidden = document.createElement("input"); // 現在表示中の月を送るhidden入力欄を作る

                currentMonthHidden.type = "hidden"; // 画面には表示しない入力欄にする

                currentMonthHidden.name = "current_month"; // Flask側でcurrent_monthとして受け取れる名前を設定する


                const currentDate = calendar.getDate(); // FullCalendarで現在表示している月の基準日を取得する

                const currentYear = currentDate.getFullYear(); // 表示中の年を取得する

                const currentMonth = String(currentDate.getMonth() + 1).padStart(2, "0"); // 表示中の月を2桁にする


                currentMonthHidden.value = `${currentYear}-${currentMonth}`; // 例「2026-09」の形で保存する


                deleteForm.appendChild(currentMonthHidden); // hidden入力欄を削除フォームへ追加する


                const deleteButton = document.createElement("button"); // 削除ボタンを作成する

                deleteButton.type = "submit"; // フォーム送信用ボタンにする

                deleteButton.className = "day-event-delete-button"; // 削除ボタン用CSSを適用する

                deleteButton.textContent = "削除"; // ボタンに「削除」と表示する


                deleteButton.addEventListener("click", (clickEvent) => { // 削除ボタンが押されたときの処理を設定する

                    const confirmed = window.confirm("この予定を削除しますか？"); // 本当に削除してよいか確認ダイアログを表示する


                    if (!confirmed) { // ユーザーがキャンセルを選んだ場合

                        clickEvent.preventDefault(); // フォーム送信を中止する

                    } // 削除確認の判定を終了する

                }); // 削除ボタンのクリック処理を終了する


                deleteForm.appendChild(deleteButton); // 削除ボタンをフォームへ追加する

                eventItem.appendChild(deleteForm); // 削除フォームを予定カードへ追加する

                eventList.appendChild(eventItem); // 完成した1件分の予定カードを一覧へ追加する

            }); // その日のすべての予定処理を終了する


            dayEventsList.appendChild(eventList); // 完成した予定一覧をモーダルへ追加する

        } // 予定の有無による表示切り替えを終了する


        dayEventsModal.classList.add("open"); // 予定一覧モーダルを表示する

    }; // 予定一覧モーダルを開く処理を終了する

    const calendar = new FullCalendar.Calendar(calendarElement, { // calendar要素を使ってFullCalendar本体を作成する

        initialView: "dayGridMonth", // 最初は1か月分のカレンダーを表示する

        initialDate: monthParam ? `${monthParam}-01` : undefined, // URLに月指定がある場合はその月を最初に表示する

        themeSystem: "classic", // FullCalendarのclassicテーマを使用して升目や罫線を表示する

        locale: "ja", // 月名や曜日などを日本語表示にする

        firstDay: 0, // 1週間の最初を日曜日にする

        height: 650, // カレンダーの高さを内容に合わせて自動調整する

        events: calendarEvents,

        eventContent: (arg) => {
            const icon = document.createElement("span");
            icon.className = "calendar-event-icon";

            const category = arg.event.extendedProps.category;

            const icons = {
                hospital: "🏥",
                trimming: "✂️",
                medication: "💊",
                vaccine: "💉",
                other: "📝"
            };

            icon.textContent = icons[category] || "📝";

            return { domNodes: [icon] };
        },


        headerToolbar: {

            start: "title", // 左側には現在表示している年月だけを表示する

            center: "", // 中央には何も表示しない

            end: "" // 右側の標準「前月・今日・次月」ボタンは表示しない
        },


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

            const classes = []; // この日付セルへ付けるクラスをまとめる配列を用意する


            if (info.isToday) { // この日付が今日の場合

                classes.push("calendar-today"); // 今日専用のクラスを追加する

            }


            if (info.isOther) { // 現在表示している月ではない日付の場合

                classes.push("calendar-other-month"); // 前月・翌月の日付セル用クラスを追加する

            }


            return classes.join(" "); // 付けるクラスを空白でつないでFullCalendarへ返す

        }, // 日付セルのクラス設定を終了する


        selectable: true, // カレンダー上の日付を選択できるようにする


        dateClick: (info) => { // カレンダーの日付がクリックされたときの処理を設定する

            openDayEventsModal(info.dateStr); // 予定入力画面ではなく、その日の予定一覧を表示する

        }, // 日付クリック時の処理を終了する

        eventClick: (info) => { // カレンダー上に表示されている予定がクリックされた場合

            info.jsEvent.preventDefault(); // ブラウザ標準のクリック動作を止める


            const eventDate = info.event.startStr.slice(0, 10); // クリックされた予定の日付部分だけを取得する


            openDayEventsModal(eventDate); // その予定が登録されている日の予定一覧を表示する

        } // 予定クリック時の処理を終了する
    
    }); // FullCalendar本体の設定を終了する


    calendar.render(); // 設定したカレンダーを実際に画面へ表示する

    floatingPrevButton.addEventListener("click", () => { // 固定の＜ボタンがクリックされた場合

        calendar.prev(); // FullCalendarを前月へ移動する

    }); // 前月ボタンの処理を終了する


    floatingTodayButton.addEventListener("click", () => { // 固定の今日ボタンがクリックされた場合

        calendar.today(); // FullCalendarを今日を含む月へ移動する

    }); // 今日ボタンの処理を終了する


    floatingNextButton.addEventListener("click", () => { // 固定の＞ボタンがクリックされた場合

        calendar.next(); // FullCalendarを次月へ移動する

    }); // 次月ボタンの処理を終了する

    openAddEventButton.addEventListener("click", () => { // 「＋予定を追加」がクリックされた場合

        dayEventsModal.classList.remove("open"); // 予定一覧モーダルを閉じる


        eventDateInput.value = selectedDate; // 一覧で見ていた日付を予定入力フォームへ自動入力する


        eventModal.classList.add("open"); // 今まで使っていた予定追加モーダルを表示する

    }); // 予定追加ボタンのクリック処理を終了する

    const closeDayEventsModal = () => { // 予定一覧モーダルを閉じる共通処理を定義する

        dayEventsModal.classList.remove("open"); // openクラスを外して予定一覧を非表示にする

    }; // 予定一覧を閉じる処理の定義を終了する

    dayEventsModalCloseButton.addEventListener("click", () => { // 予定一覧右上の×ボタンが押された場合

        closeDayEventsModal(); // 予定一覧モーダルを閉じる

    }); // ×ボタンの処理を終了する

    dayEventsModalOverlay.addEventListener("click", () => { // 予定一覧の背景部分がクリックされた場合

        closeDayEventsModal(); // 予定一覧モーダルを閉じる

    }); // 背景クリック処理を終了する

    const eventForm = document.getElementById("event-form"); // 予定登録フォームを取得する

    eventForm.addEventListener("submit", () => { // 予定フォームが送信される直前に実行する

        const currentDate = calendar.getDate(); // 現在カレンダーで表示している月の基準日を取得する

        const year = currentDate.getFullYear(); // 表示中の年を取得する

        const month = String(currentDate.getMonth() + 1).padStart(2, "0"); // 表示中の月を2桁にする


        currentMonthInput.value = `${year}-${month}`; // 例「2026-09」としてFlaskへ送れるようにする

    }); // フォーム送信前の処理を終了する


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

    const flashMessages = document.querySelectorAll(".flash-message"); // ページ上に表示されているFlashメッセージをすべて取得する

    flashMessages.forEach((message) => { // 取得したFlashメッセージを1件ずつ処理する

        setTimeout(() => { // 指定した時間が経過したあとに処理を実行する

            message.style.transition = "opacity 0.5s ease"; // メッセージが徐々に透明になるようアニメーションを設定する

            message.style.opacity = "0"; // メッセージを透明にする


            setTimeout(() => { // 透明になるアニメーションが終わったあとに処理する

                message.remove(); // Flashメッセージ自体をHTMLから削除する

            }, 500); // 0.5秒待ってから削除する

        }, 3000); // 3秒間表示したあとで消し始める

    }); // Flashメッセージすべてへの処理を終了する

}); // HTML読み込み完了後の処理を終了する