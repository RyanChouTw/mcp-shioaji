# MCP-Shioaji

MCP server for Shioaji - A bridge between MCP framework and Sinopac's Shioaji trading API.

## 簡介 (Introduction)

MCP-Shioaji 是一個基於 FastMCP 框架開發的服務器，提供與永豐證券的 Shioaji 交易 API 的整合。此專案允許使用者通過 MCP 框架輕鬆地訪問台灣股市的交易功能。

MCP-Shioaji is a server built on the FastMCP framework that integrates with Sinopac Securities' Shioaji trading API. This project allows users to easily access Taiwan stock market trading functionality through the MCP framework.

## 功能 (Features)

- 登入永豐證券帳戶
- 列出所有交易帳戶
- 列出所有可交易商品
- 查詢股票即時行情 (整股/零股)
- 查詢股票委買委賣資料
- 查詢股票即時成交行情
- 登出永豐證券帳戶

## 系統需求 (Requirements)

- Python 3.12 或更高版本
- 永豐證券帳戶 (含 API 金鑰)

## 安裝 (Installation)

### 使用 pip

```bash
# 建立虛擬環境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安裝依賴
pip install -e .
```

### 使用 uv

```bash
# 安裝 uv (如果尚未安裝)
pip install uv

# 建立虛擬環境並安裝依賴
uv venv
uv venv activate  # 啟動虛擬環境
uv pip install -e .
```

## 使用方法 (Usage)

1. 準備 `.env` 檔案，包含您的 API 金鑰資訊 (選擇性)

2. 啟動 MCP 服務器:

```bash
# 使用 python 啟動
python mcp_server.py

# 或使用 uv 啟動
uv python mcp_server.py
```

3. 使用 MCP 客戶端連接到服務器並使用提供的工具：

- `login_shioaji`: 登入永豐證券帳戶
- `list_accounts`: 列出所有交易帳戶
- `list_products`: 列出所有可交易商品
- `stock_tick`: 查詢特定股票即時行情
- `stock_bidask`: 查詢特定股票委買委賣資料
- `stock_quote`: 查詢特定股票即時成交行情
- `logout_shioaji`: 登出永豐證券帳戶

## 依賴套件 (Dependencies)

- mcp[cli] >= 1.5.0
- python-dotenv >= 1.0.1
- shioaji >= 1.2.5

## 注意事項 (Notes)

- 使用前請確保您有永豐證券的有效帳戶和 API 金鑰
- 請妥善保管您的 API 金鑰，不要將其公開或上傳到版本控制系統中
- 此專案僅供教育和研究目的使用，請遵守相關證券法規

## 授權 (License)

[請指定適當的授權]