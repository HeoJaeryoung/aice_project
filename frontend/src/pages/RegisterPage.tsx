import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [name, setName] = useState('');
  const [localError, setLocalError] = useState('');
  const { register, isLoading, error, clearError } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError('');

    if (password !== confirmPassword) {
      setLocalError('비밀번호가 일치하지 않습니다.');
      return;
    }

    if (password.length < 6) {
      setLocalError('비밀번호는 6자 이상이어야 합니다.');
      return;
    }

    try {
      await register(email, password, name);
      navigate('/dashboard');
    } catch {
      // Error is handled by store
    }
  };

  const displayError = localError || error;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary-600">AICE Master</h1>
          <p className="text-gray-600 mt-2">AI 기반 자격증 학습 플랫폼</p>
        </div>

        <div className="card">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">회원가입</h2>

          {displayError && (
            <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
              {displayError}
              <button
                onClick={() => {
                  setLocalError('');
                  clearError();
                }}
                className="ml-2 text-red-500"
              >
                &times;
              </button>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="name" className="label">
                이름
              </label>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="input"
                placeholder="이름을 입력하세요"
                required
              />
            </div>

            <div>
              <label htmlFor="email" className="label">
                이메일
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input"
                placeholder="example@email.com"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="label">
                비밀번호
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
                placeholder="6자 이상 입력하세요"
                required
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="label">
                비밀번호 확인
              </label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="input"
                placeholder="비밀번호를 다시 입력하세요"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn btn-primary py-3"
            >
              {isLoading ? '가입 중...' : '회원가입'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <span className="text-gray-600">이미 계정이 있으신가요? </span>
            <Link to="/login" className="text-primary-600 hover:underline">
              로그인
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
