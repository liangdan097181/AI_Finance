import requests
import json
from typing import Dict, List, Any
import os

class KimiAIStrategy:
    def __init__(self, api_key: str = None):
        """
        初始化 Kimi AI 策略生成器
        
        Args:
            api_key: Kimi API 密钥
        """
        self.api_key = api_key or os.getenv('KIMI_API_KEY')
        self.base_url = "https://api.moonshot.cn/v1/chat/completions"
        
    def generate_investment_strategy(self, 
                                   preferences: Dict[str, Any], 
                                   market_data: List[Dict], 
                                   stock_data: List[Dict]) -> Dict[str, Any]:
        """
        使用 Kimi AI 生成投资策略
        
        Args:
            preferences: 用户投资偏好
            market_data: 市场指数数据
            stock_data: 股票数据
            
        Returns:
            AI 生成的投资策略分析
        """
        
        # 检查是否有API密钥
        if not self.api_key:
            print("未提供Kimi API密钥，使用备用策略")
            return {
                "success": False,
                "analysis": self._generate_fallback_analysis(preferences, stock_data)
            }
        
        # 构建提示词
        prompt = self._build_prompt(preferences, market_data, stock_data)
        
        try:
            print("正在调用Kimi AI生成投资策略...")
            # 调用 Kimi API
            response = self._call_kimi_api(prompt)
            
            # 解析 AI 响应
            ai_analysis = self._parse_ai_response(response)
            
            print("Kimi AI策略生成成功")
            return {
                "success": True,
                "analysis": ai_analysis
            }
            
        except Exception as e:
            print(f"Kimi AI 调用失败: {e}")
            # 当有API密钥但调用失败时，仍然返回失败状态，让上层决定是否使用备用策略
            return {
                "success": False,
                "error": str(e),
                "analysis": self._generate_fallback_analysis(preferences, stock_data)
            }
    
    def _build_prompt(self, preferences: Dict, market_data: List, stock_data: List) -> str:
        """构建专业投资分析师级别的 AI 提示词"""
        
        trading_style_map = {
            'value': '价值投资策略',
            'growth': '成长投资策略', 
            'momentum': '动量投资策略',
            'contrarian': '逆向投资策略',
            'lowVolatility': '低波动率策略'
        }
        
        style_name = trading_style_map.get(preferences.get('tradingStyle', 'value'), '价值投资策略')
        
        prompt = f"""
你是一位资深的美股投资分析师，拥有CFA认证和10年以上的投资经验，专精于量化分析和投资组合管理。

## 投资组合构建任务
- 资金规模: ${preferences.get('investmentAmount', 100000):,}
- 投资策略: {style_name}
- 投资模式: {'多空策略 (Long/Short)' if preferences.get('allowShortSelling', False) else '仅做多 (Long Only)'}
- 组合总仓位占比: {preferences.get('maxSinglePosition', 20)}% (剩余资金保持现金)
- 最大回撤容忍度: {preferences.get('maxDrawdown', 20)}%
- 止损比例: {preferences.get('stopLoss', 20)}%
- 特殊要求: {preferences.get('customLogic', '标准投资配置')}

## 风险管理要求
- 单只股票权重不超过7%
- 行业集中度控制在合理范围内
- 考虑交易成本和流动性风险
- 设置合理的止损和止盈点位

## 当前市场环境分析
"""
        
        # 添加市场指数信息
        for index in market_data:
            trend = "上涨趋势" if index['changePercent'] > 0 else "下跌趋势"
            prompt += f"- {index['name']}: {index['price']:.2f} ({trend} {abs(index['changePercent']):.2f}%)\n"
        
        prompt += "\n## 候选股票池数据\n"
        
        # 添加股票信息
        for stock in stock_data:
            trend = "上涨" if stock['dailyChangePercent'] > 0 else "下跌"
            prompt += f"- {stock['symbol']}: ${stock['currentPrice']:.2f} (今日{trend} {abs(stock['dailyChangePercent']):.2f}%)\n"
        
        prompt += f"""

## 分析要求
请基于以上信息，为用户生成专业的投资策略分析，包括：

1. 市场环境分析（150-200字）
2. 股票选择和配置建议
3. 风险控制措施
4. 投资执行策略

## 输出格式（JSON）：
{{
    "marketAnalysis": "基于当前市场环境和宏观因素的专业分析",
    "stockSelection": [
        {{
            "symbol": "股票代码",
            "position": "{'LONG/SHORT' if preferences.get('allowShortSelling', False) else 'LONG'}",
            "allocation": 权重百分比（数字），
            "shares": 建议股数,
            "reason": "选择该股票的投资逻辑和分析依据",
            "riskLevel": "风险等级（低/中/高）"
        }}
    ],
    "investmentReasons": [
        "投资理由1",
        "投资理由2",
        "投资理由3"
    ],
    "riskWarnings": [
        "风险提示1",
        "风险提示2", 
        "风险提示3"
    ],
    "strategyInsights": "投资策略的核心洞察和执行建议",
    "expectedMetrics": {{
        "expectedReturn": "预期年化收益率",
        "riskLevel": "整体风险水平",
        "timeHorizon": "建议持有期限"
    }}
}}

## 专业要求：
1. 基于基本面和技术面分析进行选股
2. 考虑宏观经济环境对投资的影响
3. 提供可执行的投资建议
4. 严格控制风险，符合用户风险偏好
5. 组合仓位控制：所有股票配置的总和不得超过{preferences.get('maxSinglePosition', 20)}%，剩余资金保持现金
{'6. 多空策略：做多看涨股票，卖空看跌股票，控制净敞口在合理范围' if preferences.get('allowShortSelling', False) else '6. 仅做多策略：只买入看涨股票，通过分散投资控制风险'}
7. 考虑流动性和交易成本
8. 提供明确的风险管理措施
"""
        
        return prompt
    
    def _call_kimi_api(self, prompt: str) -> str:
        """调用 Kimi API"""
        
        if not self.api_key:
            raise Exception("Kimi API 密钥未配置")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "moonshot-v1-8k",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位资深的美股投资分析师，拥有CFA认证和10年以上的投资经验。你专精于量化分析、投资组合管理和风险控制。你的投资建议基于严格的基本面分析、技术分析和风险管理原则，目标是在控制风险的前提下为客户创造稳健的投资回报。请提供专业、可执行的投资建议。"
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
            # 多空策略：前3只做多，后2只做空
            long_base_weights = base_weights[:3]
            short_base_weights = base_weights[3:5]
            
            long_base_sum = sum(long_base_weights)
            short_base_sum = sum(short_base_weights)
            total_base_sum = long_base_sum + short_base_sum
            
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
                        "reason": f"基于{trading_style}策略选择的多头标的，预期表现良好",
                        "riskLevel": "中"
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
                        "reason": f"基于{trading_style}策略选择的空头标的，预期回调",
                        "riskLevel": "高"
                    })
        else:
            # 仅做多策略
            for i, stock in enumerate(stock_data[:5]):
                if i < len(base_weights):
                    allocation_percent = base_weights[i] * portfolio_position_ratio * 100
                    investment_amount = preferences.get('investmentAmount', 100000)
                    
                    selected_stocks.append({
                        "symbol": stock['symbol'],
                        "position": "LONG",
                        "allocation": allocation_percent,
                        "shares": int(investment_amount * allocation_percent / 100 / stock.get('currentPrice', 100)),
                        "reason": f"基于{trading_style}策略选择的优质标的",
                        "riskLevel": "中"
                    })
        
        # 计算总仓位
        total_allocation = sum([abs(stock['allocation']) for stock in selected_stocks])
        long_allocation = sum([stock['allocation'] for stock in selected_stocks if stock['position'] == 'LONG'])
        short_allocation = sum([stock['allocation'] for stock in selected_stocks if stock['position'] == 'SHORT'])
        net_exposure = long_allocation - short_allocation
        cash_ratio = 100 - total_allocation
        
        strategy_type = "多空对冲策略" if allow_short else "纯多头策略"
        
        if allow_short:
            market_analysis = f"基于当前市场状况和您的{trading_style}投资偏好，我们为您推荐了{strategy_type}组合。多头仓位{long_allocation:.1f}%，空头仓位{short_allocation:.1f}%，净敞口{net_exposure:.1f}%，总仓位{total_allocation:.1f}%，现金保留{cash_ratio:.1f}%。通过多空对冲降低市场风险，在控制回撤的同时获取超额收益。"
        else:
            market_analysis = f"基于当前市场状况和您的{trading_style}投资偏好，我们为您推荐了{strategy_type}组合。组合仓位占比{total_allocation:.1f}%，现金保留{cash_ratio:.1f}%，在控制风险的同时保持适度的市场敞口。"
        
        return {
            "marketAnalysis": market_analysis,
            "stockSelection": selected_stocks,
            "investmentReasons": [
                f"选择的股票符合您的{trading_style}投资风格",
                f"投资组合分散度良好，风险控制合理",
                "所选股票均为行业优质标的，具有良好的基本面",
                "基于实时市场数据进行动态调整"
            ],
            "riskWarnings": [
                "股票投资存在市场风险，价格可能出现波动",
                f"当前组合最大回撤可能达到{preferences.get('maxDrawdown', 20)}%",
                "建议设置止损点以控制风险",
                "请根据市场变化及时调整投资策略"
            ],
            "strategyInsights": f"建议采用分批建仓的方式，控制单次投资规模。{'卖空操作需要严格风险控制，设置止损线。' if allow_short else ''}密切关注市场变化，适时调整投资策略。",
            "expectedMetrics": {
                "expectedReturn": "12-15%",
                "riskLevel": "中等",
                "timeHorizon": "6-12个月"
            }
        }

