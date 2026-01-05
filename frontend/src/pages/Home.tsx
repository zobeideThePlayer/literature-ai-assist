import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Review } from '../types';
import { listReviews, deleteReview, createReview } from '../services/api';

export function Home() {
  const navigate = useNavigate();
  const [reviews, setReviews] = useState<Review[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showNewForm, setShowNewForm] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDomain, setNewDomain] = useState('');
  const [newQuestion, setNewQuestion] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    loadReviews();
  }, []);

  const loadReviews = async () => {
    try {
      const data = await listReviews();
      setReviews(data.reviews);
    } catch (error) {
      console.error('Failed to load reviews:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this review?')) return;
    try {
      await deleteReview(id);
      setReviews((prev) => prev.filter((r) => r.id !== id));
    } catch (error) {
      console.error('Failed to delete review:', error);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    setIsCreating(true);
    try {
      const review = await createReview({
        title: newTitle.trim(),
        domain: newDomain.trim() || undefined,
        research_question: newQuestion.trim() || undefined,
      });
      navigate(`/review/${review.id}`);
    } catch (error) {
      console.error('Failed to create review:', error);
    } finally {
      setIsCreating(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      created: 'bg-gray-200 text-gray-700',
      searching: 'bg-blue-100 text-blue-700',
      analyzing: 'bg-yellow-100 text-yellow-700',
      generating: 'bg-purple-100 text-purple-700',
      completed: 'bg-green-100 text-green-700',
      error: 'bg-red-100 text-red-700',
    };
    return (
      <span className={`text-xs px-2 py-1 rounded ${colors[status] || 'bg-gray-200'}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Literature Review AI Assistant
          </h1>
          <p className="text-gray-600 mt-1">
            AI-powered literature review for researchers
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">Your Reviews</h2>
          <button
            onClick={() => setShowNewForm(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            New Review
          </button>
        </div>

        {showNewForm && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">Start New Literature Review</h3>
            <form onSubmit={handleCreate}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title / Topic *
                </label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g., Effects of mindfulness on anxiety disorders"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Domain (optional)
                </label>
                <input
                  type="text"
                  value={newDomain}
                  onChange={(e) => setNewDomain(e.target.value)}
                  placeholder="e.g., Clinical Psychology"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Research Question (optional)
                </label>
                <textarea
                  value={newQuestion}
                  onChange={(e) => setNewQuestion(e.target.value)}
                  placeholder="e.g., What is the efficacy of mindfulness-based interventions compared to traditional CBT for treating generalized anxiety disorder in adults?"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={isCreating || !newTitle.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {isCreating ? 'Creating...' : 'Create Review'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowNewForm(false);
                    setNewTitle('');
                    setNewDomain('');
                    setNewQuestion('');
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
            <p className="text-gray-600 mt-3">Loading reviews...</p>
          </div>
        ) : reviews.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-600 mb-4">No reviews yet. Create your first one!</p>
            <button
              onClick={() => setShowNewForm(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Create Review
            </button>
          </div>
        ) : (
          <div className="grid gap-4">
            {reviews.map((review) => (
              <div
                key={review.id}
                className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => navigate(`/review/${review.id}`)}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-lg">{review.title}</h3>
                    {review.domain && (
                      <p className="text-sm text-gray-600">Domain: {review.domain}</p>
                    )}
                    <div className="flex items-center gap-3 mt-2">
                      {getStatusBadge(review.status)}
                      <span className="text-sm text-gray-500">
                        {review.paper_count} papers | {review.insight_count} insights
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(review.id);
                      }}
                      className="px-3 py-1 text-sm text-red-600 border border-red-300 rounded hover:bg-red-50"
                    >
                      Delete
                    </button>
                  </div>
                </div>
                <p className="text-xs text-gray-400 mt-2">
                  Created: {new Date(review.created_at).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
