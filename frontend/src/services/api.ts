import axios from 'axios';
import type {
  AuthResponse,
  TopicListResponse,
  QuestionGenerateResponse,
  AnswerSubmitResponse,
  QuestionWithAnswer,
  SessionCreateResponse,
  SessionResult,
  SessionListResponse,
  MistakeListResponse,
  StudyHistoryResponse,
  DashboardSummary,
  TopicStatsResponse,
  WeeklyStatsResponse,
} from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  register: async (email: string, password: string, name: string): Promise<AuthResponse> => {
    const response = await api.post('/auth/register', { email, password, name });
    return response.data;
  },

  login: async (email: string, password: string): Promise<AuthResponse> => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },
};

// Questions API
export const questionsApi = {
  getTopics: async (): Promise<TopicListResponse> => {
    const response = await api.get('/questions/topics');
    return response.data;
  },

  generate: async (
    topic_id: number,
    difficulty: string,
    count: number
  ): Promise<QuestionGenerateResponse> => {
    const response = await api.post('/questions/generate', {
      topic_id,
      difficulty,
      count,
    });
    return response.data;
  },

  submitAnswer: async (
    question_id: number,
    user_answer: string,
    time_spent_seconds?: number
  ): Promise<AnswerSubmitResponse> => {
    const response = await api.post(`/questions/${question_id}/answer`, {
      user_answer,
      time_spent_seconds,
    });
    return response.data;
  },

  getSolution: async (question_id: number): Promise<QuestionWithAnswer> => {
    const response = await api.get(`/questions/${question_id}/solution`);
    return response.data;
  },
};

// Study API
export const studyApi = {
  createSession: async (
    topic_id: number,
    difficulty: string,
    question_count: number
  ): Promise<SessionCreateResponse> => {
    const response = await api.post('/study/sessions', {
      topic_id,
      difficulty,
      question_count,
    });
    return response.data;
  },

  endSession: async (session_id: string): Promise<SessionResult> => {
    const response = await api.put(`/study/sessions/${session_id}`);
    return response.data;
  },

  getSessions: async (limit = 10, offset = 0): Promise<SessionListResponse> => {
    const response = await api.get('/study/sessions', {
      params: { limit, offset },
    });
    return response.data;
  },

  getMistakes: async (limit = 20, offset = 0, mastered?: boolean): Promise<MistakeListResponse> => {
    const response = await api.get('/study/mistakes', {
      params: { limit, offset, mastered },
    });
    return response.data;
  },

  getHistory: async (limit = 10): Promise<StudyHistoryResponse> => {
    const response = await api.get('/study/history', {
      params: { limit },
    });
    return response.data;
  },
};

// Dashboard API
export const dashboardApi = {
  getSummary: async (): Promise<DashboardSummary> => {
    const response = await api.get('/dashboard/summary');
    return response.data;
  },

  getTopicStats: async (): Promise<TopicStatsResponse> => {
    const response = await api.get('/dashboard/stats/topics');
    return response.data;
  },

  getWeeklyStats: async (): Promise<WeeklyStatsResponse> => {
    const response = await api.get('/dashboard/stats/weekly');
    return response.data;
  },
};

export default api;
