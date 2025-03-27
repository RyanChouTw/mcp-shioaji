import logging
import os
import datetime
import pandas as pd
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

import shioaji as sj
from shioaji import TickSTKv1, Exchange, BidAskSTKv1, QuoteSTKv1

MCP_SERVER_NAME = "shioaji"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(MCP_SERVER_NAME)

# Load environment variables
load_dotenv()

deps = [
    "python-dotenv",
    "shioaji[speed]", 
    "pandas"
]

mcp = FastMCP(MCP_SERVER_NAME, dependencies=deps)

# Get simulation mode from environment variable (default to False if not set)
simulation_mode = os.getenv("SHIOAJI_SIMULATION", "False").lower() == "true"
api_key = os.getenv("SHIOAJI_API_KEY")
secret_key = os.getenv("SHIOAJI_SECRET_KEY")
logger.info(f"Initializing Shioaji with simulation mode: {simulation_mode}")
api = sj.Shioaji(simulation=simulation_mode)

@mcp.tool()
def login_shioaji(api_key: str = api_key, secret_key: str = secret_key):
    """登入永豐證帳戶"""
    logger.info(
        f"Login Shioaji"
        f"API key: {api_key} SECRET key: {secret_key}"
    )

    try:
        accounts = api.login(api_key, secret_key)
        # Fetch contracts after successful login
        api.fetch_contracts()
        logger.info(f"Successfully log in Shioaji and fetched contracts")
    except Exception as e:
        logger.error(f"Failed to connect to Shioaji: {str(e)}")
        raise

@mcp.tool()
def list_accounts() -> str:
    """條列出所有永豐證交易帳戶"""
    logger.info("Listing all accounts")
    accounts = api.list_accounts()
    logger.info(f"Accounts: {accounts}")
    return accounts

@mcp.tool()
def list_products():
    """條列出所有永豐證卷提供的交易商品"""
    logger.info("Listing all products")
    contracts = api.Contracts
    logger.info(f"Contracts: {contracts}")
    return contracts

@mcp.tool()
def stock_tick(stock_id, intraday_odd: bool = False):
    """查詢特定股票即時行情，包括整股或是零股資訊"""
    # Convert stock_id to string if it's an integer
    stock_id = str(stock_id)
    logger.info(f"Querying stock tick {stock_id} with intraday_odd {intraday_odd}")
    api.quote.subscribe(
        api.Contracts.Stocks[stock_id],
        quote_type=sj.constant.QuoteType.Tick,
        version=sj.constant.QuoteVersion.v1,
        intraday_odd=intraday_odd
    )

def tick_callback(exchange: Exchange, tick:TickSTKv1):
    logger.info(f"on_tick_stk_v1 Exchange: {exchange}, Tick: {tick}")

api.quote.set_on_tick_stk_v1_callback(tick_callback)

@mcp.tool()
def stock_bidask(stock_id, intraday_odd: bool = False):
    """查詢特定股票委買委賣的資料，一般是上下5檔"""
    # Convert stock_id to string if it's an integer
    stock_id = str(stock_id)
    logger.info(f"Querying stock bidask for {stock_id} with intraday_odd {intraday_odd}")
    api.quote.subscribe(
        api.Contracts.Stocks[stock_id],
        quote_type=sj.constant.QuoteType.BidAsk,
        version=sj.constant.QuoteVersion.v1,
        intraday_odd=intraday_odd
    )

def bidask_callback(exchange: Exchange, bidask:BidAskSTKv1):
    logger.info(f"on_bidask_stk_v1 Exchange: {exchange}, BidAsk: {bidask}")

api.quote.set_on_bidask_stk_v1_callback(bidask_callback)

@mcp.tool()
def stock_quote(stock_id):
    """查詢特定股票即時成交行情"""
    # Convert stock_id to string if it's an integer
    stock_id = str(stock_id)
    logger.info(f"Querying stock quote {stock_id}")
    logger.info(f"contract: {api.Contracts.Stocks[stock_id]}")
    api.quote.subscribe(
        api.Contracts.Stocks[stock_id],
        quote_type=sj.constant.QuoteType.Quote,
        version=sj.constant.QuoteVersion.v1
    )

