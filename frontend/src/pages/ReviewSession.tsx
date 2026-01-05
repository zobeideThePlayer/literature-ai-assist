import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import type { Review, Paper, PaperSearchResult, Insight, AnalysisStatus } from '../types';
import {
  getReview,
  listReviewPapers,
  getInsights,
  getAnalysisStatus,
  startAnalysis,
  addPaperToReview,
  removePaperFromReview,
  generateReview,
  searchPapers,
} from '../services/api';
import { SearchPanel } from '../components/SearchPanel';
import { PaperList } from '../components/PaperList';
import { InsightTimeline } from '../components/InsightTimeline';
import { ReviewEditor } from '../components/ReviewEditor';
import { ProgressIndicator } from '../components/ProgressIndicator';

type Tab = 'search' | 'papers' | 'insights' | 'review';

export function ReviewSession() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [review, setReview] = useState<Review | null>(null);
  const [papers, setPapers] = useState<Paper[]>([]);
  const [searchResults, setSearchResults] = useState<PaperSearchResult[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [status, setStatus] = useState<AnalysisStatus | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>('search');
  const [isLoading, setIsLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const loadData = useCallback(async () => {
    if (!id) return;

    try {
      const [reviewData, papersData, insightsData, statusData] = await Promise.all([
        getReview(id),
        listReviewPapers(id),
        getInsights(id),
        getAnalysisStatus(id),
      ]);

      setReview(reviewData);
      setPapers(papersData);
      setInsights(insightsData);
      setStatus(statusData);

      if (['searching', 'analyzing', 'generating'].includes(statusData.status)) {
        setIsAnalyzing(true);
      }
    } catch (error) {
      console.error('Failed to load review data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Poll for status updates during analysis
  useEffect(() => {
    if (!isAnalyzing || !id) return;

    const interval = setInterval(async () => {
      try {
        const [statusData, insightsData, papersData] = await Promise.all([
          getAnalysisStatus(id),
          getInsights(id),
          listReviewPapers(id),
        ]);

        setStatus(statusData);
        setInsights(insightsData);
        setPapers(papersData);

        if (statusData.status === 'completed' || statusData.status === 'error') {
          setIsAnalyzing(false);
          const reviewData = await getReview(id);
          setReview(reviewData);
        }
      } catch (error) {
        console.error('Failed to poll status:', error);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [isAnalyzing, id]);

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    setIsSearching(true);
    try {
      const response = await searchPapers({ query, max_results: 20 });
      setSearchResults(response.papers);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleAddPaper = async (paper: PaperSearchResult) => {
    if (!id) return;
    try {
      const addedPaper = await addPaperToReview(id, paper);
      setPapers((prev) => [...prev, addedPaper]);
    } catch (error) {
      console.error('Failed to add paper:', error);
    }
  };

  const handleRemovePaper = async (paperId: string) => {
    if (!id) return;
    try {
      await removePaperFromReview(id, paperId);
      setPapers((prev) => prev.filter((p) => p.id !== paperId));
    } catch (error) {
      console.error('Failed to remove paper:', error);
    }
  };

  const handleStartAnalysis = async () => {
    if (!id || !searchQuery) return;

    setIsAnalyzing(true);
    setActiveTab('insights');

    try {
      await startAnalysis(id, { search_query: searchQuery, max_papers: 20 });
    } catch (error) {
      console.error('Failed to start analysis:', error);
      setIsAnalyzing(false);
    }
  };

  const handleGenerateReview = async () => {
    if (!id) return;

    setIsGenerating(true);
    setActiveTab('review');

    try {
      const result = await generateReview(id);
      setReview((prev) => (prev ? { ...prev, final_review: result.review } : null));
    } catch (error) {
      console.error('Failed to generate review:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const addedPaperIds = new Set(papers.map((p) => p.external_id));

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!review) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Review not found</p>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-blue-600 text-white rounded"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <button
            onClick={() => navigate('/')}
            className="text-blue-600 hover:text-blue-800 mb-2"
          >
            &larr; Back to Reviews
          </button>
          <h1 className="text-2xl font-bold text-gray-900">{review.title}</h1>
          {review.domain && (
            <p className="text-gray-600">Domain: {review.domain}</p>
          )}
          {review.research_question && (
            <p className="text-sm text-gray-500 mt-1">
              Research Question: {review.research_question}
            </p>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Progress Indicator */}
        {status && ['searching', 'analyzing', 'generating'].includes(status.status) && (
          <div className="mb-6">
            <ProgressIndicator status={status} />
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex border-b border-gray-200 mb-6">
          {(['search', 'papers', 'insights', 'review'] as Tab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 font-medium capitalize ${
                activeTab === tab
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab}
              {tab === 'papers' && ` (${papers.length})`}
              {tab === 'insights' && ` (${insights.length})`}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'search' && (
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <SearchPanel
                onPapersFound={(results) => {
                  setSearchResults(results);
                  handleSearch(searchQuery || review.title);
                }}
                onSearchStart={() => setIsSearching(true)}
                isLoading={isSearching}
              />

              <div className="mt-4">
                <button
                  onClick={handleStartAnalysis}
                  disabled={isAnalyzing || !searchQuery}
                  className="w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
                >
                  {isAnalyzing ? 'Analysis in Progress...' : 'Start Full Analysis'}
                </button>
                <p className="text-xs text-gray-500 mt-2 text-center">
                  This will search, analyze papers, and generate insights automatically.
                </p>
              </div>
            </div>

            <PaperList
              papers={searchResults}
              onAddPaper={handleAddPaper}
              addedPaperIds={addedPaperIds}
              title="Search Results"
              emptyMessage="Search for papers to see results"
            />
          </div>
        )}

        {activeTab === 'papers' && (
          <PaperList
            papers={papers}
            onRemovePaper={handleRemovePaper}
            title="Papers in Review"
            emptyMessage="No papers added yet. Search and add papers to begin."
          />
        )}

        {activeTab === 'insights' && (
          <div className="grid md:grid-cols-3 gap-6">
            <div className="md:col-span-2">
              <InsightTimeline insights={insights} isLoading={isAnalyzing} />
            </div>
            <div>
              <div className="bg-white rounded-lg shadow p-4">
                <h3 className="font-semibold mb-3">Quick Stats</h3>
                <div className="space-y-2 text-sm">
                  <p>Total Papers: {papers.length}</p>
                  <p>
                    Relevant Papers:{' '}
                    {papers.filter((p) => (p.relevance_score || 0) >= 0.5).length}
                  </p>
                  <p>Insights Generated: {insights.length}</p>
                  <p>
                    Themes Identified:{' '}
                    {insights.filter((i) => i.insight_type === 'theme').length}
                  </p>
                  <p>
                    Gaps Found:{' '}
                    {insights.filter((i) => i.insight_type === 'gap').length}
                  </p>
                </div>

                {review.status === 'completed' && !review.final_review && (
                  <button
                    onClick={handleGenerateReview}
                    disabled={isGenerating}
                    className="w-full mt-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:bg-gray-400"
                  >
                    {isGenerating ? 'Generating...' : 'Generate Review'}
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'review' && (
          <ReviewEditor
            review={review.final_review || ''}
            isGenerating={isGenerating}
            onRegenerate={handleGenerateReview}
          />
        )}
      </main>
    </div>
  );
}
