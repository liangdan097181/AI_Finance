import React from 'react';
import { CheckCircle, AlertTriangle, Lightbulb, Shield } from 'lucide-react';

interface Props {
  reasons: string[];
  risks: string[];
}

const ReasonsAndRisks: React.FC<Props> = ({ reasons, risks }) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* 推荐理由 */}
      <div className="bg-white rounded-xl shadow-lg p-8 fade-in">
        <div className="flex items-center mb-6">
          <Lightbulb className="w-8 h-8 text-green-600 mr-3" />
          <h2 className="text-3xl font-bold text-gray-900">
            推荐理由
          </h2>
        </div>
        
        <div className="space-y-4">
          {reasons.map((reason, index) => (
            <div key={index} className="flex items-start space-x-3">
              <CheckCircle className="w-6 h-6 text-green-600 mt-0.5 flex-shrink-0" />
              <p className="text-gray-700 leading-relaxed">
                {reason}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* 风险评估 */}
      <div className="bg-white rounded-xl shadow-lg p-8 fade-in">
        <div className="flex items-center mb-6">
          <Shield className="w-8 h-8 text-red-600 mr-3" />
          <h2 className="text-3xl font-bold text-gray-900">
            风险评估
          </h2>
        </div>
        
        <div className="space-y-4">
          {risks.map((risk, index) => (
            <div key={index} className="flex items-start space-x-3">
              <AlertTriangle className="w-6 h-6 text-red-600 mt-0.5 flex-shrink-0" />
              <p className="text-gray-700 leading-relaxed">
                {risk}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ReasonsAndRisks;