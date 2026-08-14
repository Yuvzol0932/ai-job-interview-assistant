export interface ResumeParseResult {
  content: string;
  source_type: string;
  filename: string | null;
  char_count: number;
  is_empty: boolean;
  too_short: boolean;
  preview: string;
}

export interface ClarificationItem {
  field: string;
  question: string;
  hint: string;
  answer: string;
}

export interface RequirementRow {
  requirement: string;
  evidence: string;
  strength: string;
  gap: string;
}

export interface DiagnosisResult {
  score: number;
  overall_evaluation: string;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  optimized_examples: string[];
  requirement_table: RequirementRow[];
  top_priorities: string[];
  market_notes: string;
}

export interface InterviewState {
  job_label: string;
  questions: string[];
  answers: string[];
  follow_up_questions: string[];
  follow_up_answers: string[];
  current_index: number;
  status: "ready" | "in_progress" | "finished";
  phase: string;
  total: number;
  answered_count: number;
  current_question: string;
  current_follow_up_question: string;
}

export interface QuestionComment {
  question: string;
  comment: string;
}

export interface Report {
  report_id: string;
  created_at: string;
  job_label: string;
  dimensions: Record<string, number>;
  total_score: number;
  overall_impression: string;
  question_comments: QuestionComment[];
  growth_advice: string[];
  closing: string;
}

export interface ReportMeta {
  report_id: string;
  created_at: string;
  job_label: string;
  total_score: number;
}

export interface JobPosting {
  id: string;
  title: string;
  company: string;
  category: string;
  location: string;
  salary: string;
  education: string;
  experience: string;
  requirements: string[];
  description: string;
  tags: string[];
  source: string;
  source_label: string;
  url: string;
  posted_at: string;
  deadline: string;
}

export interface MatchedJob extends JobPosting {
  match_score: number;
  match_reasons: string[];
  gap_hints: string[];
}

export interface JobFilters {
  categories: string[];
  locations: string[];
  sources: string[];
}

export interface JobFeedResponse {
  jobs: JobPosting[];
  filters: JobFilters;
  total: number;
  updated_at: string;
}

export interface JobMatchResponse {
  jobs: MatchedJob[];
  strategy: "rules" | "llm";
}
