const reservationTabButtons = document.querySelectorAll(".reservation-tab"); // 「購入」「予約」を切り替えるタブのボタンをすべて取得する

const reservationPanels = document.querySelectorAll(".reservation-panel"); // タブに対応する中身のパネルをすべて取得する

if (reservationTabButtons.length && reservationPanels.length) { // タブが存在するページ(予約画面)だけで処理する

    reservationTabButtons.forEach((button) => { // タブのボタンを1つずつ順番に処理する

        button.addEventListener("click", () => { // タブのボタンがクリックされたときの処理を設定する

            reservationTabButtons.forEach((otherButton) => { // すべてのタブボタンを1つずつ処理する

                otherButton.classList.remove("active"); // 選択中の見た目を一度すべて外す

            }); // すべてのタブボタンからactiveを外す処理を終了する

            reservationPanels.forEach((panel) => { // すべてのパネルを1つずつ処理する

                panel.classList.remove("active"); // 表示中のパネルを一度すべて隠す

            }); // すべてのパネルを隠す処理を終了する

            button.classList.add("active"); // クリックされたボタンだけ選択中の見た目にする

            const targetPanel = document.getElementById(button.dataset.target); // ボタンのdata-targetに対応するパネルを取得する

            if (targetPanel) { // 対応するパネルが見つかった場合

                targetPanel.classList.add("active"); // そのパネルだけ表示する

            } // 対応するパネルが見つかった場合の処理を終了する

        }); // 1つのタブボタンのクリック処理を終了する

    }); // すべてのタブボタンへのクリック処理設定を終了する

} // タブが存在する場合の処理を終了する

const facilitySearchInput = document.getElementById("facility-search"); // 施設名・エリアで絞り込む検索欄を取得する

const facilityCards = document.querySelectorAll(".facility-card"); // 検索対象になる施設カードをすべて取得する

if (facilitySearchInput && facilityCards.length) { // 検索欄と施設カードが存在するページ(予約画面)だけで処理する

    facilitySearchInput.addEventListener("input", () => { // 検索欄に文字が入力されるたびの処理を設定する

        const keyword = facilitySearchInput.value.trim().toLowerCase(); // 入力された検索キーワードの前後の空白を除き、小文字に揃える

        facilityCards.forEach((card) => { // 施設カードを1件ずつ処理する

            const cardText = card.dataset.facilitySearch.toLowerCase(); // カードに埋め込んでおいた「施設名 エリア」を小文字に揃える

            const isMatch = cardText.includes(keyword); // 検索キーワードがカードの文字列に含まれているか確認する

            card.style.display = isMatch ? "" : "none"; // 一致すれば通常表示、一致しなければ非表示にする

        }); // すべての施設カードへの絞り込み処理を終了する

    }); // 検索欄の入力イベント処理を終了する

} // 検索欄と施設カードが存在する場合の処理を終了する
