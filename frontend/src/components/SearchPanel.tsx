import { useState } from 'react';
import type { PaperSearchResult, PaperSource } from '../types';
import { searchPapers } from '../services/api';

interface SearchPanelProps {
  onPapersFound: (papers: PaperSearchResult[]) => void;
  onSearchStart: () => void;
  isLoading: boolean;
}

export function SearchPanel({ onPapersFound, onSearchStart, isLoading }: SearchPanelProps) {
  const [query, setQuery] = useState('');
  const [maxResults, setMaxResults] = useState(20);
  const [sources, setSources] = useState<PaperSource[]>(['pubmed', 'semantic_scholar']);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setError(null);
    onSearchStart();

    try {
      const response = await searchPapers({
        query: query.trim(),
        max_results: maxResults,
        sources,
      });
      onPapersFound(response.papers);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      onPapersFound([]);
    }
  };

  const toggleSource = (source: PaperSource) => {
    setSources((prev) =>
      prev.includes(source) ? prev.filter((s) => s !== source) : [...prev, source]
    );
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Search Literature</h2>
      <form onSubmit={handleSearch}>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Search Query
          </label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your search terms (e.g., 'cognitive behavioral therapy anxiety adolescents')"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sources
          </label>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={sources.includes('pubmed')}
                onChange={() => toggleSource('pubmed')}
                className="mr-2"
              />
              PubMed
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={sources.includes('semantic_scholar')}
                onChange={() => toggleSource('semantic_scholar')}
                className="mr-2"
              />
              Semantic Scholar
            </label>
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Max Results
          </label>
          <select
            value={maxResults}
            onChange={(e) => setMaxResults(Number(e.target.value))}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading || !query.trim() || sources.length === 0}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </form>
    </div>
  );
}
