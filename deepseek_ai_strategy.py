import requests
import json
from typing import Dict, List, Any
import os

class DeepSeekAIStrategy:
    def __init__(self, api_key: str = None):
        """
        初始化 DeepSeek AI 策略生成器
        
        Args:
            api_key: DeepSeek API 密钥
        """
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        
    def generate_investment_strategy(self, 
                                   preferences: Dict[str, Any], 
                                   market_data: List[Dict], 
                                   stock_data: List[Dict]) -> Dict[str, Any]:
        """
        使用 DeepSeek AI 生成投资策略
        
        Args:
            preferences: 用户投资偏好
            market_data: 市场指数数据
            stock_data: 股票数据
            
        Returns:
            AI 生成的投资策略分析
        """
        
        # 检查是否有API密钥
        if not self.api_key:
            print("未提供DeepSeek API密钥，使用备用策略")
            return {
                "success": False,
                "analysis": self._generate_fallback_analysis(preferences, stock_data)
            }
        
        # 构建提示词
        prompt = self._build_prompt(preferences, market_data, stock_data)
        
        try:
            print("正在调用DeepSeek AI生成投资策略...")
            # 调用 DeepSeek API
            response = self._call_deepseek_api(prompt)
            
            # 解析 AI 响应
            ai_analysis = self._parse_ai_response(response)
            
            print("DeepSeek AI策略生成成功")
            return {
                "success": True,
                "analysis": ai_analysis
            }
            
        except Exception as e:
            print(f"DeepSeek AI 调用失败: {e}")
            # 当有API密钥但调用失败时，仍然返回失败状态，让上层决定是否使用备用策略
            return {
                "success": False,
                "error": str(e),
                "analysis": self._generate_fallback_analysis(preferences, stock_data)
            }
    
    def _build_prompt(self, preferences: Dict, market_data: List, stock_data: List) -> str:
        """构建专业对冲基金 PM 级别的 AI 提示词"""
        
        trading_style_map = {
            'value': '价值因子驱动',
            'growth': '成长动量策略', 
            'momentum': '技术动量策略',
            'contrarian': '逆向价值策略',
            'lowVolatility': '低波动率策略'
        }
        
        style_name = trading_style_map.get(preferences.get('tradingStyle', 'value'), '价值因子驱动')
        
        prompt = f"""
你是一位常驻纽约、管理多空权益策略的对冲基金 PM，CFA/CAIA 持证，10 年美股经验，专长量化因子与事件驱动。

## 投资组合构建任务
- 资金规模: ${preferences.get('investmentAmount', 100000):,}
- 策略类型: {style_name}
- 投资模式: {'多空策略 (Long/Short)' if preferences.get('allowShortSelling', False) else '仅做多 (Long Only)'}
- 组合总仓位占比: {preferences.get('maxSinglePosition', 20)}% (剩余资金保持现金)
- 最大回撤容忍度: {preferences.get('maxDrawdown', 20)}%
- 止损比例: {preferences.get('stopLoss', 20)}%
- 特殊要求: {preferences.get('customLogic', '标准机构配置')}

## 风险约束条件
- 95% VaR ≤ 6%
- 单标权重 ≤ 7%，单行业(GICS L2) ≤ 25%
- Barra 因子暴露 |β| ≤ 0.6
- 扣除成本：0.02% 单边佣金 + 10 bps 市场冲击

## 当前市场环境
"""
        
        # 添加市场指数信息
        for index in market_data:
            change_direction = "多头信号" if index['changePercent'] > 0 else "空头信号"
            prompt += f"- {index['name']}: {index['price']:.2f} ({change_direction} {abs(index['changePercent']):.2f}%)\n"
        
        prompt += "\n## 股票池筛选标准\n"
        prompt += "- 仅限NYSE/Nasdaq/ARCA上市美股（不含ADR、ETF、ETN）\n"
        prompt += "- 市值 ≥ 20亿美元，日均成交额 ≥ 2,000万美元\n"
        prompt += "- 过去12个月超额收益排名前50%，最近1个月收益为正\n"
        prompt += "- ESG: Sustainalytics争议等级 ≤ 3\n"
        
        prompt += "\n## 候选标的实时数据\n"
        
        # 添加股票信息
        for stock in stock_data:
            momentum_signal = "动量正向" if stock['dailyChangePercent'] > 0 else "动量负向"
            prompt += f"- {stock['symbol']}: ${stock['currentPrice']:.2f} ({momentum_signal} {abs(stock['dailyChangePercent']):.2f}%)\n"
        
        prompt += f"""

## 情景分析要求
请考虑以下宏观情景对组合的影响：
1. 美联储12个月内降息150bp
2. 美国10Y利率突破5.5%
3. AI监管法案导致纳指盈利下修10%

## 输出格式（JSON）：
{{
    "marketAnalysis": "基于量化因子和宏观环境的专业分析（200-250字）",
    "portfolioConstruction": [
        {{
            "symbol": "股票代码",
            "position": "{'LONG/SHORT' if preferences.get('allowShortSelling', False) else 'LONG'}",
            "allocation": 权重百分比（数字），
            "shares": 建议股数,
            "rationale": "基于量化因子的选股逻辑（80-100字）",
            "riskMetrics": {{
                "beta": "预估Beta值",
                "volatility": "预估年化波动率%",
                "maxDrawdown": "预估最大回撤%"
            }}
        }}
    ],
    "riskManagement": [
        "基于VaR模型的风险控制措施",
        "行业集中度风险管理",
        "因子暴露度控制策略",
        "流动性风险管理方案"
    ],
    "scenarioAnalysis": {{
        "fedCut150bp": "降息情景下的组合表现预期",
        "yield5_5pct": "利率上升情景下的风险评估", 
        "aiRegulation": "AI监管情景下的行业轮动策略"
    }},
    "executionStrategy": "分批建仓和风险对冲的具体执行方案（150-200字）",
    "expectedMetrics": {{
        "annualizedReturn": "预期年化收益率%",
        "sharpeRatio": "预期夏普比率",
        "maxDrawdown": "预期最大回撤%",
        "var95": "95%置信度VaR%"
    }}
}}

## 专业要求：
1. 严格遵循机构级风险管理标准
2. 基于量化因子模型进行选股
3. 考虑交易成本和市场冲击
4. 提供可执行的对冲策略
5. 符合监管合规要求
6. 最大化税后净IRR
7. 组合仓位控制：所有股票配置的总和不得超过{preferences.get('maxSinglePosition', 20)}%，剩余资金保持现金
{'8. 多空策略：做多看涨股票，卖空看跌股票，控制净敞口' if preferences.get('allowShortSelling', False) else '8. 仅做多策略：只买入看涨股票，不进行卖空操作'}
{'9. 卖空风险管理：严格控制空头仓位，设置强制平仓线' if preferences.get('allowShortSelling', False) else '9. 风险控制：通过分散投资和止损控制风险'}
"""
        
        return prompt
    
    def _call_deepseek_api(self, prompt: str) -> str:
        """调用 DeepSeek API"""
        
        if not self.api_key:
            raise Exception("DeepSeek API 密钥未配置")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位常驻纽约的对冲基金投资组合经理(PM)，持有CFA和CAIA认证，拥有10年美股量化投资经验。你专精于多空权益策略、量化因子模型、事件驱动投资和风险管理。你的投资决策基于严格的量化分析、风险控制和合规要求，目标是在控制风险的前提下最大化税后净收益。请提供机构级别的专业投资建议。"
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 3000
        }
        
        response = requests.post(self.base_url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """解析 AI 响应"""
        try:
            # 尝试提取 JSON 部分
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("无法找到有效的 JSON 响应")
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"解析 AI 响应失败: {e}")
            print(f"原始响应: {response}")
            raise Exception("AI 响应格式错误")
    
    def _generate_fallback_analysis(self, preferences: Dict, stock_data: List) -> Dict[str, Any]:
        """生成备用分析（当 AI 调用失败时）"""
        
        trading_style = preferences.get('tradingStyle', 'value')
        allow_short = preferences.get('allowShortSelling', False)
        
        # 获取组合仓位占比
        portfolio_position_ratio = preferences.get('maxSinglePosition', 20) / 100
        
        # 根据交易风格确定基础权重分配
        if trading_style == 'value':
            base_weights = [0.30, 0.25, 0.20, 0.15, 0.10]
        elif trading_style == 'growth':
            base_weights = [0.35, 0.25, 0.20, 0.12, 0.08]
        elif trading_style == 'momentum':
            base_weights = [0.25, 0.25, 0.20, 0.15, 0.15]
        else:
            base_weights = [0.20, 0.20, 0.20, 0.20, 0.20]
        
        selected_stocks = []
        
        # 多空策略需要特殊处理仓位分配
        if allow_short:
            # 多空策略：确保总仓位等于用户设定的组合仓位占比
            # 将权重重新分配，确保多头+空头的绝对值 = 总仓位占比
            
            # 分配策略：前3只做多，后2只做空
            long_base_weights = base_weights[:3]  # 前3只的权重
            short_base_weights = base_weights[3:5]  # 后2只的权重
            
            # 计算基础权重总和
            long_base_sum = sum(long_base_weights)
            short_base_sum = sum(short_base_weights)
            total_base_sum = long_base_sum + short_base_sum
            
            # 按比例分配到总仓位
            long_weights = [w / total_base_sum for w in long_base_weights]
            short_weights = [w / total_base_sum for w in short_base_weights]
            
            # 处理做多仓位
            for i, stock in enumerate(stock_data[:3]):
                if i < len(long_weights):
                    allocation_percent = long_weights[i] * portfolio_position_ratio * 100
                    investment_amount = preferences.get('investmentAmount', 100000)
                    
                    selected_stocks.append({
                        "symbol": stock['symbol'],
                        "position": "LONG",
                        "allocation": allocation_percent,
                        "shares": int(investment_amount * allocation_percent / 100 / stock.get('currentPrice', 100)),
                        "rationale": f"基于{trading_style}投资风格选择的多头标的，预期上涨",
                        "riskMetrics": {
                            "beta": "1.0",
                            "volatility": "20%",
                            "maxDrawdown": "15%"
                        }
                    })
            
            # 处理做空仓位
            for i, stock in enumerate(stock_data[3:5]):
                if i < len(short_weights):
                    allocation_percent = short_weights[i] * portfolio_position_ratio * 100
                    investment_amount = preferences.get('investmentAmount', 100000)
                    
                    selected_stocks.append({
                        "symbol": stock['symbol'],
                        "position": "SHORT",
                        "allocation": allocation_percent,
                        "shares": int(investment_amount * allocation_percent / 100 / stock.get('currentPrice', 100)),
                        "rationale": f"基于{trading_style}投资风格选择的空头标的，预期下跌",
                        "riskMetrics": {
                            "beta": "-1.0",
                            "volatility": "25%",
                            "maxDrawdown": "20%"
                        }
                    })
        else:
            # 仅做多策略：正常分配
            for i, stock in enumerate(stock_data[:5]):
                if i < len(base_weights):
                    allocation_percent = base_weights[i] * portfolio_position_ratio * 100
                    investment_amount = preferences.get('investmentAmount', 100000)
                    
                    selected_stocks.append({
                        "symbol": stock['symbol'],
                        "position": "LONG",
                        "allocation": allocation_percent,
                        "shares": int(investment_amount * allocation_percent / 100 / stock.get('currentPrice', 100)),
                        "rationale": f"基于{trading_style}投资风格选择的多头标的",
                        "riskMetrics": {
                            "beta": "1.0",
                            "volatility": "20%",
                            "maxDrawdown": "15%"
                        }
                    })
        
        # 计算总仓位（多头+空头的绝对值）
        total_allocation = sum([abs(stock['allocation']) for stock in selected_stocks])
        
        # 计算净敞口（多头-空头）
        long_allocation = sum([stock['allocation'] for stock in selected_stocks if stock['position'] == 'LONG'])
        short_allocation = sum([stock['allocation'] for stock in selected_stocks if stock['position'] == 'SHORT'])
        net_exposure = long_allocation - short_allocation
        
        cash_ratio = 100 - total_allocation
        
        print(f"多空策略分配 - 多头: {long_allocation:.1f}%, 空头: {short_allocation:.1f}%, 净敞口: {net_exposure:.1f}%, 总仓位: {total_allocation:.1f}%")
        
        strategy_type = "多空对冲策略" if allow_short else "纯多头策略"
        
        # 构建市场分析描述
        if allow_short:
            market_analysis = f"基于当前市场状况和您的{trading_style}投资偏好，我们为您推荐了{strategy_type}组合。多头仓位{long_allocation:.1f}%，空头仓位{short_allocation:.1f}%，净敞口{net_exposure:.1f}%，总仓位{total_allocation:.1f}%，现金保留{cash_ratio:.1f}%。通过多空对冲降低市场风险，在控制回撤的同时获取超额收益。"
        else:
            market_analysis = f"基于当前市场状况和您的{trading_style}投资偏好，我们为您推荐了{strategy_type}组合。组合仓位占比{total_allocation:.1f}%，现金保留{cash_ratio:.1f}%，在控制风险的同时保持适度的市场敞口。"
        
        return {
            "marketAnalysis": market_analysis,
            "portfolioConstruction": selected_stocks,
            "riskManagement": [
                f"投资组合符合{trading_style}投资理念",
                "股票选择基于基本面分析",
                "配置比例经过风险优化",
                f"{'多空对冲降低市场风险' if allow_short else '纯多头策略适合牛市环境'}"
            ],
            "scenarioAnalysis": {
                "fedCut150bp": "降息环境下股票估值提升",
                "yield5_5pct": "利率上升对成长股影响较大",
                "aiRegulation": "监管政策影响科技股表现"
            },
            "executionStrategy": f"建议采用分批建仓的方式，控制单次投资规模。{'卖空操作需要严格风险控制，设置止损线。' if allow_short else ''}密切关注市场变化，适时调整投资策略。",
            "expectedMetrics": {
                "annualizedReturn": "12-15%",
                "sharpeRatio": "1.2-1.5",
                "maxDrawdown": f"{preferences.get('maxDrawdown', 20)}%",
                "var95": "5-6%"
            }
        }

