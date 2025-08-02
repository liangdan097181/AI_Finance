import React, { useEffect, useState } from 'react';
import { MarketIndex } from '../types';
import { getMarketIndices } from '../services/api';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';

interface Props {
  marketAnalysis: string;
}

const MarketOverview: React.FC<Props> = ({ marketAnalysis }) => {
  const [indices, setIndices] = useState<MarketIndex[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        const data = await getMarketIndices();
        setIndices(data);
      } catch (error) {
        console.error('获取市场数据失败:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMarketData();
  }, []);

  const formatPrice = (price: number) => {
    return price.toLocaleString();
  };

  const formatChange = (change: number, isPercent: boolean = false) => {
    const sign = change >= 0 ? '+' : '';
    const suffix = isPercent ? '%' : '';
    return `${sign}${change.toFixed(2)}${suffix}`;
  };

  const getChangeColor = (change: number) => {
    return change >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const getChangeIcon = (change: number) => {
    return change >= 0 ? (
      <TrendingUp className="w-4 h-4" />
    ) : (
      <TrendingDown className="w-4 h-4" />
    );
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-8 fade-in">
      <div className="flex items-center mb-6">
        <Activity className="w-8 h-8 text-blue-600 mr-3" />
        <h2 className="text-3xl font-bold text-gray-900">
          市场概况
        </h2>
      </div>

      {/* 市场指数 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {loading ? (
          Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="bg-gray-50 rounded-lg p-6 animate-pulse">
              <div className="h-4 bg-gray-300 rounded mb-2"></div>
              <div className="h-8 bg-gray-300 rounded mb-2"></div>
              <div className="h-4 bg-gray-300 rounded"></div>
            </div>
          ))
        ) : (
          indices.map((index) => (
            <div key={index.symbol} className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {index.name}
              </h3>
              <div className="text-2xl font-bold text-gray-900 mb-2">
                {formatPrice(index.price)}
              </div>
              <div className={`flex items-center space-x-1 ${getChangeColor(index.changePercent)}`}>
                {getChangeIcon(index.changePercent)}
                <span className="font-medium">
                  {formatChange(index.changePercent, true)}
                </span>
                <span className="text-sm">
                  ({formatChange(index.change)})
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* 市场分析 */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">
          AI市场分析
        </h3>
        <p className="text-gray-700 leading-relaxed">
          {marketAnalysis}
        </p>
      </div>
    </div>
  );
};

export default MarketOverview;