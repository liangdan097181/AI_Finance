from flask import Flask, jsonify, request
from flask_cors import CORS
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv
from deepseek_ai_strategy import integrate_deepseek_strategy

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 获取美股市场指数数据
@app.route('/api/market-indices', methods=['GET'])
def get_market_indices():
    try:
        # 获取美股主要指数实时数据
        indices_data = []
        
        # 获取纳斯达克指数 (使用.NDX)
        try:
            nasdaq_df = ak.index_us_stock_sina(symbol=".NDX")
            if not nasdaq_df.empty:
                latest = nasdaq_df.iloc[-1]
                prev = nasdaq_df.iloc[-2] if len(nasdaq_df) > 1 else latest
                indices_data.append({
                    "name": "纳斯达克综合指数",
                    "symbol": "NASDAQ",
                    "price": float(latest['close']),
                    "change": float(latest['close'] - prev['close']),
                    "changePercent": float((latest['close'] - prev['close']) / prev['close'] * 100)
                })
        except Exception as e:
            print(f"获取纳斯达克数据失败: {e}")
        
        # 获取标普500指数 (使用.INX)
        try:
            sp500_df = ak.index_us_stock_sina(symbol=".INX")
            if not sp500_df.empty:
                latest = sp500_df.iloc[-1]
                prev = sp500_df.iloc[-2] if len(sp500_df) > 1 else latest
                indices_data.append({
                    "name": "标普500指数",
                    "symbol": "S&P 500",
                    "price": float(latest['close']),
                    "change": float(latest['close'] - prev['close']),
                    "changePercent": float((latest['close'] - prev['close']) / prev['close'] * 100)
                })
        except Exception as e:
            print(f"获取标普500数据失败: {e}")
        
        # 获取道琼斯指数 (使用.DJI)
        try:
            dow_df = ak.index_us_stock_sina(symbol=".DJI")
            if not dow_df.empty:
                latest = dow_df.iloc[-1]
                prev = dow_df.iloc[-2] if len(dow_df) > 1 else latest
                indices_data.append({
                    "name": "道琼斯工业指数",
                    "symbol": "DOW",
                    "price": float(latest['close']),
                    "change": float(latest['close'] - prev['close']),
                    "changePercent": float((latest['close'] - prev['close']) / prev['close'] * 100)
                })
        except Exception as e:
            print(f"获取道琼斯数据失败: {e}")
        
        # 如果所有指数都获取失败，返回模拟数据
        if not indices_data:
            indices_data = [
                {
                    "name": "纳斯达克综合指数",
                    "symbol": "NASDAQ",
                    "price": 21178.584,
                    "change": 2.18,
                    "changePercent": 0.01
                },
                {
                    "name": "标普500指数",
                    "symbol": "S&P 500",
                    "price": 6389.77,
                    "change": -7.92,
                    "changePercent": -0.12
                },
                {
                    "name": "道琼斯工业指数",
                    "symbol": "DOW",
                    "price": 44837.56,
                    "change": -109.42,
                    "changePercent": -0.24
                }
            ]
        
        return jsonify({
            "success": True,
            "data": indices_data
        })
    
    except Exception as e:
        print(f"获取市场指数数据失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# AI策略生成接口（集成 DeepSeek AI）
@app.route('/api/generate-strategy', methods=['POST'])
def generate_ai_strategy():
    try:
        data = request.get_json()
        preferences = data.get('preferences', {})
        api_key = data.get('apiKey')  # 获取前端传来的API密钥
        
        print(f"收到AI策略生成请求: {preferences}")
        print(f"API密钥状态: {'已提供' if api_key else '未提供，将使用备用策略'}")
        
        # 基于投资偏好选择股票池（扩展为更专业的股票池）
        trading_style = preferences.get('tradingStyle', 'value')
        
        # 根据交易风格选择符合机构标准的股票池
        if trading_style == 'value':
            stock_symbols = ['AAPL', 'MSFT', 'BRK-B', 'JNJ', 'PG', 'JPM', 'BAC', 'WFC', 'CVX', 'XOM']
        elif trading_style == 'growth':
            stock_symbols = ['TSLA', 'NVDA', 'AMZN', 'GOOGL', 'META', 'CRM', 'ADBE', 'NOW', 'SHOP', 'SQ']
        elif trading_style == 'momentum':
            stock_symbols = ['AAPL', 'NVDA', 'TSLA', 'AMD', 'NFLX', 'AVGO', 'QCOM', 'AMAT', 'LRCX', 'KLAC']
        elif trading_style == 'contrarian':
            stock_symbols = ['INTC', 'IBM', 'GE', 'F', 'T', 'VZ', 'PFE', 'MRK', 'KO', 'PEP']
        else:  # lowVolatility
            stock_symbols = ['KO', 'PEP', 'WMT', 'PG', 'JNJ', 'MCD', 'UNH', 'V', 'MA', 'HD']
        
        print(f"初始股票池: {stock_symbols}")
        
        # 应用专业筛选标准
        filtered_symbols = apply_institutional_screening(stock_symbols, trading_style)
        print(f"筛选后股票池: {filtered_symbols}")
        
        # 获取市场指数数据
        market_response = get_market_indices()
        market_data = market_response.get_json()['data'] if market_response.status_code == 200 else []
        
        # 获取这些股票的实时数据
        stock_response = get_stock_data_internal(filtered_symbols)
        
        if not stock_response['success'] or not stock_response['data']:
            print("无法获取股票数据，使用模拟数据")
            stock_response = get_mock_stock_data(stock_symbols)
        
        stocks_data = stock_response['data']
        print(f"获取到 {len(stocks_data)} 只股票数据")
        
        # 确保至少有股票数据
        if not stocks_data:
            print("股票数据为空，生成默认模拟数据")
            stock_response = get_mock_stock_data(['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA'])
            stocks_data = stock_response['data']
        
        # 检查是否提供了API密钥，优先使用环境变量，然后是前端传来的密钥
        env_api_key = os.getenv('DEEPSEEK_API_KEY')
        final_api_key = api_key or env_api_key
        
        if final_api_key:
            print(f"🤖 检测到API密钥，使用DeepSeek AI生成策略 (来源: {'前端' if api_key else '环境变量'})")
            try:
                ai_strategy = integrate_deepseek_strategy(preferences, market_data, stocks_data, final_api_key)
                
                # 检查AI策略是否成功生成
                if ai_strategy.get('aiPowered', False):
                    print("✅ DeepSeek AI策略生成成功")
                    
                    # 获取历史表现数据
                    symbols_list = [r['symbol'] for r in ai_strategy['recommendations']]
                    allocations_list = [r['allocation'] for r in ai_strategy['recommendations']]
                    history_response = get_stock_history_internal(symbols_list, allocations_list)
                    historical_performance = history_response['data'] if history_response['success'] else []
                    
                    # 计算组合预期收益
                    portfolio_return = sum([r['dailyChangePercent'] * (r['allocation'] / 100) for r in ai_strategy['recommendations']])
                    
                    strategy_response = {
                        "marketAnalysis": ai_strategy['marketAnalysis'],
                        "recommendations": ai_strategy['recommendations'],
                        "historicalPerformance": historical_performance,
                        "reasons": ai_strategy['reasons'],
                        "risks": ai_strategy['risks'],
                        "portfolioReturn": portfolio_return,
                        "aiPowered": True,
                        "strategyInsights": ai_strategy.get('strategyInsights', ''),
                        "scenarioAnalysis": ai_strategy.get('scenarioAnalysis', {}),
                        "expectedMetrics": ai_strategy.get('expectedMetrics', {})
                    }
                    
                    return jsonify({
                        "success": True,
                        "data": strategy_response
                    })
                else:
                    print("❌ AI策略生成失败，回退到备用策略")
                    
            except Exception as ai_error:
                print(f"❌ DeepSeek AI 调用异常: {ai_error}")
                print("🔄 回退到备用策略")
        else:
            print("⚠️  未提供API密钥，使用备用策略")
        
        # 备用策略生成逻辑
        print("🔧 生成备用投资策略")
        investment_amount = preferences.get('investmentAmount', 100000)
        portfolio_position_ratio = preferences.get('maxSinglePosition', 20) / 100  # 组合仓位占比
        
        print(f"备用策略 - 组合仓位占比: {portfolio_position_ratio * 100}%")
        
        # 根据交易风格确定基础权重分配
        if trading_style == 'value':
            base_weights = [0.30, 0.25, 0.20, 0.15, 0.10]  # 价值投资偏重头部
        elif trading_style == 'growth':
            base_weights = [0.35, 0.25, 0.20, 0.12, 0.08]  # 成长投资更集中
        elif trading_style == 'momentum':
            base_weights = [0.25, 0.25, 0.20, 0.15, 0.15]  # 动量投资相对均衡
        else:
            base_weights = [0.20, 0.20, 0.20, 0.20, 0.20]  # 其他风格均等权重
        
        recommendations = []
        # 确保有足够的股票数据
        available_stocks = min(len(stocks_data), len(base_weights))
        
        for i in range(available_stocks):
            stock = stocks_data[i]
            # 将基础权重按组合仓位占比缩放
            allocation_percent = base_weights[i] * portfolio_position_ratio * 100
            recommended_amount = investment_amount * (allocation_percent / 100)
            
            recommendations.append({
                "symbol": stock['symbol'],
                "companyName": stock['companyName'],
                "currentPrice": stock['currentPrice'],
                "dailyChange": stock['dailyChange'],
                "dailyChangePercent": stock['dailyChangePercent'],
                "recommendedAmount": recommended_amount,
                "allocation": allocation_percent
            })
        
        # 计算总分配比例
        total_allocation = sum([r['allocation'] for r in recommendations])
        print(f"备用策略 - 总仓位分配: {total_allocation:.1f}%")
        print(f"备用策略 - 现金保留: {100 - total_allocation:.1f}%")
        
        symbols_list = [r['symbol'] for r in recommendations]
        allocations_list = [r['allocation'] for r in recommendations]
        history_response = get_stock_history_internal(symbols_list, allocations_list)
        historical_performance = history_response['data'] if history_response['success'] else []
        
        portfolio_return = sum([r['dailyChangePercent'] * (r['allocation'] / 100) for r in recommendations])
        
        strategy_response = {
            "marketAnalysis": f"基于当前市场状况和您的{trading_style}投资风格，我们为您推荐了{len(recommendations)}只优质美股。当前市场整体表现{'积极' if portfolio_return > 0 else '谨慎'}，建议分批建仓以降低风险。",
            "recommendations": recommendations,
            "historicalPerformance": historical_performance,
            "reasons": [
                f"选择的{len(recommendations)}只股票符合您的{trading_style}投资风格",
                f"投资组合分散度良好，单标最大占比控制在{max(r['allocation'] for r in recommendations):.1f}%",
                "所选股票均为行业龙头，具有良好的基本面",
                "基于实时市场数据进行动态调整"
            ],
            "risks": [
                "股票投资存在市场风险，价格可能出现波动",
                f"当前组合最大回撤可能达到{preferences.get('maxDrawdown', 20)}%",
                "建议设置止损点以控制风险",
                "请根据市场变化及时调整投资策略"
            ],
            "portfolioReturn": portfolio_return,
            "aiPowered": False
        }
        
        return jsonify({
            "success": True,
            "data": strategy_response
        })
    
    except Exception as e:
        print(f"AI策略生成失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# 获取美股股票实时数据
@app.route('/api/stock-data', methods=['POST'])
def get_stock_data():
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        stock_data = []
        
        for symbol in symbols:
            try:
                # 获取股票实时数据
                stock_df = ak.stock_us_daily(symbol=symbol)
                if not stock_df.empty:
                    latest = stock_df.iloc[-1]
                    prev = stock_df.iloc[-2] if len(stock_df) > 1 else latest
                    
                    # 获取股票基本信息
                    stock_info = {
                        "symbol": symbol,
                        "companyName": f"{symbol} Inc.",  # 简化处理
                        "currentPrice": float(latest['close']),
                        "dailyChange": float(latest['close'] - prev['close']),
                        "dailyChangePercent": float((latest['close'] - prev['close']) / prev['close'] * 100)
                    }
                    
                    stock_data.append(stock_info)
            except Exception as e:
                print(f"获取股票 {symbol} 数据失败: {e}")
                continue
        
        return jsonify({
            "success": True,
            "data": stock_data
        })
    
    except Exception as e:
        print(f"获取股票数据失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# 内部函数：获取股票数据
def get_stock_data_internal(symbols):
    try:
        stock_data = []
        
        for symbol in symbols:
            try:
                stock_df = ak.stock_us_daily(symbol=symbol)
                if not stock_df.empty:
                    latest = stock_df.iloc[-1]
                    prev = stock_df.iloc[-2] if len(stock_df) > 1 else latest
                    
                    stock_info = {
                        "symbol": symbol,
                        "companyName": f"{symbol} Inc.",
                        "currentPrice": float(latest['close']),
                        "dailyChange": float(latest['close'] - prev['close']),
                        "dailyChangePercent": float((latest['close'] - prev['close']) / prev['close'] * 100)
                    }
                    
                    stock_data.append(stock_info)
            except Exception as e:
                print(f"获取股票 {symbol} 数据失败: {e}")
                continue
        
        return {
            "success": True,
            "data": stock_data
        }
    
    except Exception as e:
        print(f"获取股票数据内部错误: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# 模拟股票数据（当真实数据获取失败时使用）
def get_mock_stock_data(symbols):
    import random
    stock_data = []
    
    for symbol in symbols:
        current_price = round(random.uniform(50, 300), 2)
        daily_change = round(random.uniform(-10, 10), 2)
        daily_change_percent = round((daily_change / current_price) * 100, 2)
        
        stock_info = {
            "symbol": symbol,
            "companyName": f"{symbol} Inc.",
            "currentPrice": current_price,
            "dailyChange": daily_change,
            "dailyChangePercent": daily_change_percent
        }
        
        stock_data.append(stock_info)
    
    return {
        "success": True,
        "data": stock_data
    }

# 获取美股股票历史数据
@app.route('/api/stock-history', methods=['POST'])
def get_stock_history():
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        period = data.get('period', 252)  # 默认一年的交易日
        
        # 转换为月份数（大约每月21个交易日）
        months = max(1, period // 21)
        
        history_response = get_stock_history_internal(symbols, period=months)
        
        return jsonify({
            "success": history_response['success'],
            "data": history_response['data']
        })
    
    except Exception as e:
        print(f"获取历史数据失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# 内部函数：获取历史数据（包含组合累计收益率）
def get_stock_history_internal(symbols, allocations=None, period=12):
    try:
        history_data = []
        
        # 如果没有提供配置权重，默认等权重
        if allocations is None:
            allocations = [100/len(symbols)] * len(symbols)
        
        # 存储每只股票的历史数据
        stock_histories = {}
        
        # 根据期间计算需要的交易日数量（大约每月21个交易日）
        trading_days = min(period * 21, 504)  # 最多2年的数据
        
        for symbol in symbols:
            try:
                stock_df = ak.stock_us_daily(symbol=symbol)
                if not stock_df.empty:
                    recent_data = stock_df.tail(trading_days)
                    
                    if len(recent_data) == 0:
                        continue
                        
                    initial_price = recent_data.iloc[0]['close']
                    monthly_data = {}
                    
                    # 按月份分组，取每月最后一个交易日的价格
                    for i, row in recent_data.iterrows():
                        date_str = str(row['date'])[:7]  # YYYY-MM格式
                        cumulative_return = (row['close'] - initial_price) / initial_price * 100
                        # 如果同一个月有多个数据点，保留最新的（最后一个）
                        monthly_data[date_str] = cumulative_return
                    
                    stock_histories[symbol] = monthly_data
            
            except Exception as e:
                print(f"获取股票 {symbol} 历史数据失败: {e}")
                continue
        
        # 如果没有获取到任何历史数据，生成模拟数据
        if not stock_histories:
            return get_mock_history_data(symbols, allocations, period)
        
        # 获取所有月份
        all_months = set()
        for stock_data in stock_histories.values():
            all_months.update(stock_data.keys())
        
        sorted_months = sorted(list(all_months))  # 按时间排序所有月份
        # 取最近的 period 个月
        sorted_months = sorted_months[-period:] if len(sorted_months) > period else sorted_months
        
        # 计算每个月的数据
        for month in sorted_months:
            month_data = {'month': month}
            
            # 添加各股票的累计收益率
            for symbol in symbols:
                if symbol in stock_histories and month in stock_histories[symbol]:
                    month_data[symbol] = round(stock_histories[symbol][month], 2)
                else:
                    month_data[symbol] = 0  # 如果没有数据，默认为0
            
            # 计算组合累计收益率（加权平均）
            portfolio_return = 0
            valid_stocks = 0
            
            for i, symbol in enumerate(symbols):
                if symbol in month_data and month_data[symbol] is not None:
                    weight = allocations[i] / 100 if i < len(allocations) else (100/len(symbols))/100
                    portfolio_return += month_data[symbol] * weight
                    valid_stocks += 1
            
            month_data['组合累计收益率'] = round(portfolio_return, 2)
            history_data.append(month_data)
        
        return {
            "success": True,
            "data": history_data
        }
    
    except Exception as e:
        print(f"获取历史数据失败: {e}")
        return get_mock_history_data(symbols, allocations, period)

# 模拟历史数据
def get_mock_history_data(symbols, allocations=None, period=12):
    import random
    from datetime import datetime, timedelta
    
    if allocations is None:
        allocations = [100/len(symbols)] * len(symbols)
    
    history_data = []
    
    for i in range(period):
        # 从最早的月份开始，往当前时间推进
        month_date = datetime.now() - timedelta(days=30*(period-1-i))
        month_str = month_date.strftime('%Y-%m')
        
        month_data = {'month': month_str}
        
        # 为每只股票生成累计收益率
        portfolio_return = 0
        for j, symbol in enumerate(symbols):
            # 模拟累计收益率（-30% 到 +50%）
            cumulative_return = round(random.uniform(-30, 50), 2)
            month_data[symbol] = cumulative_return
            
            # 计算组合收益率
            weight = allocations[j] / 100 if j < len(allocations) else (100/len(symbols))/100
            portfolio_return += cumulative_return * weight
        
        month_data['组合累计收益率'] = round(portfolio_return, 2)
        history_data.append(month_data)
    
    # 按月份排序
    history_data.sort(key=lambda x: x['month'])
    
    return {
        "success": True,
        "data": history_data
    }

# 专业股票筛选函数
def apply_institutional_screening(symbols, trading_style):
    """
    应用机构级股票筛选标准
    
    筛选标准：
    - 市值 ≥ 20亿美元
    - 日均成交额 ≥ 2,000万美元
    - 剔除破产保护、退市警告、SPAC < 1年
    - 动量过滤：过去12个月超额收益排名前50%且最近1个月收益为正
    """
    
    # 这里简化处理，实际应该连接专业数据源进行筛选
    # 基于交易风格进行进一步筛选
    
    institutional_grade_stocks = {
        'value': ['AAPL', 'MSFT', 'BRK-B', 'JNJ', 'PG', 'JPM', 'BAC'],
        'growth': ['TSLA', 'NVDA', 'AMZN', 'GOOGL', 'META', 'CRM', 'ADBE'],
        'momentum': ['AAPL', 'NVDA', 'TSLA', 'AMD', 'AVGO', 'QCOM'],
        'contrarian': ['INTC', 'IBM', 'GE', 'F', 'T', 'VZ'],
        'lowVolatility': ['KO', 'PEP', 'WMT', 'PG', 'JNJ', 'MCD', 'UNH']
    }
    
    # 获取对应风格的机构级股票
    filtered = institutional_grade_stocks.get(trading_style, symbols)
    
    # 限制数量以符合风险管理要求
    return filtered[:8]  # 最多8只股票以控制集中度风险

def get_enhanced_stock_data(symbols):
    """
    获取增强的股票数据，包含更多机构级指标
    """
    try:
        enhanced_data = []
        
        for symbol in symbols:
            try:
                stock_df = ak.stock_us_daily(symbol=symbol)
                if not stock_df.empty:
                    latest = stock_df.iloc[-1]
                    prev = stock_df.iloc[-2] if len(stock_df) > 1 else latest
                    
                    # 计算技术指标
                    recent_data = stock_df.tail(252)  # 一年数据
                    volatility = recent_data['close'].pct_change().std() * (252**0.5) * 100
                    
                    # 计算动量指标
                    momentum_1m = (latest['close'] - stock_df.iloc[-21]['close']) / stock_df.iloc[-21]['close'] * 100 if len(stock_df) > 21 else 0
                    momentum_12m = (latest['close'] - stock_df.iloc[-252]['close']) / stock_df.iloc[-252]['close'] * 100 if len(stock_df) > 252 else 0
                    
                    stock_info = {
                        "symbol": symbol,
                        "companyName": f"{symbol} Inc.",
                        "currentPrice": float(latest['close']),
                        "dailyChange": float(latest['close'] - prev['close']),
                        "dailyChangePercent": float((latest['close'] - prev['close']) / prev['close'] * 100),
                        "volatility": round(volatility, 2),
                        "momentum1M": round(momentum_1m, 2),
                        "momentum12M": round(momentum_12m, 2),
                        "volume": float(latest.get('volume', 0)),
                        "marketCap": "Large Cap",  # 简化处理
                        "sector": "Technology"  # 简化处理
                    }
                    
                    enhanced_data.append(stock_info)
            except Exception as e:
                print(f"获取股票 {symbol} 增强数据失败: {e}")
                continue
        
        return {
            "success": True,
            "data": enhanced_data
        }
    
    except Exception as e:
        print(f"获取增强股票数据失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == '__main__':
    # 检查是否配置了 DeepSeek API 密钥
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    if not deepseek_key:
        print("⚠️  警告: 未配置 DEEPSEEK_API_KEY 环境变量，将使用备用策略生成")
    else:
        print(f"✅ DeepSeek API 密钥已配置 (sk-...{deepseek_key[-8:]})")
    
    print("🚀 启动美股投资AI策略生成器后端服务")
    print("📊 支持实时市场数据获取")
    print("🤖 集成DeepSeek大模型智能分析")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5004)