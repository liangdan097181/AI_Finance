import React from 'react';
import { StockRecommendation } from '../types';

interface StockRecommendationsProps {
  recommendations: StockRecommendation[];
  portfolioReturn: number;
  aiPowered?: boolean;
  strategyInsights?: string;
}

const StockRecommendations: React.FC<StockRecommendationsProps> = ({
  recommendations,
  portfolioReturn,
  aiPowered = false,
  strategyInsights
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatPercent = (percent: number) => {
    return `${percent >= 0 ? '+' : ''}${percent.toFixed(2)}%`;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-3">
          <h2 className="text-2xl font-bold text-gray-900">AI股票组合推荐</h2>
          {aiPowered ? (
            <div className="flex items-center space-x-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-3 py-1 rounded-full text-sm font-medium">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
              </svg>
              <span>AI增强</span>
            </div>
          ) : (
            <div className="flex items-center space-x-1 bg-gray-500 text-white px-3 py-1 rounded-full text-sm font-medium">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
              </svg>
              <span>备用策略</span>
            </div>
          )}
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-600">组合累积收益率</p>
          <p className={`text-2xl font-bold ${
            portfolioReturn >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {formatPercent(portfolioReturn)}
          </p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 font-semibold text-gray-700">仓位类型</th>
              <th className="text-left py-3 px-4 font-semibold text-gray-700">股票代码</th>
              <th className="text-left py-3 px-4 font-semibold text-gray-700">公司名称</th>
              <th className="text-right py-3 px-4 font-semibold text-gray-700">最新价格</th>
              <th className="text-right py-3 px-4 font-semibold text-gray-700">日涨幅</th>
              <th className="text-right py-3 px-4 font-semibold text-gray-700">建议股数</th>
              <th className="text-right py-3 px-4 font-semibold text-gray-700">投资金额</th>
              <th className="text-right py-3 px-4 font-semibold text-gray-700">资金占比</th>
            </tr>
          </thead>
          <tbody>
            {recommendations.map((stock, index) => {
              const position = stock.position || 'LONG';
              const isLong = position === 'LONG';
              const shares = stock.shares || Math.floor(stock.recommendedAmount / stock.currentPrice);
              
              return (
                <tr key={stock.symbol} className={`border-b border-gray-100 hover:bg-gray-50 ${
                  isLong ? 'hover:bg-green-50' : 'hover:bg-red-50'
                }`}>
                  {/* 仓位类型 */}
                  <td className="py-4 px-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      isLong 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {isLong ? (
                        <>
                          <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                          </svg>
                          做多
                        </>
                      ) : (
                        <>
                          <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                          卖空
                        </>
                      )}
                    </span>
                  </td>
                  
                  {/* 股票代码 */}
                  <td className="py-4 px-4">
                    <span className={`font-semibold ${
                      isLong ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {stock.symbol}
                    </span>
                  </td>
                  
                  {/* 公司名称 */}
                  <td className="py-4 px-4 text-gray-900">{stock.companyName}</td>
                  
                  {/* 最新价格 */}
                  <td className="py-4 px-4 text-right font-medium">
                    {formatCurrency(stock.currentPrice)}
                  </td>
                  
                  {/* 日涨幅 */}
                  <td className="py-4 px-4 text-right">
                    <span className={`flex items-center justify-end ${
                      stock.dailyChangePercent >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {stock.dailyChangePercent >= 0 ? (
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                        </svg>
                      ) : (
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                      {formatPercent(stock.dailyChangePercent)}
                    </span>
                  </td>
                  
                  {/* 建议股数 */}
                  <td className="py-4 px-4 text-right font-medium">
                    <span className={isLong ? 'text-green-700' : 'text-red-700'}>
                      {isLong ? '+' : '-'}{shares.toLocaleString()}
                    </span>
                  </td>
                  
                  {/* 投资金额 */}
                  <td className="py-4 px-4 text-right font-medium">
                    <span className={isLong ? 'text-green-700' : 'text-red-700'}>
                      {formatCurrency(stock.recommendedAmount)}
                    </span>
                  </td>
                  
                  {/* 资金占比 */}
                  <td className="py-4 px-4 text-right">
                    <span className={`px-2 py-1 rounded-full text-sm font-medium ${
                      isLong 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {stock.allocation.toFixed(1)}%
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* 多空仓位汇总 */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        {(() => {
          const longPositions = recommendations.filter(stock => (stock.position || 'LONG') === 'LONG');
          const shortPositions = recommendations.filter(stock => stock.position === 'SHORT');
          const longAllocation = longPositions.reduce((sum, stock) => sum + stock.allocation, 0);
          const shortAllocation = shortPositions.reduce((sum, stock) => sum + stock.allocation, 0);
          const totalAllocation = longAllocation + shortAllocation;
          const cashRatio = 100 - totalAllocation;
          const netExposure = longAllocation - shortAllocation;
          
          return (
            <>
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-semibold text-green-900 mb-2 flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                  多头仓位
                </h3>
                <p className="text-green-800 text-sm">
                  {longPositions.length} 只股票，占比 {longAllocation.toFixed(1)}%
                </p>
                <p className="text-green-700 text-xs mt-1">
                  预期从股价上涨中获利
                </p>
              </div>
              
              <div className="bg-red-50 p-4 rounded-lg">
                <h3 className="font-semibold text-red-900 mb-2 flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  空头仓位
                </h3>
                <p className="text-red-800 text-sm">
                  {shortPositions.length} 只股票，占比 {shortAllocation.toFixed(1)}%
                </p>
                <p className="text-red-700 text-xs mt-1">
                  预期从股价下跌中获利
                </p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                  </svg>
                  现金保留
                </h3>
                <p className="text-gray-800 text-sm">
                  {cashRatio.toFixed(1)}% 现金
                </p>
                <p className="text-gray-700 text-xs mt-1">
                  风险控制与流动性保障
                </p>
              </div>
              
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-blue-900 mb-2">净敞口</h3>
                <p className={`text-sm ${netExposure >= 0 ? 'text-green-800' : 'text-red-800'}`}>
                  {netExposure >= 0 ? '+' : ''}{netExposure.toFixed(1)}%
                </p>
                <p className="text-blue-700 text-xs mt-1">
                  {netExposure > 0 ? '偏多头' : netExposure < 0 ? '偏空头' : '市场中性'}
                </p>
              </div>
            </>
          );
        })()}
      </div>

      {/* AI策略洞察 */}
      {aiPowered && strategyInsights && (
        <div className="mt-6 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
          <div className="flex items-center space-x-2 mb-2">
            <svg className="w-5 h-5 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
            </svg>
            <h3 className="font-semibold text-purple-900">AI策略洞察</h3>
          </div>
          <p className="text-purple-800 text-sm leading-relaxed">
            {strategyInsights}
          </p>
        </div>
      )}

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-semibold text-blue-900 mb-2">投资建议</h3>
        <p className="text-blue-800 text-sm">
          以上推荐基于您的投资偏好和当前市场状况。
          {(() => {
            const totalAllocation = recommendations.reduce((sum, stock) => sum + stock.allocation, 0);
            const cashRatio = 100 - totalAllocation;
            return (
              <span className="text-blue-700 font-medium">
                {' '}组合总仓位 {totalAllocation.toFixed(1)}%，现金保留 {cashRatio.toFixed(1)}% 用于风险控制。
              </span>
            );
          })()}
          {recommendations.some(stock => stock.position === 'SHORT') && (
            <span className="text-red-700 font-medium"> 注意：卖空操作风险较高，请确保您了解相关风险。</span>
          )}
          建议分批建仓，并密切关注市场变化。
        </p>
      </div>
    </div>
  );
};

export default StockRecommendations;