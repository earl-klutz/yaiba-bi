# 環境構築

## 仮想環境構築 & 活性化
```bash
uv venv .venv
source .venv/bin/activate
```

## パッケージインストール
```bash
uv sync
```

## 開発用サーバーの起動
```bash
uv run mkdocs serve --livereload
```