# 使用示例
def integrate_kimi_strategy(preferences: Dict, market_data: List, stock_data: List, api_key: str = None) -> Dict:
    """
    集成 Kimi AI 策略生成
    
    Args:
        preferences: 用户偏好
        market_data: 市场数据
        stock_data: 股票数据
        api_key: Kimi API密钥
        
    Returns:
        增强的投资策略
    """
    
    # 初始化 Kimi AI，优先使用前端传来的API密钥
    ai_strategy = KimiAIStrategy(api_key=api_key)
    
    # 生成 AI 策略
    ai_result = ai_strategy.generate_investment_strategy(preferences, market_data, stock_data)
    
    if ai_result['success']:
        print("使用Kimi AI生成的策略")
        ai_analysis = ai_result['analysis']
        
        # 将 AI 分析转换为现有格式
        recommendations = []
        investment_amount = preferences.get('investmentAmount', 100000)
        portfolio_position_ratio = preferences.get('maxSinglePosition', 20) / 100
        
        print(f"AI策略集成 - 组合仓位占比: {portfolio_position_ratio * 100}%")
        
        # 处理股票选择数据
        stock_selection = ai_analysis.get('stockSelection', [])
        
        if stock_selection:
            # 计算 AI 推荐的总权重
            ai_total_weight = sum([stock.get('allocation', 0) for stock in stock_selection])
            print(f"AI 推荐总权重: {ai_total_weight}%")
            
            # 如果 AI 推荐的总权重超过用户设定的组合仓位占比，需要按比例缩放
            if ai_total_weight > 0:
                scale_factor = (portfolio_position_ratio * 100) / ai_total_weight
                print(f"权重缩放因子: {scale_factor:.3f}")
            else:
                scale_factor = 1.0
            
            for stock_selection_item in stock_selection:
                symbol = stock_selection_item['symbol']
                ai_allocation = stock_selection_item.get('allocation', 0)
                scaled_allocation = ai_allocation * scale_factor
                position = stock_selection_item.get('position', 'LONG')
                
                # 找到对应的股票数据
                stock_info = next((s for s in stock_data if s['symbol'] == symbol), None)
                if stock_info:
                    recommended_amount = investment_amount * (scaled_allocation / 100)
                    shares = stock_selection_item.get('shares', int(recommended_amount / stock_info['currentPrice']))
                    
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
                        "aiReason": stock_selection_item.get('reason', ''),
                        "riskLevel": stock_selection_item.get('riskLevel', '中')
                    })
            
            # 验证总分配
            total_allocation = sum([r['allocation'] for r in recommendations])
            print(f"AI策略最终总分配: {total_allocation:.1f}%")
            print(f"AI策略现金保留: {100 - total_allocation:.1f}%")
        
        return {
            "marketAnalysis": ai_analysis['marketAnalysis'],
            "recommendations": recommendations,
            "reasons": ai_analysis.get('investmentReasons', []),
            "risks": ai_analysis.get('riskWarnings', []),
            "strategyInsights": ai_analysis.get('strategyInsights', ''),
            "expectedMetrics": ai_analysis.get('expectedMetrics', {}),
            "aiPowered": True,
            "professionalGrade": True
        }
    else:
        print("Kimi AI调用失败，使用备用策略")
        # 使用备用分析
        backup_analysis = ai_result['analysis']
        
        # 将备用分析的stockSelection转换为recommendations
        recommendations = []
        stock_selection = backup_analysis.get('stockSelection', [])
        
        for stock_selection_item in stock_selection:
            symbol = stock_selection_item['symbol']
            position = stock_selection_item.get('position', 'LONG')
            allocation = stock_selection_item.get('allocation', 0)
            
            # 找到对应的股票数据
            stock_info = next((s for s in stock_data if s['symbol'] == symbol), None)
            if stock_info:
                investment_amount = preferences.get('investmentAmount', 100000)
                recommended_amount = investment_amount * (allocation / 100)
                shares = stock_selection_item.get('shares', int(recommended_amount / stock_info['currentPrice']))
                
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
                    "aiReason": stock_selection_item.get('reason', ''),
                    "riskLevel": stock_selection_item.get('riskLevel', '中')
                })
        
        return {
            "marketAnalysis": backup_analysis['marketAnalysis'],
            "recommendations": recommendations,
            "reasons": backup_analysis.get('investmentReasons', []),
            "risks": backup_analysis.get('riskWarnings', []),
            "strategyInsights": backup_analysis.get('strategyInsights', ''),
            "expectedMetrics": backup_analysis.get('expectedMetrics', {}),
            "aiPowered": False,
            "professionalGrade": True
        }