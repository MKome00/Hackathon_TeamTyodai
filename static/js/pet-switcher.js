const pets = { // デモ用として、登録されているペットごとのプロフィール情報をJavaScript内に用意する

    pochi: { // ポチのプロフィール情報をまとめる

        name: "ポチ", // ポチの名前を設定する

        type: "柴犬", // ポチの種類を設定する

        age: 3, // ポチの年齢を設定する

        weight: 8.5, // ポチの体重を設定する

        note: "元気で散歩が大好きです", // ポチのその他の基本情報を設定する

        icon: "🐕" // 写真がない場合に表示する仮の絵文字を設定する

    }, // ポチのプロフィール情報を終了する


    mike: { // ミケのプロフィール情報をまとめる

        name: "ミケ", // ミケの名前を設定する

        type: "三毛猫", // ミケの種類を設定する

        age: 5, // ミケの年齢を設定する

        weight: 4.2, // ミケの体重を設定する

        note: "少し人見知りです", // ミケのその他の基本情報を設定する

        icon: "🐈" // 写真がない場合に表示する仮の絵文字を設定する

    }, // ミケのプロフィール情報を終了する


    coco: { // ココのプロフィール情報をまとめる

        name: "ココ", // ココの名前を設定する

        type: "トイプードル", // ココの種類を設定する

        age: 2, // ココの年齢を設定する

        weight: 3.1, // ココの体重を設定する

        note: "アレルギーに注意", // ココのその他の基本情報を設定する

        icon: "🐩" // 写真がない場合に表示する仮の絵文字を設定する

    } // ココのプロフィール情報を終了する

}; // デモ用ペット情報の定義を終了する


const switchButton = document.getElementById("pet-switch-button"); // 右上に表示するペット切り替えボタンを取得する

const dropdown = document.getElementById("pet-dropdown"); // ペット一覧を表示するプルダウンを取得する

const currentPetName = document.getElementById("current-pet-name"); // 現在選択中のペット名を表示する部分を取得する

const petOptions = document.querySelectorAll(".pet-option"); // プルダウン内の登録済みペット選択肢をすべて取得する

const addPetButton = document.getElementById("add-pet-button"); // 「ペットを追加」ボタンを取得する

const nameInput = document.getElementById("pet-name"); // 名前入力欄を取得する

const typeInput = document.getElementById("pet-type"); // 種類入力欄を取得する

const ageInput = document.getElementById("pet-age"); // 年齢入力欄を取得する

const weightInput = document.getElementById("pet-weight"); // 体重入力欄を取得する

const noteInput = document.getElementById("pet-note"); // その他の基本情報入力欄を取得する

const photoPlaceholder = document.querySelector(".pet-photo-placeholder"); // 写真未登録時に表示する絵文字部分を取得する


switchButton.addEventListener("click", () => { // 右上のペット名ボタンがクリックされたときの処理を設定する

    dropdown.classList.toggle("open"); // openクラスを付け外ししてプルダウンの表示と非表示を切り替える

}); // ペット切り替えボタンのクリック処理を終了する


petOptions.forEach((option) => { // 登録されているすべてのペット選択肢を1つずつ処理する

    option.addEventListener("click", () => { // ペット名がクリックされたときの処理を設定する

        const petId = option.dataset.petId; // クリックされたボタンのdata-pet-idからペットを識別するIDを取得する

        const selectedPet = pets[petId]; // IDを使って対応するペットのプロフィール情報を取得する


        currentPetName.textContent = selectedPet.name; // 右上のボタンに表示する名前を選択されたペット名へ変更する

        nameInput.value = selectedPet.name; // 名前入力欄を選択されたペットの名前へ変更する

        typeInput.value = selectedPet.type; // 種類入力欄を選択されたペットの種類へ変更する

        ageInput.value = selectedPet.age; // 年齢入力欄を選択されたペットの年齢へ変更する

        weightInput.value = selectedPet.weight; // 体重入力欄を選択されたペットの体重へ変更する

        noteInput.value = selectedPet.note; // その他の基本情報を選択されたペットの内容へ変更する

        photoPlaceholder.textContent = selectedPet.icon; // 写真部分の仮表示を選択されたペットの絵文字へ変更する


        dropdown.classList.remove("open"); // ペットを選択した後にプルダウンを閉じる

    }); // 1つのペット選択肢に対するクリック処理を終了する

}); // すべてのペット選択肢への設定を終了する


addPetButton.addEventListener("click", () => { // 「ペットを追加」がクリックされたときの処理を設定する

    currentPetName.textContent = "新しいペット"; // 右上の表示を新しいペットへ変更する

    nameInput.value = ""; // 名前入力欄を空にする

    typeInput.value = ""; // 種類入力欄を空にする

    ageInput.value = ""; // 年齢入力欄を空にする

    weightInput.value = ""; // 体重入力欄を空にする

    noteInput.value = ""; // その他の基本情報入力欄を空にする

    photoPlaceholder.textContent = "🐾"; // 写真部分を新規ペット用の足跡絵文字に変更する


    dropdown.classList.remove("open"); // 新規ペット入力画面へ切り替えた後にプルダウンを閉じる

}); // ペット追加ボタンのクリック処理を終了する


document.addEventListener("click", (event) => { // ページ内のどこかがクリックされたときの処理を設定する

    if (!event.target.closest(".pet-switcher")) { // クリックされた場所がペット切り替え領域の外側だった場合

        dropdown.classList.remove("open"); // 開いているプルダウンを閉じる

    } // ペット切り替え領域外かどうかの判定を終了する

}); // ページ全体のクリック処理を終了する