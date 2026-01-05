export type ReviewStatus =
  | 'created'
  | 'searching'
  | 'analyzing'
  | 'generating'
  | 'completed'
  | 'error';

export type PaperSource = 'pubmed' | 'semantic_scholar';

export type InsightType =
  | 'observation'
  | 'connection'
  | 'theme'
  | 'gap'
  | 'contradiction'
  | 'conclusion';

export interface Review {
  id: string;
  title: string;
  domain?: string;
  research_question?: string;
  created_at: string;
  updated_at: string;
  status: ReviewStatus;
  final_review?: string;
  paper_count: number;
  insight_count: number;
}

export interface Paper {
  id: string;
  source: PaperSource;
  external_id: string;
  title: string;
  authors: string[];
  abstract?: string;
  publication_date?: string;
  doi?: string;
  url?: string;
  pdf_url?: string;
  relevance_score?: number;
  relevance_explanation?: string;
  key_findings: string[];
  created_at: string;
}

export interface PaperSearchResult {
  source: PaperSource;
  external_id: string;
  title: string;
  authors: string[];
  abstract?: string;
  publication_date?: string;
  doi?: string;
  url?: string;
  pdf_url?: string;
}

export interface Insight {
  id: string;
  review_session_id: string;
  paper_id?: string;
  step_number: number;
  insight_type: InsightType;
  content: string;
  reasoning?: string;
  created_at: string;
}

export interface AnalysisStatus {
  review_id: string;
  status: ReviewStatus;
  papers_found: number;
  papers_analyzed: number;
  insights_generated: number;
  current_step?: string;
  error_message?: string;
}

export interface CreateReviewRequest {
  title: string;
  domain?: string;
  research_question?: string;
}

export interface SearchPapersRequest {
  query: string;
  max_results?: number;
  sources?: PaperSource[];
}

export interface SearchPapersResponse {
  papers: PaperSearchResult[];
  total_found: number;
  query: string;
}

export interface StartAnalysisRequest {
  search_query: string;
  max_papers?: number;
}
