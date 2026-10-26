# OPC Store 监控

每日北京时间 21:10 由 GitHub Actions 抓取 [ai6666.com/store](https://ai6666.com/store/) 全量产品，生成静态看板（今日新增 / 浏览 Top 20 / 历史总量）。

- 看板：https://thuhien20086-maker.github.io/opc-store-watch/
- 数据：`data/snapshot-YYYY-MM-DD.json`（逐日）+ `data/latest.json`
- 本地手动跑：`python3 watch.py`
