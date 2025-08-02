import React from 'react';
import { InvestmentPreferences } from '../types';
import LoadingButton from './LoadingButton';

interface InvestmentQuestionnaireProps {
  preferences: InvestmentPreferences;
  onPreferencesChange: (preferences: InvestmentPreferences) => void;
  onGenerateStrategy: () => void;
  loading: boolean;
  error: string | null;
}

const InvestmentQuestionnaire: React.FC<InvestmentQuestionnaireProps> = ({
  preferences,
  onPreferencesChange,
  onGenerateStrategy,
  loading,
  error
}) => {
  const handleInputChange = (field: keyof InvestmentPreferences, value: string | number | boolean) => {
    onPreferencesChange({
      ...preferences,
      [field]: value
    });
  };

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">投资偏好问卷</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 投资金额 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            投资金额 (美元)
          </label>
          <input
            type="number"
            value={preferences.investmentAmount}
            onChange={(e) => handleInputChange('investmentAmount', Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            min="1000"
            step="1000"
          />
        </div>

        {/* 交易风格 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            交易风格
          </label>
          <select
            value={preferences.tradingStyle}
            onChange={(e) => handleInputChange('tradingStyle', e.target.value as InvestmentPreferences['tradingStyle'])}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="value">价值投资</option>
            <option value="growth">成长投资</option>
            <option value="momentum">动量投资</option>
            <option value="contrarian">逆向投资</option>
            <option value="lowVolatility">低波动投资</option>
          </select>
        </div>

        {/* 最大回撤 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            最大回撤容忍度 (%)
          </label>
          <input
            type="number"
            value={preferences.maxDrawdown}
            onChange={(e) => handleInputChange('maxDrawdown', Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            min="5"
            max="50"
            step="5"
          />
        </div>

        {/* 止损比例 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            止损比例 (%)
          </label>
          <input
            type="number"
            value={preferences.stopLoss}
            onChange={(e) => handleInputChange('stopLoss', Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            min="5"
            max="30"
            step="5"
          />
        </div>

        {/* 组合仓位占比 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            组合仓位占比 (%)
          </label>
          <input
            type="number"
            value={preferences.maxSinglePosition}
            onChange={(e) => handleInputChange('maxSinglePosition', Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            min="10"
            max="100"
            step="5"
          />
          <p className="text-xs text-gray-500 mt-1">
            投资组合总仓位占比，剩余资金将保持现金
          </p>
        </div>

        {/* 卖空支持 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            投资策略类型
          </label>
          <div className="flex items-center space-x-4">
            <label className="flex items-center">
              <input
                type="radio"
                name="shortSelling"
                checked={!preferences.allowShortSelling}
                onChange={() => handleInputChange('allowShortSelling', false)}
                className="mr-2 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">仅做多 (Long Only)</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="shortSelling"
                checked={preferences.allowShortSelling}
                onChange={() => handleInputChange('allowShortSelling', true)}
                className="mr-2 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">多空策略 (Long/Short)</span>
            </label>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {preferences.allowShortSelling 
              ? "支持卖空，可以做空看跌的股票获利" 
              : "仅买入看涨的股票，风险相对较低"}
          </p>
        </div>
      </div>

      {/* 自定义选股逻辑 */}
      <div className="mt-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          自定义选股逻辑 (可选)
        </label>
        <textarea
          value={preferences.customLogic}
          onChange={(e) => handleInputChange('customLogic', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={4}
          placeholder="请描述您的特殊选股要求或偏好..."
        />
      </div>

      {/* 错误信息 */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* 生成策略按钮 */}
      <div className="mt-8 text-center">
        <LoadingButton
          onClick={onGenerateStrategy}
          loading={loading}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 px-8 rounded-lg transition-colors"
          loadingText="AI策略生成中"
          estimatedDuration={20}
        >
          AI生成投资策略
        </LoadingButton>
      </div>
    </div>
  );
};

export default InvestmentQuestionnaire;