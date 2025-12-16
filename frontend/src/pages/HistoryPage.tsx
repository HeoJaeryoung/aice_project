import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { studyApi } from '../services/api';
import type { StudyHistoryResponse } from '../types';

export default function HistoryPage() {
  const [history, setHistory] = useState<StudyHistoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await studyApi.getHistory(20);
        setHistory(response);
      } catch (error) {
        console.error('Failed to fetch history:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchHistory();
  }, []);

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return '-';
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
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

  return (
    <Layout>
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">학습 기록</h1>

        {/* Overall Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="card text-center">
            <div className="text-sm text-gray-500">총 세션</div>
            <div className="text-2xl font-bold text-gray-900">
              {history?.total_sessions || 0}회
            </div>
          </div>
          <div className="card text-center">
            <div className="text-sm text-gray-500">총 문제</div>
            <div className="text-2xl font-bold text-gray-900">
              {history?.total_questions || 0}문제
            </div>
          </div>
          <div className="card text-center">
            <div className="text-sm text-gray-500">총 정답</div>
            <div className="text-2xl font-bold text-green-600">
              {history?.total_correct || 0}개
            </div>
          </div>
          <div className="card text-center">
            <div className="text-sm text-gray-500">전체 정답률</div>
            <div className="text-2xl font-bold text-primary-600">
              {history?.overall_accuracy ? `${history.overall_accuracy.toFixed(1)}%` : '-'}
            </div>
          </div>
        </div>

        {/* Session List */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">최근 학습 세션</h2>

          {!history?.sessions.length ? (
            <div className="text-center py-8 text-gray-500">
              아직 학습 기록이 없습니다.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b text-left text-sm text-gray-500">
                    <th className="pb-3">날짜</th>
                    <th className="pb-3">주제</th>
                    <th className="pb-3">난이도</th>
                    <th className="pb-3 text-center">문제 수</th>
                    <th className="pb-3 text-center">정답</th>
                    <th className="pb-3 text-center">정답률</th>
                    <th className="pb-3 text-center">소요 시간</th>
                    <th className="pb-3 text-center">상태</th>
                  </tr>
                </thead>
                <tbody>
                  {history.sessions.map((session) => (
                    <tr key={session.session_id} className="border-b last:border-b-0">
                      <td className="py-3 text-sm">
                        {formatDate(session.started_at)}
                      </td>
                      <td className="py-3">
                        <span className="inline-block px-2 py-1 text-xs rounded bg-gray-100">
                          {session.topic_name || '-'}
                        </span>
                      </td>
                      <td className="py-3 text-sm text-gray-600">
                        {session.difficulty === 'easy'
                          ? '쉬움'
                          : session.difficulty === 'medium'
                          ? '보통'
                          : session.difficulty === 'hard'
                          ? '어려움'
                          : '-'}
                      </td>
                      <td className="py-3 text-center text-sm">
                        {session.question_count}
                      </td>
                      <td className="py-3 text-center text-sm text-green-600">
                        {session.correct_answers}
                      </td>
                      <td className="py-3 text-center">
                        {session.accuracy_rate !== null ? (
                          <span
                            className={`text-sm font-medium ${
                              session.accuracy_rate >= 80
                                ? 'text-green-600'
                                : session.accuracy_rate >= 60
                                ? 'text-yellow-600'
                                : 'text-red-600'
                            }`}
                          >
                            {session.accuracy_rate.toFixed(0)}%
                          </span>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                      <td className="py-3 text-center text-sm text-gray-600">
                        {formatDuration(session.duration_seconds)}
                      </td>
                      <td className="py-3 text-center">
                        <span
                          className={`inline-block px-2 py-1 text-xs rounded ${
                            session.status === 'completed'
                              ? 'bg-green-100 text-green-700'
                              : session.status === 'active'
                              ? 'bg-yellow-100 text-yellow-700'
                              : 'bg-gray-100 text-gray-700'
                          }`}
                        >
                          {session.status === 'completed'
                            ? '완료'
                            : session.status === 'active'
                            ? '진행중'
                            : '중단'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
