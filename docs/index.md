# 🌐 YAIBA-BI

**非プログラマー向け VRChat 人流解析ツール**
— YAIBA-VRC のログから、グラフや動画を自動生成 —

---

## 🎯 YAIBA-BI とは？

**YAIBA-BI は、VRChat の位置情報ログをアップロードするだけで
移動軌跡・滞在分布・ヒートマップ・可視化動画を自動生成できるツールです。**

元々 YAIBA はプログラマー向けの分析ツールでしたが、
YAIBA-BI によって **誰でも数クリックで人流解析ができる環境**を目指しています。

* VRChatイベントの動線可視化
* 展示会・バーイベントの混雑状況の分析
* 安全設計・導線改善のチェック
* 研究用途としての実験設計・行動分析

現実空間では難しい“人の動きの可視化”を、
**VR空間では誰もが手軽に実施できる世界**をつくるプロジェクトです。

---

## 📊 このツールでできること

> VRChat のログから自動生成される可視化例です。

### **① 同時接続数の推移（来場者数の変化が一目でわかる）**

イベント中に「何人が来ていたのか」「ピークはいつか」を時系列で確認できます。  
主催者がまず知りたい基礎的な指標を自動で可視化します。
![同時接続数の推移](./images/cc_line_2025-05-17_sample.png)

### **② ヒートマップ（どこが賑わっていたかを可視化）**

空間内の滞在傾向を色で表示します。  
混雑箇所・人気スポット・回遊性の把握が可能です。
![ヒートマップ](./images/heatmap_2D-testdata-20250516_214915_v1.0.png)

### **③ アニメーション可視化（空間内の動きをそのまま再生）**

参加者の動きを時間軸で再現したアニメーション動画を生成します。  
イベント紹介やデモ用途にも役立つ直感的な可視化です。

<iframe width="560" height="315" 
src="https://www.youtube.com/embed/-LIoVicXueo" 
title="YouTube video player" frameborder="0"
allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
allowfullscreen>
</iframe>

---

## 🚀 使い方

**STEP 1 — YAIBA-VRC をワールドに設置**
ログ取得したいワールドに YAIBA-VRC を導入します。
※ 詳しい導入手順は[YAIBA-VRC の導入手順](## YAIBA-VRC の導入手順)をご覧ください。

**STEP 2 — VRChat のログを取得**
`output_log_xxxxx.txt` を VRChat から取り出します。

**STEP 3 — YAIBA-BI にログをアップロード**
Google Colab にログファイルを入れると、自動でグラフ・動画が生成されます。

---

## ▶ YAIBA-BI（Google Colab）を開く

（ここに Colab への大きなボタンリンクを配置）

---

## YAIBA-VRC の導入手順

YAIBA-VRC の Unity での導入方法は以下にまとめています：

👉 **YAIBA-VRC 導入ガイド（詳細はこちら）**
（あなたが書いた手順書ページへのリンクを配置）

---

## 🧩 プロジェクトについて

YAIBA-BI は **DS集会「YAIBA民主化プロジェクト」** によって開発されています。

目的は、
**VR空間の行動データ解析を専門家だけのものにせず、
誰でも直感的に扱えるように民主化すること。**

* VRChatログの可視化基盤の整備
* Colab を活用したワンクリック解析
* 将来的な Web 化・統合ダッシュボード化
* 学会発表・研究支援

GitHub：

* YAIBA-VRC：[https://github.com/ScienceAssembly/YAIBA-VRC](https://github.com/ScienceAssembly/YAIBA-VRC)
* YAIBA：[https://github.com/ScienceAssembly/YAIBA](https://github.com/ScienceAssembly/YAIBA)

---

## 📝 ライセンス・クレジット

* YAIBA-VRC（© VRC Science Assembly）
* YAIBA（© cocu_tan）
* 本プロジェクトは MIT License のもと公開されています。

---

## ✨ Special Thanks

YAIBA民主化プロジェクト メンバー
（ぶんちんさん、いそひまさん、matunさん 他）

---

## 💬 お問い合わせ / 連絡先

（X アカウント or Discordサーバーリンクなどを配置）

---

# 🔧 次にできること

* ページ全体のレイアウト（画像位置・ボタンデザイン）
* Colab ボタンのデザイン生成
* 埋め込み動画の最適化
* 導入手順ページの Markdown 版の作成

---

必要であれば、
**この文章をそのまま GitHub Pages に組み込む HTML/CSS 版**
や
**サイト全体のワイヤーフレーム**
も作成できます。

次にどこを調整しますか？