# 使用示例
def integrate_deepseek_strategy(preferences: Dict, market_data: List, stock_data: List, api_key: str = None) -> Dict:
    """
    集成 DeepSeek AI 策略生成
    
    Args:
        preferences: 用户偏好
        market_data: 市场数据
        stock_data: 股票数据
        api_key: DeepSeek API密钥
        
    Returns:
        增强的投资策略
    """
    
    # 初始化 DeepSeek AI，优先使用前端传来的API密钥
    ai_strategy = DeepSeekAIStrategy(api_key=api_key)
    
    # 生成 AI 策略
    ai_result = ai_strategy.generate_investment_strategy(preferences, market_data, stock_data)
    
    if ai_result['success']:
        print("使用DeepSeek AI生成的策略")
        ai_analysis = ai_result['analysis']
        
        # 将 AI 分析转换为现有格式
        recommendations = []
        investment_amount = preferences.get('investmentAmount', 100000)
        portfolio_position_ratio = preferences.get('maxSinglePosition', 20) / 100  # 组合仓位占比
        
        print(f"AI策略集成 - 组合仓位占比: {portfolio_position_ratio * 100}%")
        
        # 处理新的 portfolioConstruction 格式
        portfolio_data = ai_analysis.get('portfolioConstruction', ai_analysis.get('stockSelection', []))
        
        if portfolio_data:
            # 计算 AI 推荐的总权重
            ai_total_weight = sum([stock.get('allocation', 0) for stock in portfolio_data])
            print(f"AI 推荐总权重: {ai_total_weight}%")
            
            # 如果 AI 推荐的总权重超过用户设定的组合仓位占比，需要按比例缩放
            if ai_total_weight > 0:
                scale_factor = (portfolio_position_ratio * 100) / ai_total_weight
                print(f"权重缩放因子: {scale_factor:.3f}")
            else:
                scale_factor = 1.0
            
            for stock_selection in portfolio_data:
                symbol = stock_selection['symbol']
                ai_allocation = stock_selection.get('allocation', 0)
                # 按用户设定的组合仓位占比缩放
                scaled_allocation = ai_allocation * scale_factor
                position = stock_selection.get('position', 'LONG')
                
                # 找到对应的股票数据
                stock_info = next((s for s in stock_data if s['symbol'] == symbol), None)
                if stock_info:
                    recommended_amount = investment_amount * (scaled_allocation / 100)
                    shares = stock_selection.get('shares', int(recommended_amount / stock_info['currentPrice']))
                    
                    recommendations.append({
                        "symbol": symbol,
                        "companyName": stock_info['companyName'],
                        "currentPrice": stock_info['currentPrice'],
                        "dailyChange": stock_info['dailyChange'],
                        "dailyChangePercent": stock_info['dailyChangePercent'],
                        "recommendedAmount": recommended_amount,
                        "allocation": scaled_allocation,
                        "position": position,
                        "shares": shares,
                        "aiReason": stock_selection.get('rationale', stock_selection.get('reason', '')),
                        "riskMetrics": stock_selection.get('riskMetrics', {})
                    })
            
            # 验证总分配
            total_allocation = sum([r['allocation'] for r in recommendations])
            print(f"AI策略最终总分配: {total_allocation:.1f}%")
            print(f"AI策略现金保留: {100 - total_allocation:.1f}%")
        
        return {
            "marketAnalysis": ai_analysis['marketAnalysis'],
            "recommendations": recommendations,
            "reasons": ai_analysis.get('investmentReasons', ai_analysis.get('riskManagement', [])),
            "risks": ai_analysis.get('riskWarnings', ai_analysis.get('riskManagement', [])),
            "strategyInsights": ai_analysis.get('strategyInsights', ai_analysis.get('executionStrategy', '')),
            "scenarioAnalysis": ai_analysis.get('scenarioAnalysis', {}),
            "expectedMetrics": ai_analysis.get('expectedMetrics', {}),
            "aiPowered": True,
            "professionalGrade": True
        }
    else:
        print("DeepSeek AI调用失败，使用备用策略")
        # 使用备用分析，需要转换为recommendations格式
        backup_analysis = ai_result['analysis']
        
        # 将备用分析的portfolioConstruction转换为recommendations
        recommendations = []
        portfolio_construction = backup_analysis.get('portfolioConstruction', [])
        
        for stock_selection in portfolio_construction:
            symbol = stock_selection['symbol']
            position = stock_selection.get('position', 'LONG')
            allocation = stock_selection.get('allocation', 0)
            
            # 找到对应的股票数据
            stock_info = next((s for s in stock_data if s['symbol'] == symbol), None)
            if stock_info:
                investment_amount = preferences.get('investmentAmount', 100000)
                recommended_amount = investment_amount * (allocation / 100)
                shares = stock_selection.get('shares', int(recommended_amount / stock_info['currentPrice']))
                
                recommendations.append({
                    "symbol": symbol,
                    "companyName": stock_info['companyName'],
                    "currentPrice": stock_info['currentPrice'],
                    "dailyChange": stock_info['dailyChange'],
                    "dailyChangePercent": stock_info['dailyChangePercent'],
                    "recommendedAmount": recommended_amount,
                    "allocation": allocation,
                    "position": position,
                    "shares": shares,
                    "aiReason": stock_selection.get('rationale', ''),
                    "riskMetrics": stock_selection.get('riskMetrics', {})
                })
        
        return {
            "marketAnalysis": backup_analysis['marketAnalysis'],
            "recommendations": recommendations,
            "reasons": backup_analysis.get('riskManagement', []),
            "risks": backup_analysis.get('riskManagement', []),
            "strategyInsights": backup_analysis.get('executionStrategy', ''),
            "scenarioAnalysis": backup_analysis.get('scenarioAnalysis', {}),
            "expectedMetrics": backup_analysis.get('expectedMetrics', {}),
            "aiPowered": False,
            "professionalGrade": True
        }