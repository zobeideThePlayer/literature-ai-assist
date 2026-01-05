import type { Insight, InsightType } from '../types';

interface InsightTimelineProps {
  insights: Insight[];
  isLoading?: boolean;
}

export function InsightTimeline({ insights, isLoading }: InsightTimelineProps) {
  const getInsightIcon = (type: InsightType): string => {
    const icons: Record<InsightType, string> = {
      observation: '👁️',
      connection: '🔗',
      theme: '📚',
      gap: '❓',
      contradiction: '⚡',
      conclusion: '✅',
    };
    return icons[type] || '📝';
  };

  const getInsightColor = (type: InsightType): string => {
    const colors: Record<InsightType, string> = {
      observation: 'border-blue-400 bg-blue-50',
      connection: 'border-purple-400 bg-purple-50',
      theme: 'border-green-400 bg-green-50',
      gap: 'border-yellow-400 bg-yellow-50',
      contradiction: 'border-red-400 bg-red-50',
      conclusion: 'border-emerald-400 bg-emerald-50',
    };
    return colors[type] || 'border-gray-400 bg-gray-50';
  };

  const getInsightLabel = (type: InsightType): string => {
    const labels: Record<InsightType, string> = {
      observation: 'Observation',
      connection: 'Connection',
      theme: 'Theme',
      gap: 'Research Gap',
      contradiction: 'Contradiction',
      conclusion: 'Conclusion',
    };
    return labels[type] || type;
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-lg font-semibold mb-4">Chain of Thought</h2>
      <p className="text-sm text-gray-600 mb-4">
        Step-by-step reasoning process for analyzing the literature.
      </p>

      {insights.length === 0 && !isLoading ? (
        <p className="text-gray-500 text-center py-8">
          No insights generated yet. Start the analysis to see the chain of thought.
        </p>
      ) : (
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200" />

          <div className="space-y-4">
            {insights.map((insight) => (
              <div key={insight.id} className="relative pl-10">
                {/* Timeline dot */}
                <div
                  className={`absolute left-2 w-5 h-5 rounded-full border-2 bg-white flex items-center justify-center text-xs ${getInsightColor(insight.insight_type)}`}
                >
                  <span>{insight.step_number}</span>
                </div>

                <div
                  className={`rounded-lg border-l-4 p-3 ${getInsightColor(insight.insight_type)}`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span>{getInsightIcon(insight.insight_type)}</span>
                    <span className="text-sm font-medium">
                      {getInsightLabel(insight.insight_type)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-800">{insight.content}</p>
                  {insight.reasoning && (
                    <details className="mt-2">
                      <summary className="text-xs text-gray-600 cursor-pointer hover:text-gray-800">
                        Show reasoning
                      </summary>
                      <p className="text-xs text-gray-600 mt-1 pl-2 border-l-2 border-gray-300">
                        {insight.reasoning}
                      </p>
                    </details>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="relative pl-10">
                <div className="absolute left-2 w-5 h-5 rounded-full border-2 bg-white border-gray-300 animate-pulse" />
                <div className="rounded-lg border-l-4 border-gray-300 bg-gray-50 p-3">
                  <div className="flex items-center gap-2">
                    <div className="animate-spin h-4 w-4 border-2 border-gray-400 border-t-transparent rounded-full" />
                    <span className="text-sm text-gray-600">Analyzing...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
