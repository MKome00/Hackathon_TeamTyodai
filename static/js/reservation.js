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

const productSearchInput = document.getElementById("product-search"); // 商品名で絞り込む検索欄を取得する

const productCategoryFilter = document.getElementById("product-category-filter"); // カテゴリで絞り込むプルダウンを取得する

const productPriceFilter = document.getElementById("product-price-filter"); // 価格帯で絞り込むプルダウンを取得する

const productFavoriteOnlyCheckbox = document.getElementById("product-favorite-only-checkbox"); // お気に入りのみ表示するチェックボックスを取得する

const productCards = document.querySelectorAll(".product-card"); // 絞り込み対象になる商品カードをすべて取得する

const productEmptyText = document.getElementById("product-empty-text"); // 絞り込み結果が0件のときに表示する案内文を取得する

if (productSearchInput && productCategoryFilter && productPriceFilter && productCards.length) { // 商品の絞り込みに必要な要素がそろっているページ(予約画面)だけで処理する

    const applyProductFilters = () => { // 検索・カテゴリ・価格帯・お気に入りの条件をまとめて適用する関数を定義する

        const keyword = productSearchInput.value.trim().toLowerCase(); // 入力された商品名キーワードの前後の空白を除き、小文字に揃える

        const selectedCategory = productCategoryFilter.value; // 選択中のカテゴリを取得する

        const selectedPriceRange = productPriceFilter.value; // 選択中の価格帯を取得する

        const favoriteOnly = productFavoriteOnlyCheckbox.checked; // お気に入りのみ表示するかどうかを取得する

        let visibleCount = 0; // 絞り込み後に表示されている商品数を数える変数を用意する

        productCards.forEach((card) => { // 商品カードを1件ずつ処理する

            const nameMatches = card.dataset.productSearch.toLowerCase().includes(keyword); // 商品名にキーワードが含まれているか確認する

            const categoryMatches = !selectedCategory || card.dataset.productCategory === selectedCategory; // カテゴリ未選択、または一致しているか確認する

            let priceMatches = true; // 価格帯の一致結果を保存する変数を用意する(未選択なら常に一致とする)

            if (selectedPriceRange) { // 価格帯が選択されている場合

                const [minPrice, maxPrice] = selectedPriceRange.split("-").map(Number); // 「最小-最大」の形の文字列を数値の配列に分ける

                const price = Number(card.dataset.productPrice); // カードに埋め込んでおいた価格を数値に変換する

                priceMatches = price >= minPrice && price <= maxPrice; // 選択された価格帯の範囲内かどうかを確認する

            } // 価格帯の選択有無による判定を終了する

            const favoriteMatches = !favoriteOnly || card.dataset.productFavorite === "true"; // お気に入りのみ表示が有効なら、お気に入り登録済みかどうかも確認する

            const isMatch = nameMatches && categoryMatches && priceMatches && favoriteMatches; // すべての条件を満たしているか確認する

            card.style.display = isMatch ? "" : "none"; // 一致すれば通常表示、一致しなければ非表示にする

            if (isMatch) { // 表示されている商品だった場合

                visibleCount += 1; // 表示件数を1つ増やす

            } // 表示件数のカウントを終了する

        }); // すべての商品カードへの絞り込み処理を終了する

        if (productEmptyText) { // 案内文の要素が見つかった場合

            productEmptyText.style.display = visibleCount === 0 ? "block" : "none"; // 表示件数が0件のときだけ案内文を表示する

        } // 案内文の表示切り替えを終了する

    }; // 絞り込み条件をまとめて適用する関数の定義を終了する

    productSearchInput.addEventListener("input", applyProductFilters); // 検索欄に文字が入力されるたびに絞り込みをやり直す

    productCategoryFilter.addEventListener("change", applyProductFilters); // カテゴリが変更されるたびに絞り込みをやり直す

    productPriceFilter.addEventListener("change", applyProductFilters); // 価格帯が変更されるたびに絞り込みをやり直す

    productFavoriteOnlyCheckbox.addEventListener("change", applyProductFilters); // お気に入りのみ表示が切り替わるたびに絞り込みをやり直す

} // 商品の絞り込みに必要な要素がそろっている場合の処理を終了する
