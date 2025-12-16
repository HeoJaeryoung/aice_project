// User types
export interface User {
  user_id: number;
  email: string;
  name: string;
  is_active: boolean;
  is_verified: boolean;
  subscription_tier: string;
  created_at: string;
  last_login_at: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Topic types
export interface Topic {
  topic_id: number;
  name: string;
  code: string | null;
  description: string | null;
  display_order: number;
}

export interface TopicListResponse {
  topics: Topic[];
  count: number;
}

// Question types
export interface Question {
  question_id: number;
  topic_id: number | null;
  question_text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  difficulty: string;
  created_at: string;
}

export interface QuestionWithAnswer extends Question {
  correct_answer: string;
  explanation: string | null;
  topic_name: string | null;
}

export interface QuestionGenerateResponse {
  questions: Question[];
  topic: Topic;
  count: number;
}

export interface AnswerSubmitResponse {
  is_correct: boolean;
  correct_answer: string;
  user_answer: string;
  explanation: string | null;
  question_id: number;
}

// Session types
export interface SessionQuestion {
  question_id: number;
  question_text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  difficulty: string;
}

export interface SessionCreateResponse {
  session_id: string;
  topic: Topic;
  difficulty: string;
  question_count: number;
  questions: SessionQuestion[];
  started_at: string;
}

export interface Session {
  session_id: string;
  topic_id: number | null;
  topic_name: string | null;
  difficulty: string | null;
  question_count: number;
  status: string;
  started_at: string;
  ended_at: string | null;
  duration_seconds: number | null;
  questions_attempted: number;
  correct_answers: number;
  accuracy_rate: number | null;
}

export interface SessionResult {
  session_id: string;
  status: string;
  questions_attempted: number;
  correct_answers: number;
  accuracy_rate: number | null;
  duration_seconds: number | null;
  ended_at: string;
}

export interface SessionListResponse {
  sessions: Session[];
  count: number;
}

// Mistake types
export interface MistakeNote {
  note_id: number;
  question: QuestionWithAnswer;
  mistake_count: number;
  first_mistake_at: string;
  last_mistake_at: string;
  review_count: number;
  last_review_at: string | null;
  mastered: boolean;
}

export interface MistakeListResponse {
  mistakes: MistakeNote[];
  count: number;
}

// Dashboard types
export interface DashboardSummary {
  total_questions: number;
  total_correct: number;
  accuracy_rate: number | null;
  total_sessions: number;
  total_study_time_seconds: number;
  current_streak: number;
  mistake_count: number;
}

export interface TopicStat {
  topic_id: number;
  topic_name: string;
  topic_code: string | null;
  total_questions: number;
  correct_answers: number;
  accuracy_rate: number | null;
}

export interface TopicStatsResponse {
  stats: TopicStat[];
  count: number;
}

export interface DailyStat {
  date: string;
  questions_count: number;
  correct_count: number;
  accuracy_rate: number | null;
}

export interface WeeklyStatsResponse {
  daily_stats: DailyStat[];
  total_questions: number;
  total_correct: number;
  average_accuracy: number | null;
}

// Study history
export interface StudyHistoryResponse {
  sessions: Session[];
  total_sessions: number;
  total_questions: number;
  total_correct: number;
  overall_accuracy: number | null;
}
