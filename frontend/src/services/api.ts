import type {
  Review,
  Paper,
  PaperSearchResult,
  Insight,
  AnalysisStatus,
  CreateReviewRequest,
  SearchPapersRequest,
  SearchPapersResponse,
  StartAnalysisRequest,
} from '../types';

const API_BASE = 'http://localhost:8000/api';

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error ${response.status}`);
  }

  return response.json();
}

// Reviews API
export async function createReview(data: CreateReviewRequest): Promise<Review> {
  return fetchApi<Review>('/reviews', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function listReviews(): Promise<{ reviews: Review[]; total: number }> {
  return fetchApi('/reviews');
}

export async function getReview(id: string): Promise<Review> {
  return fetchApi<Review>(`/reviews/${id}`);
}

export async function deleteReview(id: string): Promise<void> {
  await fetchApi(`/reviews/${id}`, { method: 'DELETE' });
}

// Papers API
export async function searchPapers(
  request: SearchPapersRequest
): Promise<SearchPapersResponse> {
  return fetchApi<SearchPapersResponse>('/papers/search', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export async function addPaperToReview(
  reviewId: string,
  paper: PaperSearchResult
): Promise<Paper> {
  return fetchApi<Paper>(`/papers/${reviewId}/add`, {
    method: 'POST',
    body: JSON.stringify(paper),
  });
}

export async function listReviewPapers(reviewId: string): Promise<Paper[]> {
  return fetchApi<Paper[]>(`/papers/${reviewId}/list`);
}

export async function removePaperFromReview(
  reviewId: string,
  paperId: string
): Promise<void> {
  await fetchApi(`/papers/${reviewId}/papers/${paperId}`, { method: 'DELETE' });
}

// Analysis API
export async function startAnalysis(
  reviewId: string,
  request: StartAnalysisRequest
): Promise<AnalysisStatus> {
  return fetchApi<AnalysisStatus>(`/analysis/${reviewId}/start`, {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export async function getAnalysisStatus(reviewId: string): Promise<AnalysisStatus> {
  return fetchApi<AnalysisStatus>(`/analysis/${reviewId}/status`);
}

export async function getInsights(reviewId: string): Promise<Insight[]> {
  return fetchApi<Insight[]>(`/analysis/${reviewId}/insights`);
}

export async function generateReview(
  reviewId: string
): Promise<{ review: string }> {
  return fetchApi<{ review: string }>(`/analysis/${reviewId}/generate-review`, {
    method: 'POST',
    body: JSON.stringify({}),
  });
}

export async function* streamGenerateReview(
  reviewId: string
): AsyncGenerator<string> {
  const response = await fetch(
    `${API_BASE}/analysis/${reviewId}/generate-review-stream`
  );

  if (!response.ok) {
    throw new Error(`HTTP error ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body');

  const decoder = new TextDecoder();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    yield decoder.decode(value, { stream: true });
  }
}
