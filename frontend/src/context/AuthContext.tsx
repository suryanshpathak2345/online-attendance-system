import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi, AuthResponse, UserProfile } from '../api/auth';

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  role: 'admin' | 'teacher' | 'student' | null;
  login: (email: string, password: string) => Promise<AuthResponse>;
  studentAccess: (rollNumber: string, classId: number, passcode?: string) => Promise<AuthResponse>;
  logout: () => void;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'));
  const [user, setUser] = useState<UserProfile | null>(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const refreshProfile = async () => {
    try {
      if (!token) {
        setUser(null);
        setIsLoading(false);
        return;
      }
      const profile = await authApi.getProfile();
      setUser(profile);
      localStorage.setItem('user', JSON.stringify(profile));
    } catch (err) {
      console.error('Failed to refresh user profile:', err);
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      refreshProfile();
    } else {
      setIsLoading(false);
    }
  }, [token]);

  const handleAuthSuccess = async (res: AuthResponse) => {
    localStorage.setItem('token', res.access_token);
    setToken(res.access_token);
    const minimalUser: UserProfile = {
      id: res.user_id,
      email: res.email,
      full_name: res.full_name,
      role: res.role,
      student_id: res.student_id,
      class_id: res.class_id,
      assigned_classes: [],
    };
    setUser(minimalUser);
    localStorage.setItem('user', JSON.stringify(minimalUser));
    // Fetch full profile (e.g. assignments)
    try {
      const full = await authApi.getProfile();
      setUser(full);
      localStorage.setItem('user', JSON.stringify(full));
    } catch {
      // Ignore if initial fetch handles it
    }
  };

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await authApi.login({ email, password });
      await handleAuthSuccess(res);
      return res;
    } finally {
      setIsLoading(false);
    }
  };

  const studentAccess = async (rollNumber: string, classId: number, passcode?: string) => {
    setIsLoading(true);
    try {
      const res = await authApi.studentAccess({ roll_number: rollNumber, class_id: classId, secret_passcode: passcode });
      await handleAuthSuccess(res);
      return res;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        role: user ? user.role : null,
        login,
        studentAccess,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
