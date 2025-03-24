import logging
import json
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

import shioaji as sj
from shioaji import TickSTKv1, Exchange

MCP_SERVER_NAME = "shioaji"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(MCP_SERVER_NAME)

load_dotenv()

deps = [
    "python-dotenv",
    "shioaji",
]

mcp = FastMCP(MCP_SERVER_NAME, dependencies=deps)
api = sj.Shioaji()

@mcp.tool()
def login_shioaji(api_key: str, secret_key: str):
    """登入永豐證帳戶"""
    logger.info(
        f"Login Shioaji"
        f"API key: {api_key} SECRET key: {secret_key}"
    )

    try:
        accounts =  api.login(api_key, secret_key)
        logger.info(f"Successfully log in Shioaji")
    except Exception as e:
        logger.error(f"Failed to connect to Shioaji: {str(e)}")
        raise

@mcp.tool()
def list_accounts() -> str:
    """條列出所有永豐證交易帳戶"""
    logger.info("Listing all accounts")
    accounts = api.list_accounts()
    logger.info(f"Accounts: {json.dumps(accounts, ensure_ascii=False)}")
    return f"{json.dumps(accounts, ensure_ascii=False)}"

@mcp.tool()
def list_products():
    """條列出所有永豐證卷提供的交易商品"""
    logger.info("Listing all products")
    result = api.Contracts
    logger.info(f"Products: {json.dumps(result, ensure_ascii=False)}")
    return f"{json.dumps(result, ensure_ascii=False)}"

@mcp.tool()
def stock_tick(stock_id: str, intraday_odd: bool):
    """查詢特定股票即時行情，包括整股或是零股資訊"""
    logger.info("Querying stock tick")
    api.quote.subscribe(
        api.Contracts.Stocks[stock_id],
        quote_type = sj.constant.QuoteType.Tick,
        version = sj.constant.QuoteVersion.v1,
        intraday_odd
    )

@api.on_tick_stk_v1()
def quote_callback(exchange: Exchange, tick:TickSTKv1):
    print(f"Exchange: {exchange}, Tick: {tick}")

@mcp.tool()
def stock_bidask(stock_id: str, intraday_odd: bool):
    """查詢特定股票委買委賣的資料，一般是上下5檔"""
    logger.info("Querying stock bidask")
    api.quote.subscribe(
        api.Contracts.Stocks[stock_id],
        quote_type = sj.constant.QuoteType.BidAsk,
        version = sj.constant.QuoteVersion.v1,
        intraday_odd
    )

@api.on_bidask_stk_v1()
def quote_callback(exchange: Exchange, bidask:BidAskSTKv1):
    print(f"Exchange: {exchange}, BidAsk: {bidask}")

@mcp.tool()
def stock_quote(stock_id: str):
    """查詢特定股票即時成交行情"""
    logger.info("Querying stock quote")
    api.quote.subscribe(
        api.Contracts.Stocks[stock_id],
        quote_type = sj.constant.QuoteType.Quote,
        version = sj.constant.QuoteVersion.v1
    )

@api.on_quote_stk_v1()
def quote_callback(exchange: Exchange, quote:QuoteSTKv1):
    print(f"Exchange: {exchange}, Quote: {quote}")


@mcp.tool()
def logout_shioaji():
    """登出永豐證帳戶"""
    api.logout()