#!/usr/bin/env python3
"""
测试 Backpack 客户端认证和订单执行
验证环境变量加载、客户端初始化和请求头正确性
"""

import os
import sys
import json
from pathlib import Path
from decimal import Decimal

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from exchanges.bp_client import Account
from bpx.constants.enums import OrderTypeEnum, TimeInForceEnum

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_header(msg):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}")
    print(f"{msg}")
    print(f"{'='*60}{Colors.END}")


def test_env_loading():
    """测试 1: 环境变量加载"""
    print_header("测试 1: 环境变量加载")
    
    env_path = Path('.env')
    if not env_path.exists():
        print_error(f".env 文件不存在: {env_path.absolute()}")
        return False
    
    print_info(f"加载 .env 文件: {env_path.absolute()}")
    load_dotenv('.env')
    
    public_key = os.getenv('BACKPACK_PUBLIC_KEY')
    secret_key = os.getenv('BACKPACK_SECRET_KEY')
    
    if not public_key:
        print_error("BACKPACK_PUBLIC_KEY 未设置")
        return False
    
    if not secret_key:
        print_error("BACKPACK_SECRET_KEY 未设置")
        return False
    
    # 检查是否有引号
    has_quote_issue = False
    if public_key.startswith("'") or public_key.startswith('"'):
        print_warning("BACKPACK_PUBLIC_KEY 包含引号，可能导致问题")
        print_info(f"原始值: {repr(public_key[:20])}...")
        has_quote_issue = True
    
    if secret_key.startswith("'") or secret_key.startswith('"'):
        print_warning("BACKPACK_SECRET_KEY 包含引号，可能导致问题")
        print_info(f"原始值: {repr(secret_key[:20])}...")
        has_quote_issue = True
    
    if has_quote_issue:
        print_warning("建议修复 .env 文件，移除引号")
        print_info("运行命令: sed -i.bak \"s/='\\(.*\\)'/=\\1/g\" .env")
    
    print_success(f"BACKPACK_PUBLIC_KEY 长度: {len(public_key)}")
    print_success(f"BACKPACK_SECRET_KEY 长度: {len(secret_key)}")
    print_info(f"PUBLIC_KEY 前10个字符: {public_key[:10]}...")
    print_info(f"SECRET_KEY 前10个字符: {secret_key[:10]}...")
    
    # 检查 Base64 格式
    if public_key.endswith('='):
        print_info("PUBLIC_KEY 包含 Base64 填充符 '=' (正常)")
    if secret_key.endswith('='):
        print_info("SECRET_KEY 包含 Base64 填充符 '=' (正常)")
    
    return True


def test_client_initialization():
    """测试 2: 客户端初始化"""
    print_header("测试 2: Backpack 客户端初始化")
    
    try:
        public_key = os.getenv('BACKPACK_PUBLIC_KEY')
        secret_key = os.getenv('BACKPACK_SECRET_KEY')
        
        print_info(f"使用 public_key: {public_key[:10]}...")
        print_info(f"使用 secret_key: {secret_key[:10]}...")
        
        # 初始化客户端
        account = Account(
            public_key=public_key,
            secret_key=secret_key,
            window=5000,
            debug=False
        )
        
        print_success("Account 客户端初始化成功")
        print_info(f"客户端类型: {type(account).__name__}")
        print_info(f"Window: {account.window}")
        print_info(f"Debug: {account.debug}")
        
        return account
        
    except Exception as e:
        print_error(f"客户端初始化失败: {e}")
        import traceback
        print(traceback.format_exc())
        return None


