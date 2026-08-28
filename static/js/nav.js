const nav = document.querySelector(".bottom-nav"); // ページ内の下部ナビゲーション全体を取得する

const indicator = document.querySelector(".nav-indicator"); // 滑らかに移動させる薄黄色の背景を取得する

const links = document.querySelectorAll(".bottom-nav a"); // 下部ナビゲーションにある5つのリンクをすべて取得する

const activeLink = document.querySelector(".bottom-nav a.active"); // 現在開いているページに対応するactive付きリンクを取得する


if (nav && indicator && activeLink) { // 必要なナビゲーション要素がすべて存在する場合だけ、以下の処理を実行する

    const currentIndex = Number(activeLink.dataset.index); // 現在選択されているタブの番号を数値として取得する

    const previousIndex = Number(sessionStorage.getItem("previousNavIndex") ?? currentIndex); // 前のページで選択されていたタブ番号を取得し、存在しない場合は現在の番号を使用する

    const previousLink = links[previousIndex]; // 前に選択されていたタブのリンク要素を取得する


    indicator.style.left = `${previousLink.offsetLeft}px`; // 黄色背景の開始位置を前のタブの左端に設定する

    indicator.style.width = `${previousLink.offsetWidth}px`; // 黄色背景の開始時の横幅を前のタブと同じ幅にする


    requestAnimationFrame(() => { // ブラウザが開始位置を描画した直後に、次の処理を実行する

        requestAnimationFrame(() => { // CSSのtransitionが確実に働くよう、さらに次の描画タイミングまで待つ

            indicator.style.left = `${activeLink.offsetLeft}px`; // 黄色背景を現在選択されているタブの位置まで移動する

            indicator.style.width = `${activeLink.offsetWidth}px`; // 黄色背景の横幅を現在のタブと同じ幅に変更する

        }); // 2回目のrequestAnimationFrame処理を終了する

    }); // 1回目のrequestAnimationFrame処理を終了する


    links.forEach((link) => { // 下部ナビゲーションの5つのリンクを1つずつ順番に処理する

        link.addEventListener("click", () => { // いずれかのナビゲーション項目がクリックされたときの処理を設定する

            sessionStorage.setItem("previousNavIndex", currentIndex); // 現在のタブ番号を、次のページで使うためブラウザに一時保存する

        }); // クリック時の処理を終了する

    }); // 5つのリンクすべてへの設定を終了する

} // ナビゲーションが存在する場合の処理を終了する