import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { studyApi } from '../services/api';
import type { MistakeNote } from '../types';

export default function MistakesPage() {
  const [mistakes, setMistakes] = useState<MistakeNote[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  useEffect(() => {
    const fetchMistakes = async () => {
      try {
        const response = await studyApi.getMistakes(50, 0, false);
        setMistakes(response.mistakes);
      } catch (error) {
        console.error('Failed to fetch mistakes:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMistakes();
  }, []);

  const toggleExpand = (noteId: number) => {
    setExpandedId(expandedId === noteId ? null : noteId);
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
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">오답노트</h1>
          <div className="text-sm text-gray-500">총 {mistakes.length}개</div>
        </div>

        {mistakes.length === 0 ? (
          <div className="card text-center py-12">
            <div className="text-gray-500 mb-4">아직 오답이 없습니다.</div>
            <div className="text-sm text-gray-400">
              문제를 풀고 틀린 문제가 여기에 저장됩니다.
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {mistakes.map((mistake) => {
              const isExpanded = expandedId === mistake.note_id;
              const question = mistake.question;

              return (
                <div key={mistake.note_id} className="card">
                  <div
                    className="cursor-pointer"
                    onClick={() => toggleExpand(mistake.note_id)}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="inline-block px-2 py-1 text-xs rounded bg-gray-100 text-gray-600">
                        {question.topic_name || '일반'}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-red-500">
                          {mistake.mistake_count}회 오답
                        </span>
                        <span className="text-xs text-gray-400">
                          {isExpanded ? '접기' : '펼치기'}
                        </span>
                      </div>
                    </div>

                    <h3 className="font-medium text-gray-900">{question.question_text}</h3>
                  </div>

                  {isExpanded && (
                    <div className="mt-4 pt-4 border-t">
                      <div className="space-y-2">
                        {['a', 'b', 'c', 'd'].map((option) => {
                          const optionText =
                            question[`option_${option}` as keyof typeof question];
                          const isCorrect = question.correct_answer === option;

                          return (
                            <div
                              key={option}
                              className={`p-3 rounded-lg ${
                                isCorrect
                                  ? 'bg-green-50 border border-green-200'
                                  : 'bg-gray-50'
                              }`}
                            >
                              <span className="font-medium mr-2">
                                {option.toUpperCase()}.
                              </span>
                              {optionText}
                              {isCorrect && (
                                <span className="ml-2 text-green-600 text-sm">
                                  (정답)
                                </span>
                              )}
                            </div>
                          );
                        })}
                      </div>

                      {question.explanation && (
                        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                          <div className="text-sm font-medium text-blue-800 mb-1">
                            해설
                          </div>
                          <div className="text-sm text-blue-700">
                            {question.explanation}
                          </div>
                        </div>
                      )}

                      <div className="mt-4 flex justify-between text-xs text-gray-400">
                        <span>
                          첫 오답:{' '}
                          {new Date(mistake.first_mistake_at).toLocaleDateString('ko-KR')}
                        </span>
                        <span>
                          마지막 오답:{' '}
                          {new Date(mistake.last_mistake_at).toLocaleDateString('ko-KR')}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </Layout>
  );
}
