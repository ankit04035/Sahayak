import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { UserProvider } from '../context/UserContext';
import App from '../App';
import { registerUser } from '../api/auth';

vi.mock('../api/auth', () => ({
  registerUser: vi.fn(),
  loginUser: vi.fn(),
}));

// Mock health and data APIs to avoid network errors during testing
vi.mock('../api/health', () => ({
  getHealth: vi.fn().mockResolvedValue({
    status: 'ok',
    demo_mode: true,
    ai_provider: 'demo',
    timestamp: '2026-09-23T00:00:00Z',
  }),
}));

vi.mock('../api/documents', () => ({
  getDocuments: vi.fn().mockResolvedValue([]),
}));

vi.mock('../api/chat', () => ({
  listChatSessions: vi.fn().mockResolvedValue([]),
}));

vi.mock('../api/resumes', () => ({
  listResumes: vi.fn().mockResolvedValue([]),
}));

vi.mock('../api/career', () => ({
  getCareerProfile: vi.fn().mockResolvedValue(null),
  listRoadmaps: vi.fn().mockResolvedValue([]),
}));

describe('SahayakAI Frontend App', () => {
  beforeEach(() => {
    localStorage.clear();
    localStorage.setItem('sahayakai_user', JSON.stringify({ id: 1, name: 'Test Student', email: 'student@example.com' }));
  });

  it('renders the brand title and navigation links', async () => {
    render(
      <UserProvider>
        <App />
      </UserProvider>
    );

    // Brand and subtitle
    expect(screen.getByText('Student Assistant')).toBeInTheDocument();
    expect(screen.getAllByText(/Student Assistant/i)[0]).toBeInTheDocument();

    // Primary navigation links in sidebar
    expect(screen.getAllByText(/Dashboard/i)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/Study Documents/i)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/Study Assistant/i)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/Resume Analyzer/i)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/Career Profile/i)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/Career Roadmap/i)[0]).toBeInTheDocument();
  });

  it('shows the signed-in account and logout action', () => {
    render(
      <UserProvider>
        <App />
      </UserProvider>
    );

    expect(screen.getByText('Test Student')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument();
  });

  it('redirects unauthenticated visitors to login', () => {
    localStorage.clear();
    render(
      <UserProvider>
        <App />
      </UserProvider>
    );

    expect(screen.getByRole('heading', { name: 'Welcome back' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Sign in' })).toBeInTheDocument();
  });

  it('registers an account, stores its session, and opens the home page', async () => {
    localStorage.clear();
    vi.mocked(registerUser).mockResolvedValue({
      message: 'Account created successfully.',
      user: { id: 2, name: 'New Student', email: 'new@example.com' },
    });

    render(
      <UserProvider>
        <App />
      </UserProvider>
    );

    fireEvent.click(screen.getByRole('link', { name: 'Create one' }));
    fireEvent.change(screen.getByLabelText('Full name'), { target: { value: 'New Student' } });
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'new@example.com' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'StrongPass123!' } });
    fireEvent.click(screen.getByRole('button', { name: 'Create account' }));

    await waitFor(() => {
      expect(registerUser).toHaveBeenCalledWith({
        name: 'New Student',
        email: 'new@example.com',
        password: 'StrongPass123!',
      });
      expect(screen.getByText('New Student')).toBeInTheDocument();
    });
    expect(JSON.parse(localStorage.getItem('sahayakai_user') || '{}')).toMatchObject({
      id: 2,
      name: 'New Student',
      email: 'new@example.com',
    });
  });
});
