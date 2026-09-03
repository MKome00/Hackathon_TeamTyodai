const certificateTypeSelects = document.querySelectorAll(".certificate-type-select"); // 証明書の種類を選ぶプルダウンをすべて取得する(ペットの数だけ存在する)

const CERTIFICATE_OTHER_VALUE = "その他"; // 「その他」が選ばれたときに表示を切り替える判定に使う値

certificateTypeSelects.forEach((select) => { // 種類選択プルダウンを1つずつ順番に処理する

    const form = select.closest(".certificate-form"); // このプルダウンが属している証明書追加フォームを取得する

    if (!form) { // 対応するフォームが見つからなかった場合

        return; // このプルダウンに対する処理を中断する

    } // フォームが見つからなかった場合の処理を終了する

    const customNameGroup = form.querySelector(".certificate-custom-name-group"); // 「その他」用の証明書名入力欄をまとめている領域を取得する

    const customNameInput = form.querySelector(".certificate-custom-name-group input"); // 「その他」用の証明書名入力欄そのものを取得する

    if (!customNameGroup || !customNameInput) { // 名前入力欄が見つからなかった場合

        return; // このプルダウンに対する処理を中断する

    } // 名前入力欄が見つからなかった場合の処理を終了する

    const updateCustomNameVisibility = () => { // 選択されている種類に応じて名前入力欄の表示を切り替える関数を定義する

        if (select.value === CERTIFICATE_OTHER_VALUE) { // 「その他」が選ばれている場合

            customNameGroup.hidden = false; // 名前入力欄を表示する

            customNameInput.required = true; // 「その他」の場合は名前の入力を必須にする

        } else { // 「その他」以外が選ばれている場合

            customNameGroup.hidden = true; // 名前入力欄を隠す

            customNameInput.required = false; // プリセットを選んでいる間は名前の入力を必須にしない

            customNameInput.value = ""; // 隠したタイミングで前に入力されていた名前をクリアする

        } // 選択されている種類による表示切り替えを終了する

    }; // 表示切り替え関数の定義を終了する

    select.addEventListener("change", updateCustomNameVisibility); // プルダウンの選択が変わるたびに表示を更新する

    updateCustomNameVisibility(); // ページを開いた直後の状態にも表示切り替えを一度適用する

}); // すべての種類選択プルダウンへの処理設定を終了する
