import React, { useState, useEffect } from 'react';

interface LoadingProgressProps {
  loading: boolean;
  steps?: string[];
  stepDuration?: number;
}

const LoadingProgress: React.FC<LoadingProgressProps> = ({
  loading,
  steps = [
    '正在分析市场数据...',
    '获取股票实时价格...',
    'AI正在分析投资策略...',
    '计算投资组合配置...',
    '生成历史回测数据...',
    '完成策略生成...'
  ],
  stepDuration = 2000
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [isNearComplete, setIsNearComplete] = useState(false);

  useEffect(() => {
    if (!loading) {
      setCurrentStep(0);
      setProgress(0);
      setIsNearComplete(false);
      return;
    }

    let progressTimer: NodeJS.Timeout;
    let stepTimer: NodeJS.Timeout;
    let startTime = Date.now();

    // 智能进度更新逻辑
    const updateProgress = () => {
      const elapsed = Date.now() - startTime;
      let newProgress = 0;

      if (elapsed < 3000) {
        // 前3秒快速到30%
        newProgress = (elapsed / 3000) * 30;
      } else if (elapsed < 8000) {
        // 3-8秒缓慢到70%
        newProgress = 30 + ((elapsed - 3000) / 5000) * 40;
      } else if (elapsed < 12000) {
        // 8-12秒到85%
        newProgress = 70 + ((elapsed - 8000) / 4000) * 15;
      } else if (elapsed < 20000) {
        // 12-20秒缓慢到95%
        newProgress = 85 + ((elapsed - 12000) / 8000) * 10;
      } else {
        // 20秒后保持在95-98%之间波动，等待实际完成
        const fluctuation = Math.sin((elapsed - 20000) / 1000) * 1.5;
        newProgress = 96.5 + fluctuation;
        setIsNearComplete(true);
      }

      setProgress(Math.min(newProgress, 98)); // 最多到98%，留2%给实际完成
    };

    // 步骤切换逻辑
    const updateStep = () => {
      const elapsed = Date.now() - startTime;
      let stepIndex = 0;

      if (elapsed < 2000) stepIndex = 0;
      else if (elapsed < 4000) stepIndex = 1;
      else if (elapsed < 8000) stepIndex = 2;
      else if (elapsed < 12000) stepIndex = 3;
      else if (elapsed < 16000) stepIndex = 4;
      else stepIndex = 5;

      setCurrentStep(Math.min(stepIndex, steps.length - 1));
    };

    // 更频繁的更新以获得更流畅的动画
    progressTimer = setInterval(() => {
      updateProgress();
      updateStep();
    }, 100);

    return () => {
      if (progressTimer) clearInterval(progressTimer);
      if (stepTimer) clearInterval(stepTimer);
    };
  }, [loading, steps.length]);

  // 当loading变为false时，快速完成进度条
  useEffect(() => {
    if (!loading && progress > 0) {
      setProgress(100);
      setCurrentStep(steps.length - 1);
      
      // 短暂延迟后隐藏
      const hideTimer = setTimeout(() => {
        setProgress(0);
        setCurrentStep(0);
        setIsNearComplete(false);
      }, 500);

      return () => clearTimeout(hideTimer);
    }
  }, [loading, progress, steps.length]);

  if (!loading) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
        <div className="text-center">
          {/* 加载动画 */}
          <div className="mb-6">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto"></div>
          </div>
          
          {/* 当前步骤 */}
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            AI策略生成中
          </h3>
          
          <p className="text-gray-600 mb-6">
            {isNearComplete ? '正在完成最后的策略优化...' : steps[currentStep]}
          </p>
          
          {/* 进度条 */}
          <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
            <div 
              className={`h-3 rounded-full transition-all duration-200 ease-out ${
                isNearComplete 
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600' 
                  : 'bg-blue-600'
              }`}
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          
          {/* 进度百分比 */}
          <p className="text-sm text-gray-500">
            {Math.round(progress)}% 完成
          </p>
          
          {/* 动态提示信息 */}
          <p className="text-xs text-gray-400 mt-4">
            {isNearComplete 
              ? '即将完成，请稍等片刻...' 
              : '正在为您分析最优投资组合，请稍候...'}
          </p>
          
          {/* 额外的视觉反馈 */}
          {isNearComplete && (
            <div className="mt-3 flex justify-center">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LoadingProgress;