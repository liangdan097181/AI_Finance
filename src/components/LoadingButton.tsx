import React, { useState, useEffect } from 'react';

interface LoadingButtonProps {
  onClick: () => void;
  loading: boolean;
  disabled?: boolean;
  className?: string;
  children: React.ReactNode;
  loadingText?: string;
  estimatedDuration?: number; // 预估持续时间（秒）
}

const LoadingButton: React.FC<LoadingButtonProps> = ({
  onClick,
  loading,
  disabled = false,
  className = '',
  children,
  loadingText = '处理中',
  estimatedDuration = 15
}) => {
  const [elapsed, setElapsed] = useState(0);
  const [phase, setPhase] = useState<'initial' | 'processing' | 'finalizing'>('initial');

  useEffect(() => {
    let timer: NodeJS.Timeout;
    
    if (loading) {
      setElapsed(0);
      setPhase('initial');
      
      timer = setInterval(() => {
        setElapsed((prev) => {
          const newElapsed = prev + 1;
          
          // 根据时间设置不同阶段
          if (newElapsed < estimatedDuration * 0.7) {
            setPhase('processing');
          } else {
            setPhase('finalizing');
          }
          
          return newElapsed;
        });
      }, 1000);
    } else {
      setElapsed(0);
      setPhase('initial');
    }

    return () => {
      if (timer) {
        clearInterval(timer);
      }
    };
  }, [loading, estimatedDuration]);

  const getButtonText = () => {
    if (!loading) return children;
    
    switch (phase) {
      case 'processing':
        return `${loadingText}... (${elapsed}s)`;
      case 'finalizing':
        return `即将完成... (${elapsed}s)`;
      default:
        return `${loadingText}...`;
    }
  };

  const getSpinnerColor = () => {
    switch (phase) {
      case 'finalizing':
        return 'border-yellow-300';
      default:
        return 'border-white';
    }
  };

  return (
    <button
      onClick={onClick}
      disabled={loading || disabled}
      className={`relative ${className}`}
    >
      {loading && (
        <div className="absolute left-3 top-1/2 transform -translate-y-1/2">
          <div className={`animate-spin rounded-full h-4 w-4 border-b-2 ${getSpinnerColor()}`}></div>
        </div>
      )}
      <span className={loading ? 'ml-6' : ''}>{getButtonText()}</span>
    </button>
  );
};

export default LoadingButton;