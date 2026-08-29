const switchButton = document.getElementById("pet-switch-button"); // 右上に表示されているペット切り替えボタンを取得する

const dropdown = document.getElementById("pet-dropdown"); // 登録済みペット一覧を表示するプルダウンメニューを取得する

const petOptions = document.querySelectorAll(".pet-option"); // データベースから生成されたすべてのペット選択ボタンを取得する

const addPetButton = document.getElementById("add-pet-button"); // 「ペットを追加」ボタンを取得する

switchButton.addEventListener("click", () => { // 右上のペット切り替えボタンがクリックされたときの処理を設定する

    dropdown.classList.toggle("open"); // openクラスを付け外ししてプルダウンの表示と非表示を切り替える

}); // ペット切り替えボタンのクリック処理を終了する

petOptions.forEach((option) => { // 登録されているペット選択ボタンを1つずつ順番に処理する

    option.addEventListener("click", () => { // プルダウン内のペット名がクリックされたときの処理を設定する

        const petUrl = option.dataset.petUrl; // HTMLのdata-pet-urlに保存されている、そのペット専用のURLを取得する

        window.location.href = petUrl; // 選択されたペットID付きのURLへ移動し、Flaskにプロフィールを読み込ませる

    }); // 1匹分のペット選択ボタンのクリック処理を終了する

}); // 登録済みペットすべてへのクリック処理設定を終了する

addPetButton.addEventListener("click", () => { // 「ペットを追加」ボタンがクリックされたときの処理を設定する

    const addUrl = addPetButton.dataset.addUrl; // HTMLのdata-add-urlから新規ペット登録用のURLを取得する

    window.location.href = addUrl; // pet_idを付けずにペットページへ移動し、新規登録状態にする

}); // 「ペットを追加」ボタンのクリック処理を終了する

document.addEventListener("click", (event) => { // ページ内のどこかがクリックされたときの処理を設定する

    if (!event.target.closest(".pet-switcher")) { // クリックされた場所がペット切り替え領域の外側だった場合

        dropdown.classList.remove("open"); // 開いているプルダウンを閉じる

    } // ペット切り替え領域の外側かどうかの判定を終了する

}); // ページ全体のクリック処理を終了する

const photoInput = document.getElementById("pet-photo"); // 「写真を選ぶ」で使用している画像ファイル入力欄を取得する

const photoBox = document.querySelector(".pet-photo-box"); // ペット写真を表示している枠全体を取得する

photoInput.addEventListener("change", () => { // ユーザーが写真を選択したときの処理を設定する

    const selectedFile = photoInput.files[0]; // 選択された画像ファイルの1つ目を取得する

    if (!selectedFile) { // 画像が選択されていない場合

        return; // プレビュー処理を行わずここで終了する

    } // 画像が選択されているかどうかの判定を終了する

    const reader = new FileReader(); // 選択された画像ファイルをブラウザ上で読み込むためのFileReaderを作成する

    reader.addEventListener("load", () => { // 画像ファイルの読み込みが完了したときの処理を設定する

        photoBox.innerHTML = ""; // 現在表示されている犬の絵文字や以前の写真を一度すべて削除する

        const previewImage = document.createElement("img"); // プレビュー画像を表示するためのimg要素を新しく作成する

        previewImage.className = "pet-profile-photo"; // 既存のプロフィール写真用CSSを適用するためクラス名を設定する

        previewImage.src = reader.result; // 読み込んだ画像データをimg要素の表示画像として設定する

        previewImage.alt = "選択したペットの写真"; // 画像が表示できない場合の説明文を設定する

        photoBox.appendChild(previewImage); // 作成したプレビュー画像を写真枠の中へ追加する

    }); // 画像読み込み完了時の処理を終了する

    reader.readAsDataURL(selectedFile); // 選択された画像ファイルをブラウザで表示できるデータ形式として読み込む

}); // 写真選択時の処理を終了する

const petForm = document.querySelector('form[action="/pets"]'); // ペット情報を送信するフォームを取得する

const saveButton = document.querySelector(".pet-save-button"); // 保存ボタンを取得する

if (petForm && saveButton) { // フォームと保存ボタンの両方が存在する場合だけ処理する

    petForm.addEventListener("submit", () => { // 保存フォームが送信された瞬間の処理を設定する

        saveButton.textContent = "保存中..."; // ボタンの文字を「保存中...」へ変更する

        saveButton.disabled = true; // 二重クリックによる重複送信を防ぐためボタンを無効にする

    }); // フォーム送信時の処理を終了する

}