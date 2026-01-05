import type { AnalysisStatus } from '../types';

interface ProgressIndicatorProps {
  status: AnalysisStatus | null;
}

export function ProgressIndicator({ status }: ProgressIndicatorProps) {
  if (!status) return null;

  const getStatusColor = () => {
    switch (status.status) {
      case 'completed':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      case 'searching':
      case 'analyzing':
      case 'generating':
        return 'bg-blue-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getProgress = () => {
    if (status.status === 'completed') return 100;
    if (status.status === 'error') return 0;
    if (status.status === 'searching') return 25;
    if (status.status === 'analyzing') {
      const base = 25;
      const range = 50;
      if (status.papers_found === 0) return base;
      const progress = (status.papers_analyzed / status.papers_found) * range;
      return base + progress;
    }
    if (status.status === 'generating') return 85;
    return 0;
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium">Analysis Progress</span>
        <span className="text-sm text-gray-500">{Math.round(getProgress())}%</span>
      </div>

      <div className="h-2 bg-gray-200 rounded-full overflow-hidden mb-3">
        <div
          className={`h-full ${getStatusColor()} transition-all duration-500`}
          style={{ width: `${getProgress()}%` }}
        />
      </div>

      <p className="text-sm text-gray-600">{status.current_step}</p>

      <div className="grid grid-cols-3 gap-4 mt-4 text-center">
        <div>
          <p className="text-2xl font-bold text-gray-800">{status.papers_found}</p>
          <p className="text-xs text-gray-500">Papers Found</p>
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-800">{status.papers_analyzed}</p>
          <p className="text-xs text-gray-500">Analyzed</p>
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-800">{status.insights_generated}</p>
          <p className="text-xs text-gray-500">Insights</p>
        </div>
      </div>

      {status.error_message && (
        <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
          {status.error_message}
        </div>
      )}
    </div>
  );
}