def quote_callback(exchange: Exchange, quote:QuoteSTKv1):
    logger.info(f"on_quote_stk_v1Exchange: {exchange}, Quote: {quote}")

api.quote.set_on_quote_stk_v1_callback(quote_callback)

@mcp.tool()
def place_order(
    stock_id,
    price: float = 0.0, 
    quantity: int = 1, 
    action: str = sj.constant.Action.Buy, 
    price_type: str = sj.constant.StockPriceType.LMT,
    order_type: str = sj.constant.OrderType.ROD,
    order_lot: str = sj.constant.StockOrderLot.Common,
):
    """下單"""
    # Convert stock_id to string if it's an integer
    stock_id = str(stock_id)
    logger.info(f"Placing order for {stock_id} with price {price}")

    try:
        contract = api.Contracts.Stocks[stock_id]
        order = api.Order(
            price=price,
            quantity=quantity,
            action=action,
            price_type=price_type,
            order_type=order_type,
            order_lot=order_lot,
            account=api.stock_account
        )

        trade = api.place_order(contract, order)

        api.update_status(api.stock_account) # 更新狀態

        # 看委託單狀態, 會回傳以下七種
        # PendingSubmit: 傳送中
        # PreSubmitted: 預約單
        # Submitted: 傳送成功
        # Failed: 失敗
        # Cancelled: 已刪除
        # Filled: 完全成交
        # Filling: 部分成交mc

        logger.info(f"Order status: {trade['status']['status']}")
        return trade["status"]["status"] 


    except Exception as e:
        logger.error(f"Failed to place order: {str(e)}")
        raise

def order_callback(stat, msg):
    logger.info(f'order_callback {stat} {msg}')

api.set_order_callback(order_callback)

@mcp.tool()
def update_order_price(price: float = 0.0):
    """更新委託單價格"""
    logger.info("Updating order status")
    api.update_order(
        trade=shioaji.order.Trade,
        price=price,
    )
    logger.info(f"Order status: {trade['status']['status']}")
    return trade["status"]["status"] 

@mcp.tool()
def update_order_quantity(quantity: int = 0):
    """更新委託單數量"""
    logger.info("Updating order quantity")
    api.update_order(
        trade=shioaji.order.Trade,
        quantity=quantity,
    )
    logger.info(f"Order status: {trade['status']['status']}")
    return trade["status"]["status"] 

@mcp.tool()
def cancel_order():
    """取消委託"""
    logger.info("Cancelling order")
    try:
        api.cancel_order(trade=shioaji.order.Trade)
        api.update_status(api.stock_account) # 更新狀態
        return "Order cancelled successfully"
    except Exception as e:
        logger.error(f"Failed to cancel order: {str(e)}")
        raise

@mcp.tool()
def list_stock_trades():
    """列出所有股票證卷委託"""
    logger.info("Listing all stock trades")
    api.update_status(api.stock_account) # 更新狀態
    trades = api.list_trades()
    logger.info(f"Trades: {trades}")
    return trades

@mcp.tool()
def list_positions():
    """列出所有持仓"""
    logger.info("Listing all positions")
    positions = api.list_positions(api.stock_account)
    df = pd.DataFrame(s.__dict__ for s in positions)
    return df

@mcp.tool()
def list_profit_loss(begin_date: str, end_date: str):
    """列出已實現損益"""

    # Validate date format
    try:
        datetime.datetime.strptime(begin_date, "%Y-%m-%d")
        datetime.datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
        begin_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        
    logger.info(f"Listing all profit and loss from {begin_date} to {end_date}")
    profitloss = api.list_profit_loss(api.stock_account, begin_date, end_date)
    df = pd.DataFrame(s.__dict__ for s in profitloss)
    return df

@mcp.tool()
def account_balance():
    """列出帳戶餘額"""
    logger.info("Listing account balance")
    balance = api.account_balance()
    logger.info(f"Balance: {balance}")
    return balance

@mcp.tool()
def logout_shioaji():
    """登出永豐證帳戶"""
    api.logout()
