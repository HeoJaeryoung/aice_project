import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { questionsApi, studyApi } from '../services/api';
import type { Topic, SessionQuestion, AnswerSubmitResponse } from '../types';

type QuizState = 'setup' | 'quiz' | 'result';

export default function QuizPage() {
  const navigate = useNavigate();
  const [state, setState] = useState<QuizState>('setup');
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<number | null>(null);
  const [difficulty, setDifficulty] = useState('medium');
  const [questionCount, setQuestionCount] = useState(5);
  const [isLoading, setIsLoading] = useState(false);

  // Quiz state
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [questions, setQuestions] = useState<SessionQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [answerResult, setAnswerResult] = useState<AnswerSubmitResponse | null>(null);
  const [startTime, setStartTime] = useState<number>(0);

  // Result state
  const [correctCount, setCorrectCount] = useState(0);
  const [totalTime, setTotalTime] = useState(0);

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const response = await questionsApi.getTopics();
        setTopics(response.topics);
        if (response.topics.length > 0) {
          setSelectedTopic(response.topics[0].topic_id);
        }
      } catch (error) {
        console.error('Failed to fetch topics:', error);
      }
    };
    fetchTopics();
  }, []);

  const startQuiz = async () => {
    if (!selectedTopic) return;

    setIsLoading(true);
    try {
      const response = await studyApi.createSession(selectedTopic, difficulty, questionCount);
      setSessionId(response.session_id);
      setQuestions(response.questions);
      setCurrentIndex(0);
      setCorrectCount(0);
      setSelectedAnswer(null);
      setAnswerResult(null);
      setStartTime(Date.now());
      setState('quiz');
    } catch (error) {
      console.error('Failed to start quiz:', error);
      alert('퀴즈를 시작할 수 없습니다. 다시 시도해주세요.');
    } finally {
      setIsLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!selectedAnswer) return;

    const question = questions[currentIndex];
    const timeSpent = Math.floor((Date.now() - startTime) / 1000);

    try {
      const result = await questionsApi.submitAnswer(
        question.question_id,
        selectedAnswer,
        timeSpent
      );
      setAnswerResult(result);
      if (result.is_correct) {
        setCorrectCount((prev) => prev + 1);
      }
    } catch (error) {
      console.error('Failed to submit answer:', error);
    }
  };

  const nextQuestion = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
      setSelectedAnswer(null);
      setAnswerResult(null);
      setStartTime(Date.now());
    } else {
      endQuiz();
    }
  };

  const endQuiz = async () => {
    if (sessionId) {
      try {
        await studyApi.endSession(sessionId);
      } catch (error) {
        console.error('Failed to end session:', error);
      }
    }
    setTotalTime(Math.floor((Date.now() - startTime) / 1000));
    setState('result');
  };

  const currentQuestion = questions[currentIndex];

  if (state === 'setup') {
    return (
      <Layout>
        <div className="max-w-2xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">문제 풀기</h1>

          <div className="card space-y-6">
            <div>
              <label className="label">주제 선택</label>
              <select
                value={selectedTopic || ''}
                onChange={(e) => setSelectedTopic(Number(e.target.value))}
                className="input"
              >
                {topics.map((topic) => (
                  <option key={topic.topic_id} value={topic.topic_id}>
                    {topic.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="label">난이도</label>
              <div className="flex gap-4">
                {[
                  { value: 'easy', label: '쉬움' },
                  { value: 'medium', label: '보통' },
                  { value: 'hard', label: '어려움' },
                ].map((option) => (
                  <label key={option.value} className="flex items-center">
                    <input
                      type="radio"
                      value={option.value}
                      checked={difficulty === option.value}
                      onChange={(e) => setDifficulty(e.target.value)}
                      className="mr-2"
                    />
                    {option.label}
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="label">문제 수</label>
              <select
                value={questionCount}
                onChange={(e) => setQuestionCount(Number(e.target.value))}
                className="input"
              >
                {[3, 5, 10].map((count) => (
                  <option key={count} value={count}>
                    {count}문제
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={startQuiz}
              disabled={isLoading || !selectedTopic}
              className="w-full btn btn-primary py-3"
            >
              {isLoading ? '문제 생성 중...' : '시작하기'}
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  if (state === 'quiz' && currentQuestion) {
    return (
      <Layout>
        <div className="max-w-3xl mx-auto">
          <div className="flex justify-between items-center mb-6">
            <div className="text-sm text-gray-500">
              {currentIndex + 1} / {questions.length}
            </div>
            <div className="w-full max-w-xs mx-4 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-primary-500 transition-all"
                style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
              />
            </div>
            <div className="text-sm text-gray-500">{currentQuestion.difficulty}</div>
          </div>

          <div className="card">
            <h2 className="text-lg font-medium text-gray-900 mb-6">
              {currentQuestion.question_text}
            </h2>

            <div className="space-y-3">
              {['a', 'b', 'c', 'd'].map((option) => {
                const optionText = currentQuestion[`option_${option}` as keyof SessionQuestion];
                const isSelected = selectedAnswer === option;
                const isCorrect = answerResult?.correct_answer === option;
                const isWrong = answerResult && isSelected && !answerResult.is_correct;

                let className = 'w-full p-4 text-left rounded-lg border-2 transition-colors ';
                if (answerResult) {
                  if (isCorrect) {
                    className += 'border-green-500 bg-green-50';
                  } else if (isWrong) {
                    className += 'border-red-500 bg-red-50';
                  } else {
                    className += 'border-gray-200';
                  }
                } else {
                  className += isSelected
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300';
                }

                return (
                  <button
                    key={option}
                    onClick={() => !answerResult && setSelectedAnswer(option)}
                    disabled={!!answerResult}
                    className={className}
                  >
                    <span className="font-medium mr-2">{option.toUpperCase()}.</span>
                    {optionText}
                  </button>
                );
              })}
            </div>

            {answerResult && (
              <div
                className={`mt-6 p-4 rounded-lg ${
                  answerResult.is_correct ? 'bg-green-100' : 'bg-red-100'
                }`}
              >
                <div className="font-medium mb-2">
                  {answerResult.is_correct ? '정답입니다!' : '오답입니다.'}
                </div>
                {answerResult.explanation && (
                  <div className="text-sm text-gray-700">{answerResult.explanation}</div>
                )}
              </div>
            )}

            <div className="mt-6 flex justify-end">
              {!answerResult ? (
                <button
                  onClick={submitAnswer}
                  disabled={!selectedAnswer}
                  className="btn btn-primary"
                >
                  제출
                </button>
              ) : (
                <button onClick={nextQuestion} className="btn btn-primary">
                  {currentIndex < questions.length - 1 ? '다음 문제' : '결과 보기'}
                </button>
              )}
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  if (state === 'result') {
    const accuracy = questions.length > 0 ? (correctCount / questions.length) * 100 : 0;

    return (
      <Layout>
        <div className="max-w-2xl mx-auto text-center">
          <div className="card">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">학습 완료!</h1>

            <div className="grid grid-cols-2 gap-6 mb-8">
              <div>
                <div className="text-sm text-gray-500">정답</div>
                <div className="text-4xl font-bold text-primary-600">
                  {correctCount}/{questions.length}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-500">정답률</div>
                <div className="text-4xl font-bold text-gray-900">{accuracy.toFixed(0)}%</div>
              </div>
            </div>

            <div className="flex gap-4 justify-center">
              <button onClick={() => navigate('/dashboard')} className="btn btn-secondary">
                대시보드로
              </button>
              <button
                onClick={() => {
                  setState('setup');
                  setQuestions([]);
                  setSessionId(null);
                  setCurrentIndex(0);
                  setSelectedAnswer(null);
                  setAnswerResult(null);
                  setCorrectCount(0);
                }}
                className="btn btn-primary"
              >
                다시 풀기
              </button>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return null;
}
