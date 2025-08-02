// 投资偏好接口
export interface InvestmentPreferences {
  investmentAmount: number;
  tradingStyle: 'value' | 'growth' | 'momentum' | 'contrarian' | 'lowVolatility';
  maxDrawdown: number;
  stopLoss: number;
  maxSinglePosition: number;
  customLogic: string;
  allowShortSelling: boolean; // 新增：是否允许卖空
}

// 市场指数接口
export interface MarketIndex {
  name: string;
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
}

// 股票推荐接口
export interface StockRecommendation {
  symbol: string;
  companyName: string;
  currentPrice: number;
  dailyChange: number;
  dailyChangePercent: number;
  recommendedAmount: number;
  allocation: number;
  position?: 'LONG' | 'SHORT'; // 新增：多头或空头仓位
  shares?: number; // 新增：建议股数
  aiReason?: string; // 新增：AI 推荐理由
  riskMetrics?: {
    beta?: string;
    volatility?: string;
    maxDrawdown?: string;
  }; // 新增：风险指标
}

// 历史表现数据接口
export interface PerformanceData {
  month: string;
  [stockSymbol: string]: number | string;
}

// AI策略响应接口
export interface AIStrategyResponse {
  marketAnalysis: string;
  recommendations: StockRecommendation[];
  historicalPerformance: PerformanceData[];
  reasons: string[];
  risks: string[];
  portfolioReturn: number;
  aiPowered?: boolean; // 新增：是否使用AI生成
  strategyInsights?: string; // 新增：策略洞察
}

// API响应接口
export interface ApiResponse {
  success: boolean;
  data?: AIStrategyResponse;
  error?: string;
}