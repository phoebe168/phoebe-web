# phoebe-web 非比營養諮詢中心官網

純靜態網站，放在 GitHub 帳號 phoebe168，用 GitHub Pages 從 `docs/` 發布。

## 資料夾
- `src/layout.html`：共用頁首、頁尾（改選單、聯絡資料改這裡）
- `src/pages/*.html`：各頁內容
- `build.py`：把 src 組成 `docs/*.html`
- `docs/`：實際上線的檔案（style.css、Logo、LINE QR 在 `docs/assets/`）

## 修改流程
1. 改 `src/` 底下的檔案（樣式改 `docs/assets/style.css`）
2. 執行 `python build.py`
3. 用瀏覽器打開 `docs/index.html` 檢查
4. commit 後 push

## 第一次部署
1. 用 phoebe168 登入 GitHub，新增 repo：`phoebe-web`（Public）
2. 在本資料夾：
   ```
   git init
   git add .
   git commit -m "第一版"
   git branch -M main
   git remote add origin https://github.com/phoebe168/phoebe-web.git
   git push -u origin main
   ```
3. repo 的 Settings > Pages：Source 選 Deploy from a branch，Branch 選 `main`、資料夾選 `/docs`
4. 幾分鐘後網址為 https://phoebe168.github.io/phoebe-web/

## 網址
- 主網址：https://phoebecare.tw（`docs/CNAME` 內容即此網址）
- www.phoebecare.tw 由 GitHub 自動導到主網址
- phoebecare.com.tw 轉址到 https://phoebecare.tw
- PChome DNS（phoebecare.tw）：
  - A 紀錄（主機留空）：185.199.108.153、185.199.109.153、185.199.110.153、185.199.111.153
  - CNAME：www 指向 phoebe168.github.io
- GitHub repo Settings > Pages > Custom domain 填 phoebecare.tw，勾選 Enforce HTTPS

## 待補資料
- 營養師姓名、職稱、專長、照片（`src/pages/team.html`，照片放 `docs/assets/team/`）
- 完整地址（`src/layout.html`、`src/pages/contact.html`）
- 服務流程、各頁文案由美英確認
