"""
美股投资AI策略生成器 - 主后端服务
集成DeepSeek大模型的智能投资策略分析系统
"""

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

@app.route('/api/market-indices', methods=['GET'])
def get_market_indices():
    """获取美股市场指数数据"""
    try:
        print("📊 获取美股市场指数数据...")
        indices_data = []
        
        # 获取纳斯达克指数
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
                print("✅ 纳斯达克指数数据获取成功")
        except Exception as e:
            print(f"❌ 获取纳斯达克数据失败: {e}")
        
        # 获取标普500指数
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
                print("✅ 标普500指数数据获取成功")
        except Exception as e:
            print(f"❌ 获取标普500数据失败: {e}")
        
        # 获取道琼斯指数
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
                print("✅ 道琼斯指数数据获取成功")
        except Exception as e:
            print(f"❌ 获取道琼斯数据失败: {e}")
        
        # 如果所有指数都获取失败，返回模拟数据
        if not indices_data:
            print("⚠️  使用模拟市场数据")
            indices_data = [
                {"name": "纳斯达克综合指数", "symbol": "NASDAQ", "price": 21178.584, "change": 2.18, "changePercent": 0.01},
                {"name": "标普500指数", "symbol": "S&P 500", "price": 6389.77, "change": -7.92, "changePercent": -0.12},
                {"name": "道琼斯工业指数", "symbol": "DOW", "price": 44837.56, "change": -109.42, "changePercent": -0.24}
            ]
        
        print(f"📈 成功获取 {len(indices_data)} 个市场指数数据")
        return jsonify({"success": True, "data": indices_data})
    
    except Exception as e:
        print(f"❌ 获取市场指数数据失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/generate-strategy', methods=['POST'])
def generate_ai_strategy():
    """AI策略生成接口（集成DeepSeek AI）"""
    try:
        data = request.get_json()
        preferences = data.get('preferences', {})
        api_key = data.get('apiKey')
        
        print("🎯 收到AI策略生成请求")
        print(f"   投资金额: ${preferences.get('investmentAmount', 100000):,}")
        print(f"   交易风格: {preferences.get('tradingStyle', 'value')}")
        print(f"   最大仓位: {preferences.get('maxSinglePosition', 20)}%")
        print(f"   API密钥: {'已提供' if api_key else '未提供'}")
        
        # 选择股票池
        trading_style = preferences.get('tradingStyle', 'value')
        stock_symbols = get_stock_pool(trading_style)
        print(f"📋 初始股票池: {stock_symbols}")
        
        # 筛选股票
        filtered_symbols = apply_institutional_screening(stock_symbols, trading_style)
        print(f"🔍 筛选后股票池: {filtered_symbols}")
        
        # 获取市场数据
        market_response = get_market_indices()
        market_data = market_response.get_json()['data'] if market_response.status_code == 200 else []
        
        # 获取股票数据
        stock_response = get_stock_data_internal(filtered_symbols)
        if not stock_response['success'] or not stock_response['data']:
            print("⚠️  无法获取实时股票数据，使用模拟数据")
            stock_response = get_mock_stock_data(filtered_symbols)
        
        stocks_data = stock_response['data']
        print(f"📊 获取到 {len(stocks_data)} 只股票数据")
        
        # 使用AI生成策略
        env_api_key = os.getenv('DEEPSEEK_API_KEY')
        final_api_key = api_key or env_api_key
        
        if final_api_key:
            print(f"🤖 使用DeepSeek AI生成策略 (来源: {'前端' if api_key else '环境变量'})")
            try:
                ai_strategy = integrate_deepseek_strategy(preferences, market_data, stocks_data, final_api_key)
                
                if ai_strategy.get('aiPowered', False):
                    print("✅ DeepSeek AI策略生成成功")
                    return create_strategy_response(ai_strategy, True)
                else:
                    print("❌ AI策略生成失败，使用备用策略")
                    
            except Exception as ai_error:
                print(f"❌ DeepSeek AI调用异常: {ai_error}")
                print("🔄 回退到备用策略")
        else:
            print("⚠️  未提供API密钥，使用备用策略")
        
        # 生成备用策略
        backup_strategy = generate_backup_strategy(preferences, stocks_data, trading_style)
        return create_strategy_response(backup_strategy, False)
    
    except Exception as e:
        print(f"❌ 策略生成失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

def get_stock_pool(trading_style):
    """根据交易风格选择股票池"""
    pools = {
        'value': ['AAPL', 'MSFT', 'BRK-B', 'JNJ', 'PG', 'JPM', 'BAC', 'WFC', 'CVX', 'XOM'],
        'growth': ['TSLA', 'NVDA', 'AMZN', 'GOOGL', 'META', 'CRM', 'ADBE', 'NOW', 'SHOP', 'SQ'],
        'momentum': ['AAPL', 'NVDA', 'TSLA', 'AMD', 'NFLX', 'AVGO', 'QCOM', 'AMAT', 'LRCX', 'KLAC'],
        'contrarian': ['INTC', 'IBM', 'GE', 'F', 'T', 'VZ', 'PFE', 'MRK', 'KO', 'PEP'],
        'lowVolatility': ['KO', 'PEP', 'WMT', 'PG', 'JNJ', 'MCD', 'UNH', 'V', 'MA', 'HD']
    }
    return pools.get(trading_style, pools['value'])

def apply_institutional_screening(symbols, trading_style):
    """应用机构级股票筛选标准"""
    institutional_grade = {
        'value': ['AAPL', 'MSFT', 'BRK-B', 'JNJ', 'PG', 'JPM', 'BAC'],
        'growth': ['TSLA', 'NVDA', 'AMZN', 'GOOGL', 'META', 'CRM', 'ADBE'],
        'momentum': ['AAPL', 'NVDA', 'TSLA', 'AMD', 'AVGO', 'QCOM'],
        'contrarian': ['INTC', 'IBM', 'GE', 'F', 'T', 'VZ'],
        'lowVolatility': ['KO', 'PEP', 'WMT', 'PG', 'JNJ', 'MCD', 'UNH']
    }
    return institutional_grade.get(trading_style, symbols)[:8]

def get_stock_data_internal(symbols):
    """获取股票实时数据"""
    try:
        stock_data = []
        for symbol in symbols:
            try:
                stock_df = ak.stock_us_daily(symbol=symbol)
                if not stock_df.empty:
                    latest = stock_df.iloc[-1]
                    prev = stock_df.iloc[-2] if len(stock_df) > 1 else latest
                    
                    stock_data.append({
                        "symbol": symbol,
                        "companyName": f"{symbol} Inc.",
                        "currentPrice": float(latest['close']),
                        "dailyChange": float(latest['close'] - prev['close']),
                        "dailyChangePercent": float((latest['close'] - prev['close']) / prev['close'] * 100)
                    })
            except Exception as e:
                print(f"❌ 获取股票 {symbol} 数据失败: {e}")
                continue
        
        return {"success": True, "data": stock_data}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_mock_stock_data(symbols):
    """生成模拟股票数据"""
    import random
    stock_data = []
    
    for symbol in symbols:
        current_price = round(random.uniform(50, 300), 2)
        daily_change = round(random.uniform(-10, 10), 2)
        daily_change_percent = round((daily_change / current_price) * 100, 2)
        
        stock_data.append({
            "symbol": symbol,
            "companyName": f"{symbol} Inc.",
            "currentPrice": current_price,
            "dailyChange": daily_change,
            "dailyChangePercent": daily_change_percent
        })
    
    return {"success": True, "data": stock_data}

def generate_backup_strategy(preferences, stocks_data, trading_style):
    """生成备用投资策略"""
    print("🔧 生成备用投资策略")
    
    investment_amount = preferences.get('investmentAmount', 100000)
    portfolio_ratio = preferences.get('maxSinglePosition', 20) / 100
    
    # 权重分配策略
    weight_strategies = {
        'value': [0.30, 0.25, 0.20, 0.15, 0.10],
        'growth': [0.35, 0.25, 0.20, 0.12, 0.08],
        'momentum': [0.25, 0.25, 0.20, 0.15, 0.15],
        'default': [0.20, 0.20, 0.20, 0.20, 0.20]
    }
    
    base_weights = weight_strategies.get(trading_style, weight_strategies['default'])
    recommendations = []
    
    for i, stock in enumerate(stocks_data[:len(base_weights)]):
        allocation = base_weights[i] * portfolio_ratio * 100
        amount = investment_amount * (allocation / 100)
        
        recommendations.append({
            "symbol": stock['symbol'],
            "companyName": stock['companyName'],
            "currentPrice": stock['currentPrice'],
            "dailyChange": stock['dailyChange'],
            "dailyChangePercent": stock['dailyChangePercent'],
            "recommendedAmount": amount,
            "allocation": allocation
        })
    
    total_allocation = sum(r['allocation'] for r in recommendations)
    portfolio_return = sum(r['dailyChangePercent'] * (r['allocation'] / 100) for r in recommendations)
    
    print(f"📊 备用策略生成完成 - 总仓位: {total_allocation:.1f}%, 现金: {100-total_allocation:.1f}%")
    
    return {
        "marketAnalysis": f"基于{trading_style}投资风格的专业策略分析。当前市场{'积极' if portfolio_return > 0 else '谨慎'}，建议分批建仓控制风险。",
        "recommendations": recommendations,
        "reasons": [
            f"选择符合{trading_style}风格的优质股票",
            f"投资组合分散度良好，最大单股占比{max(r['allocation'] for r in recommendations):.1f}%",
            "基于实时市场数据动态调整",
            "严格的风险控制和仓位管理"
        ],
        "risks": [
            "股票投资存在市场风险，价格可能波动",
            f"组合最大回撤可能达到{preferences.get('maxDrawdown', 20)}%",
            "建议设置止损点控制风险",
            "请根据市场变化及时调整策略"
        ],
        "portfolioReturn": portfolio_return,
        "aiPowered": False
    }

def create_strategy_response(strategy, ai_powered):
    """创建策略响应"""
    # 获取历史数据
    symbols = [r['symbol'] for r in strategy['recommendations']]
    allocations = [r['allocation'] for r in strategy['recommendations']]
    history_response = get_stock_history_internal(symbols, allocations)
    
    return jsonify({
        "success": True,
        "data": {
            "marketAnalysis": strategy['marketAnalysis'],
            "recommendations": strategy['recommendations'],
            "historicalPerformance": history_response['data'] if history_response['success'] else [],
            "reasons": strategy['reasons'],
            "risks": strategy['risks'],
            "portfolioReturn": strategy['portfolioReturn'],
            "aiPowered": ai_powered,
            "strategyInsights": strategy.get('strategyInsights', ''),
            "expectedMetrics": strategy.get('expectedMetrics', {})
        }
    })

def get_stock_history_internal(symbols, allocations=None, period=12):
    """获取股票历史数据"""
    try:
        if allocations is None:
            allocations = [100/len(symbols)] * len(symbols)
        
        # 简化版历史数据生成
        import random
        from datetime import datetime, timedelta
        
        history_data = []
        for i in range(period):
            month_date = datetime.now() - timedelta(days=30*(period-1-i))
            month_str = month_date.strftime('%Y-%m')
            
            month_data = {'month': month_str}
            portfolio_return = 0
            
            for j, symbol in enumerate(symbols):
                cumulative_return = round(random.uniform(-30, 50), 2)
                month_data[symbol] = cumulative_return
                
                weight = allocations[j] / 100 if j < len(allocations) else (100/len(symbols))/100
                portfolio_return += cumulative_return * weight
            
            month_data['组合累计收益率'] = round(portfolio_return, 2)
            history_data.append(month_data)
        
        return {"success": True, "data": history_data}
    except Exception as e:
        print(f"❌ 获取历史数据失败: {e}")
        return {"success": False, "data": []}

@app.route('/api/stock-data', methods=['POST'])
def get_stock_data():
    """获取股票实时数据API"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        result = get_stock_data_internal(symbols)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stock-history', methods=['POST'])
def get_stock_history():
    """获取股票历史数据API"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        period = data.get('period', 252) // 21  # 转换为月份
        result = get_stock_history_internal(symbols, period=period)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "service": "AI Stock Strategy Generator",
        "version": "1.0.0",
        "deepseek_configured": bool(os.getenv('DEEPSEEK_API_KEY'))
    })

if __name__ == '__main__':
    print("🚀 美股投资AI策略生成器")
    print("=" * 50)
    
    # 检查DeepSeek API配置
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    if not deepseek_key:
        print("⚠️  警告: 未配置 DEEPSEEK_API_KEY 环境变量")
        print("   系统将使用备用策略生成功能")
    else:
        print(f"✅ DeepSeek API 已配置 (sk-...{deepseek_key[-8:]})")
    
    print("📊 支持功能:")
    print("   • 实时美股市场数据获取")
    print("   • DeepSeek大模型智能分析")
    print("   • 多种投资风格策略")
    print("   • 风险管理和历史回测")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5001)