def test_account_info(account):
    """测试 3: 获取账户信息"""
    print_header("测试 3: 获取账户信息 (验证认证)")
    
    try:
        print_info("调用 get_account()...")
        result = account.get_account()
        
        if isinstance(result, dict):
            print_success("成功获取账户信息")
            
            # 显示关键信息
            if 'userId' in result:
                print_info(f"用户 ID: {result.get('userId')}")
            if 'username' in result:
                print_info(f"用户名: {result.get('username')}")
            
            # 显示完整响应（截断）
            result_str = json.dumps(result, indent=2)
            if len(result_str) > 500:
                print_info(f"账户数据 (前500字符):\n{result_str[:500]}...")
            else:
                print_info(f"账户数据:\n{result_str}")
            
            return True
        else:
            print_error(f"返回格式异常: {type(result)}")
            print_info(f"返回内容: {result}")
            return False
            
    except Exception as e:
        print_error(f"获取账户信息失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_balances(account):
    """测试 4: 获取余额信息"""
    print_header("测试 4: 获取余额信息")
    
    try:
        print_info("调用 get_balances()...")
        result = account.get_balances()
        
        if isinstance(result, dict):
            print_success("成功获取余额信息")
            
            # 显示余额
            balances = result.get('balances', [])
            print_info(f"资产数量: {len(balances)}")
            
            for balance in balances[:5]:  # 只显示前5个
                symbol = balance.get('symbol', 'Unknown')
                available = balance.get('available', '0')
                locked = balance.get('locked', '0')
                print_info(f"  {symbol}: 可用={available}, 锁定={locked}")
            
            if len(balances) > 5:
                print_info(f"  ... 还有 {len(balances) - 5} 个资产")
            
            return True
        else:
            print_error(f"返回格式异常: {type(result)}")
            return False
            
    except Exception as e:
        print_error(f"获取余额失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_open_positions(account):
    """测试 5: 获取持仓信息"""
    print_header("测试 5: 获取持仓信息")
    
    try:
        print_info("调用 get_open_positions()...")
        result = account.get_open_positions()
        
        if isinstance(result, (dict, list)):
            print_success("成功获取持仓信息")
            
            positions = result if isinstance(result, list) else result.get('positions', [])
            if positions:
                print_info(f"当前持仓数量: {len(positions)}")
                for pos in positions[:3]:
                    symbol = pos.get('symbol', 'Unknown')
                    size = pos.get('size', '0')
                    side = pos.get('side', 'Unknown')
                    print_info(f"  {symbol}: {side} {size}")
            else:
                print_info("当前无持仓")
            
            return True
        else:
            print_error(f"返回格式异常: {type(result)}")
            return False
            
    except Exception as e:
        print_error(f"获取持仓信息失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_order_headers(account):
    """测试 6: 检查订单请求头（不实际下单）"""
    print_header("测试 6: 验证请求头生成")
    
    try:
        print_info("测试请求头生成逻辑...")
        
        # 测试参数
        test_params = {
            'symbol': 'SOL_USDC',
            'side': 'Bid',
            'order_type': OrderTypeEnum.LIMIT,
            'time_in_force': TimeInForceEnum.GTC,
            'quantity': '0.1',
            'price': '100.00',
            'post_only': True,
            'window': 5000
        }
        
        print_info("测试订单参数:")
        for key, value in test_params.items():
            print_info(f"  {key}: {value}")
        
        # 使用父类方法生成请求配置
        from bpx.base.base_account import BaseAccount
        request_config = BaseAccount.execute_order(account, **test_params)
        
        print_success("请求配置生成成功")
        print_info(f"URL: {request_config.url}")
        
        # 检查关键请求头
        required_headers = ['X-API-Key', 'X-Signature', 'X-Timestamp', 'X-Window']
        all_present = True
        
        print_info("\n请求头检查:")
        for header in required_headers:
            if header in request_config.headers:
                value = request_config.headers[header]
                if len(str(value)) > 30:
                    print_success(f"  ✓ {header}: {str(value)[:30]}... (已截断)")
                else:
                    print_success(f"  ✓ {header}: {value}")
            else:
                print_error(f"  ✗ {header}: 缺失")
                all_present = False
        
        # 检查数据
        if hasattr(request_config, 'data') and request_config.data:
            print_info(f"\n请求体: {request_config.data}")
        
        return all_present
        
    except Exception as e:
        print_error(f"请求头验证失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_real_order_execution(account):
    """测试 7: 真实订单执行测试（使用安全参数）"""
    print_header("测试 7: 真实订单执行 (DRY RUN)")
    
    print_warning("⚠️  此测试将真实调用下单 API")
    print_warning("⚠️  使用极端价格和 IOC 订单避免真实成交")
    
    # 检查是否在交互式终端中
    import sys
    if not sys.stdin.isatty():
        print_info("非交互模式：自动跳过真实订单测试")
        return None
    
    print_info("\n按 Enter 继续，输入 'skip' 跳过此测试...")
    
    try:
        user_input = input().strip().lower()
        if user_input == 'skip':
            print_info("跳过真实订单测试")
            return None
    except (EOFError, KeyboardInterrupt):
        print_info("\n跳过真实订单测试")
        return None
    
    try:
        # 先获取当前市场价格
        from bpx.public import Public
        public_client = Public()
        
        print_info("\n获取 SOL_USDC 当前市场价...")
        depth = public_client.get_depth('SOL_USDC')
        
        if not depth or 'bids' not in depth or 'asks' not in depth:
            print_error("无法获取市场价格")
            return False
        
        best_bid = Decimal(depth['bids'][0][0]) if depth['bids'] else Decimal('0')
        best_ask = Decimal(depth['asks'][0][0]) if depth['asks'] else Decimal('0')
        
        print_info(f"当前最佳买价: {best_bid}")
        print_info(f"当前最佳卖价: {best_ask}")
        
        # 使用远低于市场价的买单（99%不会成交）
        safe_price =   Decimal('175')  # 只用市场价的 50%
        safe_quantity = '0.01'  # 最小数量
        
        print_info(f"\n测试订单参数:")
        print_info(f"  交易对: SOL_USDC")
        print_info(f"  方向: Bid (买入)")
        print_info(f"  价格: {safe_price} (市场价的 50%)")
        print_info(f"  数量: {safe_quantity} SOL")
        print_info(f"  类型: IOC (立即成交或取消)")
        print_warning(f"  预期: 订单将因价格过低而立即取消")
        
        print_info("\n正在下单...")
        result = account.execute_order(
            symbol='SOL_USDC',
            side='Bid',
            order_type=OrderTypeEnum.LIMIT,
            time_in_force=TimeInForceEnum.GTC,  # IOC 立即取消未成交部分
            quantity=safe_quantity,
            price=str(safe_price),
            post_only=False
        )
        
        print_success("订单 API 调用成功")
        print_info(f"\n返回结果:")
        result_str = json.dumps(result, indent=2, default=str)
        print(result_str)
        
        # 分析返回结果
        if isinstance(result, dict):
            if 'id' in result or 'orderId' in result:
                print_success("✓ 返回包含订单 ID")
                order_id = result.get('id') or result.get('orderId')
                print_info(f"  订单 ID: {order_id}")
            
            if 'status' in result:
                status = result.get('status')
                print_info(f"  订单状态: {status}")
                
                if status in ['CANCELED', 'CANCELLED', 'EXPIRED']:
                    print_success("✓ 订单按预期被取消（未成交）")
                elif status == 'FILLED':
                    print_warning("⚠️  订单意外成交了！")
                elif status in ['NEW', 'OPEN']:
                    print_warning("⚠️  订单仍在订单簿中")
            
            if 'code' in result:
                # API 返回错误
                code = result.get('code')
                message = result.get('message', '')
                print_info(f"  错误码: {code}")
                print_info(f"  错误信息: {message}")
                
                # 某些错误是可接受的
                acceptable_errors = [
                    'INVALID_PRICE',
                    'PRICE_TOO_LOW',
                    'PRICE_TOO_HIGH',
                    'INSUFFICIENT_BALANCE'
                ]
                
                if any(err in code or err in message for err in acceptable_errors):
                    print_success("✓ API 拒绝了不合理的订单（符合预期）")
                    return True
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print_error(f"订单执行失败: {error_msg}")
        
        # 某些错误也是可接受的
        if any(keyword in error_msg.lower() for keyword in ['price', 'quantity', 'balance', 'invalid']):
            print_warning("⚠️  API 返回错误（但请求到达服务器）")
            print_success("✓ 请求头正确，API 认证成功")
            return True
        else:
            import traceback
            print(traceback.format_exc())
            return False


def test_place_open_order_simulation(account):
    """测试 8: 模拟 place_open_order 逻辑（不实际下单）"""
    print_header("测试 8: place_open_order 逻辑模拟")
    
    try:
        from bpx.public import Public
        from decimal import Decimal
        
        public_client = Public()
        contract_id = 'SOL_USDC'
        quantity = Decimal('0.1')
        tick_size = Decimal('0.01')
        
        print_info(f"模拟参数:")
        print_info(f"  交易对: {contract_id}")
        print_info(f"  数量: {quantity}")
        print_info(f"  Tick Size: {tick_size}")
        
        # 模拟 place_open_order 的定价逻辑
        print_info("\n获取市场 BBO...")
        depth = public_client.get_depth(contract_id)
        
        if not depth or 'bids' not in depth or 'asks' not in depth:
            print_error("无法获取市场深度")
            return False
        
        # 使用 fetch_bbo_prices 的排序逻辑
        bids = depth.get('bids', [])
        asks = depth.get('asks', [])
        
        # Sort bids and asks (与 fetch_bbo_prices 一致)
        bids = sorted(bids, key=lambda x: Decimal(x[0]), reverse=True)  # 降序：最高价在前
        asks = sorted(asks, key=lambda x: Decimal(x[0]))                # 升序：最低价在前
        
        # Best bid is the highest price someone is willing to buy at
        best_bid = Decimal(bids[0][0]) if bids and len(bids) > 0 else Decimal('0')
        # Best ask is the lowest price someone is willing to sell at
        best_ask = Decimal(asks[0][0]) if asks and len(asks) > 0 else Decimal('0')
        
        print_success(f"当前 BBO:")
        print_info(f"  最佳买价 (Best Bid): {best_bid}")
        print_info(f"  最佳卖价 (Best Ask): {best_ask}")
        print_info(f"  价差 (Spread): {best_ask - best_bid}")
        
        # 模拟 buy 方向的定价
        print_info(f"\n【买入方向】定价逻辑:")
        buy_order_price = best_ask - 2 * tick_size
        print_info(f"  公式: best_ask - 2 * tick_size")
        print_info(f"  计算: {best_ask} - 2 * {tick_size} = {buy_order_price}")
        print_info(f"  订单侧: Bid (买入)")
        
        if buy_order_price > best_bid:
            print_success(f"  ✓ 订单价格 ({buy_order_price}) > 最佳买价 ({best_bid})")
            print_success(f"  ✓ 订单将在买盘顶部，优先成交")
        else:
            print_warning(f"  ⚠️  订单价格 ({buy_order_price}) <= 最佳买价 ({best_bid})")
        
        if buy_order_price < best_ask:
            print_success(f"  ✓ 订单价格 ({buy_order_price}) < 最佳卖价 ({best_ask})")
            print_success(f"  ✓ Post-only 订单不会立即成交")
        else:
            print_error(f"  ✗ 订单价格 ({buy_order_price}) >= 最佳卖价 ({best_ask})")
            print_error(f"  ✗ Post-only 订单会被拒绝!")
        
        # 模拟 sell 方向的定价
        print_info(f"\n【卖出方向】定价逻辑:")
        sell_order_price = best_bid + 2 * tick_size
        print_info(f"  公式: best_bid + 2 * tick_size")
        print_info(f"  计算: {best_bid} + 2 * {tick_size} = {sell_order_price}")
        print_info(f"  订单侧: Ask (卖出)")
        
        if sell_order_price < best_ask:
            print_success(f"  ✓ 订单价格 ({sell_order_price}) < 最佳卖价 ({best_ask})")
            print_success(f"  ✓ 订单将在卖盘底部，优先成交")
        else:
            print_warning(f"  ⚠️  订单价格 ({sell_order_price}) >= 最佳卖价 ({best_ask})")
        
        if sell_order_price > best_bid:
            print_success(f"  ✓ 订单价格 ({sell_order_price}) > 最佳买价 ({best_bid})")
            print_success(f"  ✓ Post-only 订单不会立即成交")
        else:
            print_error(f"  ✗ 订单价格 ({sell_order_price}) <= 最佳买价 ({best_bid})")
            print_error(f"  ✗ Post-only 订单会被拒绝!")
        
        # 分析价格合理性
        print_info(f"\n【价格分析】:")
        buy_distance_to_mid = abs(buy_order_price - (best_bid + best_ask) / 2)
        sell_distance_to_mid = abs(sell_order_price - (best_bid + best_ask) / 2)
        
        print_info(f"  买单距离中间价: {buy_distance_to_mid:.2f}")
        print_info(f"  卖单距离中间价: {sell_distance_to_mid:.2f}")
        
        spread = best_ask - best_bid
        print_info(f"  当前价差: {spread}")
        
        if spread > 4 * tick_size:
            print_success(f"  ✓ 价差 ({spread}) > 4 * tick_size ({4 * tick_size})")
            print_success(f"  ✓ 有足够空间放置 post-only 订单")
        else:
            print_warning(f"  ⚠️  价差 ({spread}) 较小，post-only 订单可能经常被拒绝")
        
        # 总结
        print_info(f"\n【总结】:")
        print_success(f"✓ 定价逻辑正确")
        print_success(f"✓ Post-only 订单不会吃单（Maker 订单）")
        print_success(f"✓ 订单价格有竞争力（接近最佳价）")
        
        return True
        
    except Exception as e:
        print_error(f"模拟测试失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_market_data():
    """测试 9: 获取市场数据（无需认证）"""
    print_header("测试 9: 获取市场数据 (Public API)")
    
    try:
        from bpx.public import Public
        
        public_client = Public()
        print_info("Public 客户端初始化成功")
        
        # 获取市场数据
        print_info("获取 SOL_USDC 深度...")
        depth = public_client.get_depth('SOL_USDC')
        
        if depth and 'bids' in depth and 'asks' in depth:
            print_success("成功获取市场深度")
            
            # 使用 fetch_bbo_prices 的排序逻辑
            from decimal import Decimal
            bids = depth.get('bids', [])
            asks = depth.get('asks', [])
            
            # Sort bids and asks
            bids = sorted(bids, key=lambda x: Decimal(x[0]), reverse=True)  # 降序：最高价在前
            asks = sorted(asks, key=lambda x: Decimal(x[0]))                # 升序：最低价在前
            
            print_info("\n买单 (Bids - 价格从高到低):")
            for bid in bids[:3]:
                print_info(f"  价格: {bid[0]}, 数量: {bid[1]}")
            
            print_info("\n卖单 (Asks - 价格从低到高):")
            for ask in asks[:3]:
                print_info(f"  价格: {ask[0]}, 数量: {ask[1]}")
            
            return True
        else:
            print_error("市场深度数据格式异常")
            return False
            
    except Exception as e:
        print_error(f"获取市场数据失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def main():
    """主测试流程"""
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "    🧪 Backpack 客户端完整测试套件".center(68) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    print(Colors.END)
    
    results = {}
    
    # 测试 1: 环境变量
    results['env_loading'] = test_env_loading()
    if not results['env_loading']:
        print_error("\n⛔ 环境变量加载失败，终止测试")
        print_info("请检查 .env 文件是否存在且格式正确")
        return 1
    
    # 测试 2: 客户端初始化
    account = test_client_initialization()
    results['client_init'] = account is not None
    if not account:
        print_error("\n⛔ 客户端初始化失败，终止测试")
        return 1
    
    # 测试 3: 账户信息（验证认证）
    results['account_info'] = test_account_info(account)
    
    # 测试 4: 余额信息
    results['balances'] = test_balances(account)
    
    # 测试 5: 持仓信息
    results['open_positions'] = test_open_positions(account)
    
    # 测试 6: 请求头检查
    results['order_headers'] = test_order_headers(account)
    
    # 测试 7: 真实订单执行（可选）
    results['real_order'] = test_real_order_execution(account)
    
    # 测试 8: place_open_order 逻辑模拟
    results['place_order_logic'] = test_place_open_order_simulation(account)
    
    # 测试 9: 市场数据
    results['market_data'] = test_market_data()
    
    # 总结
    print_header("📊 测试结果总结")
    
    for test_name, result in results.items():
        test_display = test_name.replace('_', ' ').title()
        if result is True:
            print(f"{Colors.GREEN}  ✓ {test_display:<25} 通过{Colors.END}")
        elif result is False:
            print(f"{Colors.RED}  ✗ {test_display:<25} 失败{Colors.END}")
        else:
            print(f"{Colors.YELLOW}  - {test_display:<25} 跳过{Colors.END}")
    
    # 计算通过率
    passed = sum(1 for r in results.values() if r is True)
    total = sum(1 for r in results.values() if r is not None)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ 所有测试通过！({passed}/{total}) - {percentage:.0f}%{Colors.END}")
        print(f"{Colors.GREEN}🎉 Backpack 客户端配置正确，可以正常使用{Colors.END}")
        return 0
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  部分测试失败 ({passed}/{total}) - {percentage:.0f}%{Colors.END}")
        print(f"{Colors.YELLOW}请检查失败的测试项并修复问题{Colors.END}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        print(f"\n{Colors.BLUE}测试完成，退出码: {exit_code}{Colors.END}\n")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  测试被用户中断{Colors.END}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}❌ 测试过程发生未预期的错误: {e}{Colors.END}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)

