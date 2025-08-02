import axios from 'axios';
import { InvestmentPreferences, AIStrategyResponse, MarketIndex } from '../types';

const API_BASE_URL = 'http://localhost:5001/api';

// 获取市场指数数据（真实数据）
export const getMarketIndices = async (): Promise<MarketIndex[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/market-indices`);
    
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.error || '获取市场数据失败');
    }
  } catch (error) {
    console.error('获取市场指数失败:', error);
    // 如果后端服务不可用，返回模拟数据作为备选
    return [
      {
        name: '纳斯达克综合指数',
        symbol: 'NASDAQ',
        price: 15000,
        change: 150,
        changePercent: 1.0
      },
      {
        name: '标普500指数',
        symbol: 'S&P 500',
        price: 4500,
        change: -20,
        changePercent: -0.44
      },
      {
        name: '道琼斯工业指数',
        symbol: 'DOW',
        price: 35000,
        change: 100,
        changePercent: 0.29
      }
    ];
  }
};

// 生成AI投资策略（使用真实数据）
export const generateAIStrategy = async (preferences: InvestmentPreferences, apiKey?: string): Promise<AIStrategyResponse> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/generate-strategy`, {
      preferences,
      apiKey: apiKey || undefined
    });
    
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.error || 'AI策略生成失败');
    }
  } catch (error) {
    console.error('生成AI策略失败:', error);
    throw new Error('AI策略生成失败，请稍后重试');
  }
};

// 获取股票实时数据
export const getStockData = async (symbols: string[]) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/stock-data`, {
      symbols
    });
    
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.error || '获取股票数据失败');
    }
  } catch (error) {
    console.error('获取股票数据失败:', error);
    throw error;
  }
};

// 获取股票历史数据
export const getStockHistory = async (symbols: string[], period: number = 252) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/stock-history`, {
      symbols,
      period
    });
    
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.error || '获取历史数据失败');
    }
  } catch (error) {
    console.error('获取历史数据失败:', error);
    throw error;
  }
};