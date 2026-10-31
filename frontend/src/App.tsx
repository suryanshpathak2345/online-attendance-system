import React from 'react';
import { BrowserRouter, Navigate, Outlet, Route, Routes } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AppLayout } from './components/layout/AppLayout';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { StudentAccessPage } from './pages/StudentAccessPage';
import { TeacherDashboard } from './pages/teacher/TeacherDashboard';
import { MarkAttendancePage } from './pages/teacher/MarkAttendancePage';
import { AttendanceHistoryPage } from './pages/teacher/AttendanceHistoryPage';
import { ReportsPage } from './pages/teacher/ReportsPage';
import { ExcelExportPage } from './pages/teacher/ExcelExportPage';
import { StudentDashboardPage } from './pages/student/StudentDashboardPage';
import { LoadingSpinner } from './components/common/LoadingSpinner';

const ProtectedRoute: React.FC<{ children: React.ReactNode; roles?: Array<'admin' | 'teacher' | 'student'> }> = ({ children, roles }) => {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return <LoadingSpinner label="Loading your workspace..." className="h-screen" />;
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  if (roles && !roles.includes(user.role)) {
    return <Navigate to={user.role === 'student' ? '/student/dashboard' : '/teacher/dashboard'} replace />;
  }

  return <>{children}</>;
};

const TeacherRoutes: React.FC = () => (
  <ProtectedRoute roles={['teacher', 'admin']}>
    <AppLayout>
      <Outlet />
    </AppLayout>
  </ProtectedRoute>
);

const StudentRoutes: React.FC = () => (
  <ProtectedRoute roles={['student']}>
    <AppLayout>
      <Outlet />
    </AppLayout>
  </ProtectedRoute>
);

export const App: React.FC = () => (
  <BrowserRouter>
    <AuthProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/student-access" element={<StudentAccessPage />} />

        <Route path="/teacher" element={<TeacherRoutes />}>
          <Route index element={<Navigate to="/teacher/dashboard" replace />} />
          <Route path="dashboard" element={<TeacherDashboard />} />
          <Route path="mark-attendance" element={<MarkAttendancePage />} />
          <Route path="history" element={<AttendanceHistoryPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="export" element={<ExcelExportPage />} />
        </Route>

        <Route path="/student" element={<StudentRoutes />}>
          <Route index element={<Navigate to="/student/dashboard" replace />} />
          <Route path="dashboard" element={<StudentDashboardPage />} />
          <Route path="subjects" element={<StudentDashboardPage />} />
          <Route path="calendar" element={<StudentDashboardPage />} />
          <Route path="personal-tracker" element={<StudentDashboardPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  </BrowserRouter>
);
