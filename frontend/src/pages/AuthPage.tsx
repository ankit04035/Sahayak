import React, { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { loginUser, registerUser } from '../api/auth';

interface AuthPageProps {
  mode: 'login' | 'register';
}

const initialForm = {
  name: '',
  email: '',
  password: '',
};

export const AuthPage: React.FC<AuthPageProps> = ({ mode }) => {
  const navigate = useNavigate();
  const { loginUser: setSessionUser } = useUser();
  const [form, setForm] = useState(initialForm);
  const [submitState, setSubmitState] = useState<'idle' | 'loading' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const isRegister = useMemo(() => mode === 'register', [mode]);

  const handleChange = (field: keyof typeof initialForm, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrorMessage('');
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitState('loading');
    setErrorMessage('');

    try {
      const payload = {
        name: form.name.trim(),
        email: form.email.trim(),
        password: form.password,
      };

      const response = isRegister
        ? await registerUser(payload)
        : await loginUser({ email: payload.email, password: payload.password });

      const user = response.user;
      setSessionUser({ id: user.id, name: user.name, email: user.email });
      navigate('/');
    } catch (error) {
      setSubmitState('error');
      const message = error instanceof Error ? error.message : 'Unable to complete authentication.';
      setErrorMessage(message);
    } finally {
      setSubmitState('idle');
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center p-6">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-lg">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary-600 text-lg font-bold text-white">
            S
          </div>
          <h1 className="text-2xl font-bold text-slate-900">{isRegister ? 'Create your account' : 'Welcome back'}</h1>
          <p className="mt-2 text-sm text-slate-500">
            {isRegister ? 'Register with your email to start using SahayakAI.' : 'Sign in to continue with your profile.'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <div>
              <label htmlFor="name" className="mb-1 block text-sm font-medium text-slate-700">Full name</label>
              <input
                id="name"
                type="text"
                value={form.name}
                onChange={(e) => handleChange('name', e.target.value)}
                className="w-full rounded-lg border border-slate-300 bg-slate-50 px-3 py-2.5 text-sm outline-none transition focus:border-primary-500 focus:bg-white"
                placeholder="Enter your full name"
                required
              />
            </div>
          )}

          <div>
            <label htmlFor="email" className="mb-1 block text-sm font-medium text-slate-700">Email</label>
            <input
              id="email"
              type="email"
              value={form.email}
              onChange={(e) => handleChange('email', e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-slate-50 px-3 py-2.5 text-sm outline-none transition focus:border-primary-500 focus:bg-white"
              placeholder="name@example.com"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="mb-1 block text-sm font-medium text-slate-700">Password</label>
            <input
              id="password"
              type="password"
              value={form.password}
              onChange={(e) => handleChange('password', e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-slate-50 px-3 py-2.5 text-sm outline-none transition focus:border-primary-500 focus:bg-white"
              placeholder={isRegister ? 'At least 12 characters' : 'Enter your password'}
              minLength={isRegister ? 12 : 8}
              required
            />
          </div>

          {errorMessage && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {errorMessage}
            </div>
          )}

          <button
            type="submit"
            disabled={submitState === 'loading'}
            className="w-full rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {submitState === 'loading' ? 'Please wait...' : isRegister ? 'Create account' : 'Sign in'}
          </button>
        </form>

        <div className="mt-5 text-center text-sm text-slate-600">
          {isRegister ? 'Already have an account?' : 'Need an account?'}{' '}
          <Link
            to={isRegister ? '/login' : '/register'}
            className="font-semibold text-primary-600 hover:text-primary-700"
          >
            {isRegister ? 'Sign in' : 'Create one'}
          </Link>
        </div>
      </div>
    </div>
  );
};
