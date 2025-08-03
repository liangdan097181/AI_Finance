import React, { useState, useMemo, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { PerformanceData, StockRecommendation } from '../types';
import { BarChart3, TrendingUp, TrendingDown, Calendar } from 'lucide-react';

interface Props {
  data: PerformanceData[];
  recommendations: StockRecommendation[];
}

const PerformanceChart: React.FC<Props> = ({ data, recommendations }) => {
  const [monthRange, setMonthRange] = useState<number>(12);
  const [dynamicData, setDynamicData] = useState<PerformanceData[]>(data);
  const [loading, setLoading] = useState<boolean>(false);

  // 当月份范围改变时，获取新的历史数据
  useEffect(() => {
    const fetchHistoryData = async () => {
      if (monthRange === 12) {
        // 如果是12个月，使用原始数据
        setDynamicData(data);
        return;
      }

      setLoading(true);
      try {
        const symbols = recommendations.map(r => r.symbol);
        const allocations = recommendations.map(r => r.allocation);
        
        const response = await fetch('/api/stock-history', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            symbols,
            allocations,
            period: monthRange * 21  // 转换为交易日数量（每月约21个交易日）
          })
        });

        const result = await response.json();
        
        console.log(`获取 ${monthRange} 个月的历史数据:`, result.data?.length, '个月');
        console.log('数据范围:', result.data?.[0]?.month, '到', result.data?.[result.data?.length - 1]?.month);
        
        if (result.success) {
          setDynamicData(result.data);
        } else {
          console.error('获取历史数据失败:', result.error);
          // 如果获取失败，使用原始数据的子集
          setDynamicData(data.slice(-monthRange));
        }
      } catch (error) {
        console.error('获取历史数据出错:', error);
        // 如果出错，使用原始数据的子集
        setDynamicData(data.slice(-monthRange));
      } finally {
        setLoading(false);
      }
    };

    fetchHistoryData();
  }, [monthRange, recommendations]);

  // 使用动态数据，确保按时间顺序排列并取最近的N个月
  const filteredData = useMemo(() => {
    if (!dynamicData || dynamicData.length === 0) return [];
    
    // 按月份排序（确保时间顺序正确）
    const sortedData = [...dynamicData].sort((a, b) => {
      return new Date(a.month + '-01').getTime() - new Date(b.month + '-01').getTime();
    });
    
    // 取最近的 monthRange 个月的数据
    return sortedData.slice(-monthRange);
  }, [dynamicData, monthRange]);

  // 计算月度涨幅数据（每月相对于上月的涨幅）
  const monthlyChangeData = useMemo(() => {
    if (!filteredData || filteredData.length === 0) return [];
    
    return filteredData.map((currentData, index) => {
      if (index === 0) {
        // 第一个月，月度涨幅就是累计涨幅
        const monthData: any = { month: currentData.month };
        recommendations.forEach(stock => {
          monthData[stock.symbol] = Number(currentData[stock.symbol]) || 0;
        });
        return monthData;
      }
      
      // 计算相对于上个月的涨幅
      const prevData = filteredData[index - 1];
      const monthData: any = { month: currentData.month };
      
      recommendations.forEach(stock => {
        const currentValue = Number(currentData[stock.symbol]) || 0;
        const prevValue = Number(prevData[stock.symbol]) || 0;
        monthData[stock.symbol] = currentValue - prevValue;
      });
      
      return monthData;
    });
  }, [filteredData, recommendations]);

  // 生成颜色数组
  const colors = [
    '#3B82F6', // blue
    '#EF4444', // red
    '#10B981', // green
    '#F59E0B', // yellow
    '#8B5CF6', // purple
    '#06B6D4', // cyan
    '#F97316', // orange
    '#84CC16'  // lime
  ];

  // 删除这个重复的声明：
  // const filteredData = useMemo(() => {
  //   if (!data || data.length === 0) return [];
  //   return data.slice(-monthRange);
  // }, [data, monthRange]);

  // 计算组合累计收益率（基于过滤后的数据）
  const calculatePortfolioReturn = () => {
    if (!filteredData || filteredData.length === 0) return 0;
    
    // 获取选定时间范围的第一个和最后一个数据点
    const firstData = filteredData[0];
    const latestData = filteredData[filteredData.length - 1];
    let portfolioReturn = 0;
    
    recommendations.forEach((stock, index) => {
      // 获取起始和结束时间点的累计收益率
      const firstValue = firstData[stock.symbol];
      const latestValue = latestData[stock.symbol];
      
      // 确保数据是数字类型
      const firstReturn = typeof firstValue === 'number' ? firstValue : parseFloat(String(firstValue)) || 0;
      const latestReturn = typeof latestValue === 'number' ? latestValue : parseFloat(String(latestValue)) || 0;
      
      // 计算该时间段内的收益率变化
      // 如果起始点是5%，结束点是15%，那么这个时间段的收益率是10%
      const periodReturn = latestReturn - firstReturn;
      const weight = stock.allocation / 100;
      portfolioReturn += periodReturn * weight;
    });
    
    return portfolioReturn;
  };

  const portfolioReturn = calculatePortfolioReturn();
  const isPositive = portfolioReturn >= 0;

  // 滑动条样式
  const sliderStyle: React.CSSProperties = {
    width: '100%',
    height: '8px',
    borderRadius: '4px',
    background: `linear-gradient(to right, #8B5CF6 0%, #8B5CF6 ${((monthRange - 3) / (12 - 3)) * 100}%, #E5E7EB ${((monthRange - 3) / (12 - 3)) * 100}%, #E5E7EB 100%)`,
    outline: 'none',
    cursor: 'pointer',
    WebkitAppearance: 'none',
    appearance: 'none'
  };

  // 状态控制显示模式
  const [showMonthlyChange, setShowMonthlyChange] = useState<boolean>(false);

  // 自定义工具提示
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900 mb-2">{label}</p>
          <p className="text-xs text-gray-600 mb-2">
            {showMonthlyChange ? '当月涨幅' : '累计涨幅'}
          </p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.dataKey}: {entry.value > 0 ? '+' : ''}{entry.value.toFixed(2)}%
            </p>
          ))}
          <p className="text-xs text-gray-500 mt-2 border-t pt-2">
            点击图表切换显示模式
          </p>
        </div>
      );
    }
    return null;
  };

  // 图表点击事件处理
  const handleChartClick = () => {
    setShowMonthlyChange(!showMonthlyChange);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-8 fade-in">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <BarChart3 className="w-8 h-8 text-purple-600 mr-3" />
          <div>
            <h2 className="text-3xl font-bold text-gray-900">
              历史表现可视化
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              当前显示: {showMonthlyChange ? '当月涨幅' : '累计涨幅'} 
              <span className="ml-2 text-purple-600 cursor-pointer hover:underline" onClick={handleChartClick}>
                (点击切换)
              </span>
            </p>
          </div>
        </div>
        
        {/* 组合累计收益率显示区域 */}
        <div className="bg-gray-50 rounded-lg p-6 min-w-[200px]">
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-2">组合累计收益率</p>
            <div className="flex items-center justify-center">
              {isPositive ? (
                <TrendingUp className="w-6 h-6 text-green-500 mr-2" />
              ) : (
                <TrendingDown className="w-6 h-6 text-red-500 mr-2" />
              )}
              <span className={`text-2xl font-bold ${
                isPositive ? 'text-green-600' : 'text-red-600'
              }`}>
                {portfolioReturn > 0 ? '+' : ''}{portfolioReturn.toFixed(2)}%
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              基于配置权重计算（最近{monthRange}个月）
            </p>
          </div>
        </div>
      </div>

      <div className="h-96">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-gray-500">加载中...</div>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart 
              data={showMonthlyChange ? monthlyChangeData : filteredData} 
              margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
              onClick={handleChartClick}
              style={{ cursor: 'pointer' }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                dataKey="month" 
                stroke="#6B7280"
                fontSize={12}
              />
              <YAxis 
                stroke="#6B7280"
                fontSize={12}
                tickFormatter={(value) => `${value}%`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="line"
              />
              
              {/* 显示各股票的收益率线（累计或月度） */}
              {recommendations.map((stock, index) => (
                <Line
                  key={stock.symbol}
                  type="monotone"
                  dataKey={stock.symbol}
                  stroke={colors[index % colors.length]}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                  name={`${stock.symbol} (${stock.allocation.toFixed(1)}%)`}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* 时间范围滑动控件 */}
      <div className="mt-8 bg-gray-50 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Calendar className="w-5 h-5 text-gray-600 mr-2" />
            <span className="text-lg font-semibold text-gray-800">时间范围调整</span>
          </div>
          <div className="text-right">
            <span className="text-2xl font-bold text-purple-600">{monthRange}</span>
            <span className="text-sm text-gray-600 ml-1">个月</span>
          </div>
        </div>
        
        <div className="relative">
          <input
            type="range"
            min="3"
            max="12"
            value={monthRange}
            onChange={(e) => setMonthRange(parseInt(e.target.value))}
            style={sliderStyle}
            className="range-slider"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-2">
            <span>3个月</span>
            <span>6个月</span>
            <span>9个月</span>
            <span>12个月</span>
          </div>
        </div>
        
        <div className="mt-4 text-center text-sm text-gray-600">
          <p>拖动滑块调整查看时间范围，当前显示最近 <span className="font-semibold text-purple-600">{monthRange}</span> 个月的数据</p>
        </div>
      </div>

      <div className="mt-6 text-center text-sm text-gray-600">
        <p>* 图表显示各股票的{showMonthlyChange ? '月度涨幅' : '累积收益率'}表现，括号内为配置权重</p>
        <p className="mt-1 text-xs text-gray-500">点击图表可在累计涨幅和当月涨幅之间切换显示</p>
      </div>
      
      {/* 添加CSS样式到全局样式表或使用内联样式 */}
      <style dangerouslySetInnerHTML={{
        __html: `
          .range-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            height: 20px;
            width: 20px;
            border-radius: 50%;
            background: #8B5CF6;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
          }
          
          .range-slider::-moz-range-thumb {
            height: 20px;
            width: 20px;
            border-radius: 50%;
            background: #8B5CF6;
            cursor: pointer;
            border: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
          }
        `
      }} />
    </div>
  );
};

export default PerformanceChart;