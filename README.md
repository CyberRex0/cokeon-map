# cokeon-map
公式のマップがガバガバすぎたので自力で作るプロジェクト

# 開発環境構築
## 要件
- Node.js 18.x以降
  - pnpm
- Python 3.9以降
  - virtualenv
- MySQL 8.x以降

## インストール手順
```
$ pnpm i
$ virtualenv env
$ . env/bin/activate
$ pip install -U -r requirements.txt
```

## 起動手順
(ターミナル1)
```
$ pnpm build --watch
```
※ HMRは使えない。

(ターミナル2)
```
$ . env/bin/activate
(env) $ uvicorn backend:app --reload
```


## Recommended IDE Setup

- [VS Code](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur) + [TypeScript Vue Plugin (Volar)](https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin).
