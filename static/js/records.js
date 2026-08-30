const switchButton = document.getElementById("pet-switch-button"); // 右上に表示されているペット切り替えボタンを取得する

const dropdown = document.getElementById("pet-dropdown"); // 登録済みペット一覧を表示するプルダウンメニューを取得する

const petOptions = document.querySelectorAll(".pet-option"); // データベースから生成されたすべてのペット選択ボタンを取得する

if (switchButton && dropdown) { // ペットが1匹も登録されておらず切り替えUIが無い場合にエラーにならないようにする

    switchButton.addEventListener("click", () => { // 右上のペット切り替えボタンがクリックされたときの処理を設定する

        dropdown.classList.toggle("open"); // openクラスを付け外ししてプルダウンの表示と非表示を切り替える

    }); // ペット切り替えボタンのクリック処理を終了する

    petOptions.forEach((option) => { // 登録されているペット選択ボタンを1つずつ順番に処理する

        option.addEventListener("click", () => { // プルダウン内のペット名がクリックされたときの処理を設定する

            const petUrl = option.dataset.petUrl; // HTMLのdata-pet-urlに保存されている、そのペット専用のURLを取得する

            window.location.href = petUrl; // 選択されたペットID付きのURLへ移動し、Flaskに記録一覧を読み込ませる

        }); // 1匹分のペット選択ボタンのクリック処理を終了する

    }); // 登録済みペットすべてへのクリック処理設定を終了する

    document.addEventListener("click", (event) => { // ページ内のどこかがクリックされたときの処理を設定する

        if (!event.target.closest(".pet-switcher")) { // クリックされた場所がペット切り替え領域の外側だった場合

            dropdown.classList.remove("open"); // 開いているプルダウンを閉じる

        } // ペット切り替え領域の外側かどうかの判定を終了する

    }); // ページ全体のクリック処理を終了する

} // ペット切り替えUIが存在する場合の処理を終了する
