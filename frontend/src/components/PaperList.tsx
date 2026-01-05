import type { Paper, PaperSearchResult } from '../types';
import { PaperCard } from './PaperCard';

interface PaperListProps {
  papers: (Paper | PaperSearchResult)[];
  onSelectPaper?: (paper: Paper | PaperSearchResult) => void;
  onAddPaper?: (paper: PaperSearchResult) => void;
  onRemovePaper?: (paperId: string) => void;
  selectedPaperId?: string;
  addedPaperIds?: Set<string>;
  title?: string;
  emptyMessage?: string;
}

export function PaperList({
  papers,
  onSelectPaper,
  onAddPaper,
  onRemovePaper,
  selectedPaperId,
  addedPaperIds = new Set(),
  title = 'Papers',
  emptyMessage = 'No papers found',
}: PaperListProps) {
  const getPaperId = (paper: Paper | PaperSearchResult): string => {
    return 'id' in paper ? paper.id : `${paper.source}-${paper.external_id}`;
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">{title}</h2>
        <span className="text-sm text-gray-500">{papers.length} papers</span>
      </div>

      {papers.length === 0 ? (
        <p className="text-gray-500 text-center py-8">{emptyMessage}</p>
      ) : (
        <div className="space-y-3 max-h-[600px] overflow-y-auto">
          {papers.map((paper) => {
            const paperId = getPaperId(paper);
            const isPaper = 'id' in paper;

            return (
              <PaperCard
                key={paperId}
                paper={paper}
                onSelect={() => onSelectPaper?.(paper)}
                onAdd={
                  !isPaper && onAddPaper
                    ? () => onAddPaper(paper as PaperSearchResult)
                    : undefined
                }
                onRemove={
                  isPaper && onRemovePaper
                    ? () => onRemovePaper((paper as Paper).id)
                    : undefined
                }
                isSelected={selectedPaperId === paperId}
                isAdded={addedPaperIds.has(paper.external_id)}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}
