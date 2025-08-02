from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 模拟数据生成函数
def generate_mock_stock_data(symbol, days=30):
    """生成模拟股票数据"""
    base_price = random.uniform(50, 300)
    dates = []
    prices = []
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days-i)
        dates.append(date.strftime('%Y-%m-%d'))
        
        # 模拟价格波动
        if i == 0:
            price = base_price
        else:
            change = random.uniform(-0.05, 0.05)  # -5% 到 +5% 的变化
            price = prices[-1] * (1 + change)
        
        prices.append(round(price, 2))
    
    return dates, prices

# 获取美股市场指数数据
@app.route('/api/market-indices', methods=['GET'])
def get_market_indices():
    try:
        # 模拟美股主要指数数据
        indices_data = [
            {
                "name": "纳斯达克综合指数",
                "symbol": "NASDAQ",
                "price": round(random.uniform(15000, 16000), 2),
                "change": round(random.uniform(-200, 200), 2),
                "changePercent": round(random.uniform(-2, 2), 2)
            },
            {
                "name": "标普500指数",
                "symbol": "S&P 500",
                "price": round(random.uniform(4500, 5000), 2),
                "change": round(random.uniform(-50, 50), 2),
                "changePercent": round(random.uniform(-1.5, 1.5), 2)
            },
            {
                "name": "道琼斯工业指数",
                "symbol": "DOW",
                "price": round(random.uniform(35000, 37000), 2),
                "change": round(random.uniform(-300, 300), 2),
                "changePercent": round(random.uniform(-1, 1), 2)
            }
        ]
        
        return jsonify({
            "success": True,
            "data": indices_data
        })
    
    except Exception as e:
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
                # 生成模拟股票数据
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
            except Exception as e:
                print(f"获取股票 {symbol} 数据失败: {e}")
                continue
        
        return jsonify({
            "success": True,
            "data": stock_data
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# AI策略生成接口
@app.route('/api/generate-strategy', methods=['POST'])
def generate_ai_strategy():
    try:
        data = request.get_json()
        preferences = data.get('preferences', {})
        
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
        
        # 获取这些股票的模拟数据
        stock_response = get_stock_data_internal(stock_symbols)
        
        if not stock_response['success']:
            raise Exception("无法获取股票数据")
        
        stocks_data = stock_response['data']
        investment_amount = preferences.get('investmentAmount', 100000)
        max_single_position = preferences.get('maxSinglePosition', 20) / 100
        
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
        
        # 生成模拟历史表现数据
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
        
        return jsonify({
            "success": True,
            "data": strategy_response
        })
    
    except Exception as e:
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
            except Exception as e:
                print(f"获取股票 {symbol} 数据失败: {e}")
                continue
        
        return {
            "success": True,
            "data": stock_data
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# 内部函数：获取历史数据
def get_stock_history_internal(symbols, allocations=None, period=12):
    try:
        history_data = []
        
        # 如果没有提供配置权重，默认等权重
        if allocations is None:
            allocations = [100/len(symbols)] * len(symbols)
        
        # 生成过去12个月的模拟数据
        for i in range(period):
            month_date = datetime.now() - timedelta(days=30*i)
            month_str = month_date.strftime('%Y-%m')
            
            month_data = {'month': month_str}
            
            # 为每只股票生成累计收益率
            portfolio_return = 0
            for j, symbol in enumerate(symbols):
                # 模拟累计收益率（-30% 到 +50%）
                cumulative_return = random.uniform(-30, 50)
                month_data[symbol] = round(cumulative_return, 2)
                
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
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)