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

# 安裝 (Installation)

## 系統需求 (Requirements)

- Python 3.12 或更高版本
- uv package manager:
- 永豐證券帳戶 (含 API 金鑰)

If you're on Mac, please install uv as

```bash
brew install uv
```

On Windows
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
``` 
and then
```
set Path=C:\Users\nntra\.local\bin;%Path%
```

Otherwise installation instructions are on their website: Install uv

⚠️ Do not proceed before installing UV

## Claude for Desktop Integration

Go to Claude > Settings > Developer > Edit Config > claude_desktop_config.json to include the following:
```
{
    "mcpServers": {
        "shioaji": {
            "command": "uvx",
            "args": [
                "mcp-shioaji"
            ]
        }
    }
}
```
For Windows users, go to Settings > MCP > Add Server, add a new server with the following settings:
```
{
    "mcpServers": {
        "shioaji": {
            "command": "cmd",
            "args": [
                "/c",
                "uvx",
                "mcp-shioaji"
            ]
        }
    }
}
```

## 使用方法 (Usage)

1. 啟動 MCP 服務器:

```bash
# 開發模式啟動
mcp dev mcp_server.py

# 或安裝此 MCP server (方便之後可以直接從 Claude 來調用)
mcp install mcp_server.py
```

2. 使用 MCP 客戶端連接到服務器並使用提供的工具：

- `login_shioaji`: 登入永豐證券帳戶
- `list_accounts`: 列出所有交易帳戶
- `list_products`: 列出所有可交易商品
- `stock_tick`: 查詢特定股票即時行情
- `stock_bidask`: 查詢特定股票委買委賣資料
- `stock_quote`: 查詢特定股票即時成交行情
- `place_order`: 下單
- `update_order_price`: 更新委託單價格
- `update_order_quantity`: 更新委託單數量
- `cancel_order`: 取消委託
- `list_positions`: 列出所有持倉
- `list_profit_loss`: 列出已實現損益
- `logout_shioaji`: 登出永豐證券帳戶

## 依賴套件 (Dependencies)

- mcp[cli] >= 1.5.0
- python-dotenv >= 1.0.1
- shioaji[speed] >= 1.2.5

## 注意事項 (Notes)

- 使用前請確保您有永豐證券的有效帳戶和 API 金鑰
- 請妥善保管您的 API 金鑰，不要將其公開或上傳到版本控制系統中
- 此專案僅供教育和研究目的使用，請遵守相關證券法規

## 授權 (License)

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.