import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useUser } from './context/UserContext';
import { MainLayout } from './layouts/MainLayout';
import { DashboardPage } from './pages/DashboardPage';
import { DocumentsPage } from './pages/DocumentsPage';
import { DocumentDetailPage } from './pages/DocumentDetailPage';
import { ChatPage } from './pages/ChatPage';
import { ResumePage } from './pages/ResumePage';
import { CareerProfilePage } from './pages/CareerProfilePage';
import { CareerRoadmapPage } from './pages/CareerRoadmapPage';
import { AuthPage } from './pages/AuthPage';
import { NotFoundPage } from './pages/NotFoundPage';

const AppRoutes: React.FC = () => {
  const { currentUser } = useUser();

  return (
    <Routes>
      <Route path="/login" element={currentUser ? <Navigate to="/" replace /> : <AuthPage mode="login" />} />
      <Route path="/register" element={currentUser ? <Navigate to="/" replace /> : <AuthPage mode="register" />} />

      <Route path="/" element={currentUser ? <MainLayout /> : <Navigate to="/login" replace />}>
        <Route index element={<DashboardPage />} />
        <Route path="documents" element={<DocumentsPage />} />
        <Route path="documents/:id" element={<DocumentDetailPage />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="resumes" element={<ResumePage />} />
        <Route path="career/profile" element={<CareerProfilePage />} />
        <Route path="career/roadmap" element={<CareerRoadmapPage />} />
        <Route path="404" element={<NotFoundPage />} />
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Route>
    </Routes>
  );
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
};

export default App;
