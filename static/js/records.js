const allTabButtons = document.querySelectorAll(".record-all-tab"); // 「全員」表示内の時系列・ペット別・項目別を切り替えるサブタブのボタンをすべて取得する

const allPanels = document.querySelectorAll(".record-all-panel"); // サブタブに対応する中身のパネルをすべて取得する

if (allTabButtons.length && allPanels.length) { // 「全員」表示ではないページ(個別ペット表示)ではサブタブが存在しないためエラーにならないようにする

    allTabButtons.forEach((button) => { // サブタブのボタンを1つずつ順番に処理する

        button.addEventListener("click", () => { // サブタブのボタンがクリックされたときの処理を設定する

            allTabButtons.forEach((otherButton) => { // すべてのサブタブボタンを1つずつ処理する

                otherButton.classList.remove("active"); // 選択中の見た目を一度すべて外す

            }); // すべてのサブタブボタンからactiveを外す処理を終了する

            allPanels.forEach((panel) => { // すべてのパネルを1つずつ処理する

                panel.classList.remove("active"); // 表示中のパネルを一度すべて隠す

            }); // すべてのパネルを隠す処理を終了する

            button.classList.add("active"); // クリックされたボタンだけ選択中の見た目にする

            const targetPanel = document.getElementById(button.dataset.target); // ボタンのdata-targetに対応するパネルを取得する

            if (targetPanel) { // 対応するパネルが見つかった場合

                targetPanel.classList.add("active"); // そのパネルだけ表示する

            } // 対応するパネルが見つかった場合の処理を終了する

        }); // 1つのサブタブボタンのクリック処理を終了する

    }); // すべてのサブタブボタンへのクリック処理設定を終了する

} // サブタブが存在する場合の処理を終了する
