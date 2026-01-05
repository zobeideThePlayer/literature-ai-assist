import type { Paper, PaperSearchResult } from '../types';

interface PaperCardProps {
  paper: Paper | PaperSearchResult;
  onSelect?: () => void;
  onAdd?: () => void;
  onRemove?: () => void;
  isSelected?: boolean;
  isAdded?: boolean;
}

export function PaperCard({
  paper,
  onSelect,
  onAdd,
  onRemove,
  isSelected,
  isAdded,
}: PaperCardProps) {
  const isPaper = 'id' in paper;
  const relevanceScore = isPaper ? (paper as Paper).relevance_score : undefined;
  const keyFindings = isPaper ? (paper as Paper).key_findings : [];

  const getRelevanceColor = (score: number | undefined) => {
    if (score === undefined) return 'bg-gray-200';
    if (score >= 0.7) return 'bg-green-500';
    if (score >= 0.5) return 'bg-yellow-500';
    return 'bg-red-400';
  };

  const getSourceBadge = (source: string) => {
    const colors = {
      pubmed: 'bg-blue-100 text-blue-800',
      semantic_scholar: 'bg-purple-100 text-purple-800',
    };
    const labels = {
      pubmed: 'PubMed',
      semantic_scholar: 'Semantic Scholar',
    };
    return (
      <span className={`text-xs px-2 py-1 rounded ${colors[source as keyof typeof colors] || 'bg-gray-100'}`}>
        {labels[source as keyof typeof labels] || source}
      </span>
    );
  };

  return (
    <div
      className={`bg-white rounded-lg shadow p-4 border-2 transition-all cursor-pointer hover:shadow-md ${
        isSelected ? 'border-blue-500' : 'border-transparent'
      }`}
      onClick={onSelect}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            {getSourceBadge(paper.source)}
            {relevanceScore !== undefined && (
              <span className="flex items-center gap-1 text-sm">
                <span
                  className={`w-3 h-3 rounded-full ${getRelevanceColor(relevanceScore)}`}
                />
                {(relevanceScore * 100).toFixed(0)}% relevant
              </span>
            )}
          </div>

          <h3 className="font-medium text-gray-900 mb-1 line-clamp-2">
            {paper.title}
          </h3>

          <p className="text-sm text-gray-600 mb-2">
            {paper.authors.slice(0, 3).join(', ')}
            {paper.authors.length > 3 && ` +${paper.authors.length - 3} more`}
            {paper.publication_date && ` (${paper.publication_date})`}
          </p>

          {paper.abstract && (
            <p className="text-sm text-gray-500 line-clamp-3 mb-2">
              {paper.abstract}
            </p>
          )}

          {keyFindings.length > 0 && (
            <div className="mt-2">
              <p className="text-xs font-medium text-gray-700 mb-1">Key Findings:</p>
              <ul className="text-xs text-gray-600 list-disc list-inside">
                {keyFindings.slice(0, 2).map((finding, i) => (
                  <li key={i} className="line-clamp-1">{finding}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex items-center gap-3 mt-3">
            {paper.url && (
              <a
                href={paper.url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="text-blue-600 text-sm hover:underline"
              >
                View Paper
              </a>
            )}
            {paper.doi && (
              <a
                href={`https://doi.org/${paper.doi}`}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="text-blue-600 text-sm hover:underline"
              >
                DOI
              </a>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-2">
          {onAdd && !isAdded && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onAdd();
              }}
              className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
            >
              Add
            </button>
          )}
          {onRemove && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onRemove();
              }}
              className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
            >
              Remove
            </button>
          )}
          {isAdded && (
            <span className="px-3 py-1 text-sm bg-gray-200 text-gray-600 rounded">
              Added
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
