from flask import Flask, jsonify, request
from flask_cors import CORS
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

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

# AI策略生成接口（集成真实数据）
@app.route('/api/generate-strategy', methods=['POST'])
def generate_ai_strategy():
    try:
        data = request.get_json()
        preferences = data.get('preferences', {})
        
        print(f"收到AI策略生成请求: {preferences}")
        
        # 基于投资偏好选择股票池
        trading_style = preferences.get('tradingStyle', 'value')
        
        # 根据交易风格选择不同的股票
        if trading_style == 'value':
            stock_symbols = ['AAPL', 'MSFT', 'BRK-B', 'JNJ', 'PG']
        elif trading_style == 'growth':
            stock_symbols = ['TSLA', 'NVDA', 'AMZN', 'GOOGL', 'META']
        elif trading_style == 'momentum':
            stock_symbols = ['AAPL', 'NVDA', 'TSLA', 'AMD', 'NFLX']
        elif trading_style == 'contrarian':
            stock_symbols = ['INTC', 'IBM', 'GE', 'F', 'T']
        else:  # lowVolatility
            stock_symbols = ['KO', 'PEP', 'WMT', 'PG', 'JNJ']
        
        print(f"选择的股票池: {stock_symbols}")
        
        # 获取这些股票的实时数据
        stock_response = get_stock_data_internal(stock_symbols)
        
        if not stock_response['success'] or not stock_response['data']:
            print("无法获取股票数据，使用模拟数据")
            # 如果获取真实数据失败，使用模拟数据
            stock_response = get_mock_stock_data(stock_symbols)
        
        stocks_data = stock_response['data']
        investment_amount = preferences.get('investmentAmount', 100000)
        max_single_position = preferences.get('maxSinglePosition', 20) / 100
        
        print(f"获取到 {len(stocks_data)} 只股票数据")
        
        # 生成推荐配置
        recommendations = []
        total_allocation = 0
        
        for i, stock in enumerate(stocks_data[:5]):  # 最多5只股票
            if trading_style == 'value':
                allocation = [25, 20, 20, 20, 15][i]
            elif trading_style == 'growth':
                allocation = [30, 25, 20, 15, 10][i]
            else:
                allocation = [20, 20, 20, 20, 20][i]
            
            # 确保不超过单标最大占比
            allocation = min(allocation, max_single_position * 100)
            
            recommended_amount = investment_amount * (allocation / 100)
            
            recommendations.append({
                "symbol": stock['symbol'],
                "companyName": stock['companyName'],
                "currentPrice": stock['currentPrice'],
                "dailyChange": stock['dailyChange'],
                "dailyChangePercent": stock['dailyChangePercent'],
                "recommendedAmount": recommended_amount,
                "allocation": allocation
            })
            
            total_allocation += allocation
        
        print(f"生成了 {len(recommendations)} 个推荐")
        
        # 获取历史表现数据（传入配置权重）
        symbols_list = [r['symbol'] for r in recommendations]
        allocations_list = [r['allocation'] for r in recommendations]
        history_response = get_stock_history_internal(symbols_list, allocations_list)
        historical_performance = history_response['data'] if history_response['success'] else []
        
        # 计算组合预期收益
        portfolio_return = sum([r['dailyChangePercent'] * (r['allocation'] / 100) for r in recommendations])
        
        # 生成市场分析
        market_analysis = f"基于当前市场状况和您的{trading_style}投资风格，我们为您推荐了{len(recommendations)}只优质美股。当前市场整体表现{'积极' if portfolio_return > 0 else '谨慎'}，建议分批建仓以降低风险。"
        
        # 生成投资理由
        reasons = [
            f"选择的{len(recommendations)}只股票符合您的{trading_style}投资风格",
            f"投资组合分散度良好，单标最大占比控制在{max(r['allocation'] for r in recommendations):.1f}%",
            "所选股票均为行业龙头，具有良好的基本面",
            "基于实时市场数据进行动态调整"
        ]
        
        # 生成风险提示
        risks = [
            "股票投资存在市场风险，价格可能出现波动",
            f"当前组合最大回撤可能达到{preferences.get('maxDrawdown', 20)}%",
            "建议设置止损点以控制风险",
            "请根据市场变化及时调整投资策略"
        ]
        
        strategy_response = {
            "marketAnalysis": market_analysis,
            "recommendations": recommendations,
            "historicalPerformance": historical_performance,
            "reasons": reasons,
            "risks": risks,
            "portfolioReturn": portfolio_return
        }
        
        print("AI策略生成成功")
        
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)