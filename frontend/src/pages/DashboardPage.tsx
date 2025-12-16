import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { dashboardApi } from '../services/api';
import type { DashboardSummary, TopicStatsResponse, WeeklyStatsResponse } from '../types';

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [topicStats, setTopicStats] = useState<TopicStatsResponse | null>(null);
  const [weeklyStats, setWeeklyStats] = useState<WeeklyStatsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setError(null);
        const [summaryData, topicData, weeklyData] = await Promise.all([
          dashboardApi.getSummary(),
          dashboardApi.getTopicStats(),
          dashboardApi.getWeeklyStats(),
        ]);
        setSummary(summaryData);
        setTopicStats(topicData);
        setWeeklyStats(weeklyData);
      } catch (err: any) {
        console.error('Failed to fetch dashboard data:', err);
        setError(err?.response?.data?.detail || err?.message || '데이터를 불러오는데 실패했습니다.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}시간 ${minutes}분`;
    }
    return `${minutes}분`;
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="text-gray-500">로딩 중...</div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="flex flex-col justify-center items-center h-64">
          <div className="text-red-500 mb-4">오류: {error}</div>
          <button
            onClick={() => window.location.reload()}
            className="btn btn-primary"
          >
            다시 시도
          </button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">대시보드</h1>
          <Link to="/quiz" className="btn btn-primary">
            문제 풀기 시작
          </Link>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="card">
            <div className="text-sm text-gray-500">총 푼 문제</div>
            <div className="text-3xl font-bold text-gray-900">
              {summary?.total_questions || 0}
            </div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-500">정답률</div>
            <div className="text-3xl font-bold text-primary-600">
              {summary?.accuracy_rate != null ? `${summary.accuracy_rate.toFixed(1)}%` : '-'}
            </div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-500">연속 학습</div>
            <div className="text-3xl font-bold text-green-600">
              {summary?.current_streak || 0}일
            </div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-500">오답 노트</div>
            <div className="text-3xl font-bold text-red-600">
              {summary?.mistake_count || 0}개
            </div>
          </div>
        </div>

        {/* Weekly Chart */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">주간 학습 현황</h2>
          <div className="flex items-end justify-between h-40 gap-2">
            {weeklyStats?.daily_stats && weeklyStats.daily_stats.length > 0 ? (
              weeklyStats.daily_stats.map((day) => {
                const maxHeight = 120;
                const maxQuestions = Math.max(...weeklyStats.daily_stats.map(d => d.questions_count || 1), 1);
                const height = weeklyStats.total_questions > 0
                  ? (day.questions_count / maxQuestions) * maxHeight
                  : 0;
                const dayName = new Date(day.date).toLocaleDateString('ko-KR', { weekday: 'short' });

                return (
                  <div key={day.date} className="flex-1 flex flex-col items-center">
                    <div className="text-xs text-gray-500 mb-1">
                      {day.questions_count > 0 ? day.questions_count : ''}
                    </div>
                    <div
                      className="w-full bg-primary-500 rounded-t"
                      style={{ height: `${Math.max(height, 4)}px` }}
                    />
                    <div className="text-xs text-gray-600 mt-2">{dayName}</div>
                  </div>
                );
              })
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-400">
                아직 학습 기록이 없습니다
              </div>
            )}
          </div>
        </div>

        {/* Topic Stats */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">주제별 정답률</h2>
          <div className="space-y-3">
            {topicStats?.stats && topicStats.stats.length > 0 ? (
              topicStats.stats.map((topic) => (
                <div key={topic.topic_id} className="flex items-center">
                  <div className="w-32 text-sm text-gray-700">{topic.topic_name}</div>
                  <div className="flex-1 mx-4">
                    <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary-500 rounded-full"
                        style={{ width: `${topic.accuracy_rate || 0}%` }}
                      />
                    </div>
                  </div>
                  <div className="w-20 text-right text-sm">
                    {topic.total_questions > 0 && topic.accuracy_rate != null ? (
                      <span className="text-gray-900">
                        {topic.accuracy_rate.toFixed(0)}%
                        <span className="text-gray-500 ml-1">({topic.total_questions})</span>
                      </span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center text-gray-400 py-4">
                아직 학습 기록이 없습니다
              </div>
            )}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">총 학습 시간</h3>
            <div className="text-2xl font-bold text-gray-700">
              {formatTime(summary?.total_study_time_seconds || 0)}
            </div>
          </div>
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">완료한 세션</h3>
            <div className="text-2xl font-bold text-gray-700">
              {summary?.total_sessions || 0}회
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
