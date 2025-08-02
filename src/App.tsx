import React, { useState } from 'react';
import InvestmentQuestionnaire from './components/InvestmentQuestionnaire';
import MarketOverview from './components/MarketOverview';
import StockRecommendations from './components/StockRecommendations';
import PerformanceChart from './components/PerformanceChart';
import ReasonsAndRisks from './components/ReasonsAndRisks';
import LoadingProgress from './components/LoadingProgress';
import { InvestmentPreferences, AIStrategyResponse } from './types';
import { generateAIStrategy } from './services/api';
import './App.css';

function App() {
  const [preferences, setPreferences] = useState<InvestmentPreferences>({
    investmentAmount: 100000,
    tradingStyle: 'value',
    maxDrawdown: 20,
    stopLoss: 20,
    maxSinglePosition: 20,
    customLogic: '',
    allowShortSelling: false // 默认不支持卖空
  });
  
  const [strategy, setStrategy] = useState<AIStrategyResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState<string>('');
  const [showApiKeyInput, setShowApiKeyInput] = useState(false);

  const handleGenerateStrategy = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await generateAIStrategy(preferences, apiKey);
      setStrategy(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : '生成策略失败');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToQuestionnaire = () => {
    setStrategy(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <LoadingProgress loading={loading} />
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            美股投资AI策略生成器
          </h1>
          <p className="text-lg text-gray-600">
            基于DeepSeek大模型，为您量身定制专业投资策略
          </p>
        </header>



        {!strategy ? (
          <InvestmentQuestionnaire
            preferences={preferences}
            onPreferencesChange={setPreferences}
            onGenerateStrategy={handleGenerateStrategy}
            loading={loading}
            error={error}
          />
        ) : (
          <div className="space-y-8">
            <MarketOverview marketAnalysis={strategy.marketAnalysis} />
            
            <StockRecommendations 
              recommendations={strategy.recommendations}
              portfolioReturn={strategy.portfolioReturn}
              aiPowered={strategy.aiPowered}
              strategyInsights={strategy.strategyInsights}
            />
            
            <PerformanceChart 
              data={strategy.historicalPerformance}
              recommendations={strategy.recommendations}
            />
            
            <ReasonsAndRisks 
              reasons={strategy.reasons}
              risks={strategy.risks}
            />
            
            <div className="text-center">
              <button
                onClick={handleBackToQuestionnaire}
                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg transition-colors"
              >
                选股逻辑修改：重新设置偏好
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;