import logging
import json
import os
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
    "shioaji",
]

mcp = FastMCP(MCP_SERVER_NAME, dependencies=deps)

# Get simulation mode from environment variable (default to False if not set)
simulation_mode = os.getenv("SHIOAJI_SIMULATION", "False").lower() == "true"
logger.info(f"Initializing Shioaji with simulation mode: {simulation_mode}")
api = sj.Shioaji(simulation=simulation_mode)

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
        quote_type=sj.constant.QuoteType.Tick,
        version=sj.constant.QuoteVersion.v1,
        intraday_odd=intraday_odd
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
        quote_type=sj.constant.QuoteType.BidAsk,
        version=sj.constant.QuoteVersion.v1,
        intraday_odd=intraday_odd
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
        quote_type=sj.constant.QuoteType.Quote,
        version=sj.constant.QuoteVersion.v1
    )

@api.on_quote_stk_v1()
def quote_callback(exchange: Exchange, quote:QuoteSTKv1):
    print(f"Exchange: {exchange}, Quote: {quote}")


@mcp.tool()
def place_order(
    stock_id: str,
    price: float = 0.0, 
    quanity: int = 1, 
    action: str = sj.constant.Action.Buy, 
    price_type: str = sj.constant.StockPriceType.LMT,
    order_type: str = sj.constant.OrderType.ROD,
    order_lot: str = sj.constant.StockOrderLot.Common,
):
    """下單"""
    logger.info("Placing order")

    try:
        contract = api.Contracts.Stocks[stock_id]
        order = api.Order(
            price = price,
            quantity = quanity,
            action = action,
            price_type = price_type,
            order_type = order_type,
            order_lot = order_lot,
            account = api.stock_account
        )

        trade = api.place_order(contract, order)

        api.update_status(api.stock_account) # 更新狀態
        return trade["status"]["status"] 
        # 看委託單狀態, 會回傳以下七種
        # PendingSubmit: 傳送中
        # PreSubmitted: 預約單
        # Submitted: 傳送成功
        # Failed: 失敗
        # Cancelled: 已刪除
        # Filled: 完全成交
        # Filling: 部分成交

    except Exception as e:
        logger.error(f"Failed to place order: {str(e)}")
        raise

@mcp.tool()
def update_order_price(price: float = 0.0):
    """更新委託單價格"""
    logger.info("Updating order status")
    api.update_order(
        trade=shioaji.order.Trade,
        price=price,
    )
    logger.info("Order status updated successfully")
    return trade["status"]["status"] 

@mcp.tool()
def update_order_quantity(quantity: int = 0):
    """更新委託單數量"""
    logger.info("Updating order quantity")
    api.update_order(
        trade=shioaji.order.Trade,
        quantity=quantity,
    )
    logger.info("Order quantity updated successfully")
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
def logout_shioaji():
    """登出永豐證帳戶"""
    api.logout()


@mcp.tool()
def list_positions():
    """列出所有持仓"""
    logger.info("Listing all positions")
    positions = api.list_positions(api.stock_account, unit=sj.constant.Unit.Share)
    df = pd.DataFrame(s.__dict__ for s in positions).set_index("id")
    return df.to_json(orient="records")

@mcp.tool()
def list_profit_loss(begin_date: str, end_date: str):
    """列出已實現損益"""
    logger.info("listing all profit and loss")
    profitloss = api.list_profit_loss(api.stock_account, begin_date, end_date)
    df = pd.DataFrame(s.__dict__ for s in profitloss).set_index("id")
    return df.to_json(orient="records")

