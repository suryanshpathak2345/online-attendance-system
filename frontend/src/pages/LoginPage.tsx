import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { CheckSquare, Lock, Mail, ArrowRight, AlertCircle, Shield, UserCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const res = await login(email, password);
      if (res.role === 'student') {
        navigate('/student/dashboard');
      } else {
        navigate('/teacher/dashboard');
      }
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Invalid email or password. Please try again.';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const fillDemoAccount = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <Link to="/" className="flex items-center justify-center gap-2.5">
          <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-md">
            <CheckSquare className="w-6 h-6" />
          </div>
          <span className="text-2xl font-bold tracking-tight text-slate-900">AttendEase</span>
        </Link>
        <h2 className="mt-6 text-center text-2xl font-extrabold text-slate-900">
          Faculty & Administrator Sign In
        </h2>
        <p className="mt-2 text-center text-sm text-slate-600">
          Or{' '}
          <Link to="/student-access" className="font-semibold text-indigo-600 hover:text-indigo-500">
            access student attendance portal
          </Link>
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-sm border border-slate-200/90 rounded-2xl sm:px-10">
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm font-medium text-rose-800">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
                Email Address
              </label>
              <div className="mt-1 relative rounded-xl shadow-2xs">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="faculty@attendease.edu"
                  className="block w-full pl-10 pr-3.5 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-600 focus:border-indigo-600 text-slate-900 bg-white"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
                Password
              </label>
              <div className="mt-1 relative rounded-xl shadow-2xs">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="block w-full pl-10 pr-3.5 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-600 focus:border-indigo-600 text-slate-900 bg-white"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center items-center gap-2 py-2.5 px-4 border border-transparent rounded-xl shadow-sm text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-hidden focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all disabled:opacity-60"
              >
                {isLoading ? 'Signing In...' : 'Sign In to Dashboard'}
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>

          {/* Demonstration Quick-Fill Account Selector */}
          <div className="mt-8 pt-6 border-t border-slate-100">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-3 text-center">
              Demonstration Quick-Fill Accounts
            </span>
            <div className="grid grid-cols-1 gap-2">
              <button
                type="button"
                onClick={() => fillDemoAccount('prof.sharma@attendease.edu', 'Teacher@Pass2026!')}
                className="flex items-center justify-between p-2.5 rounded-xl border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/50 transition-colors text-left"
              >
                <div className="flex items-center gap-2.5">
                  <UserCheck className="w-4 h-4 text-indigo-600" />
                  <div>
                    <span className="text-xs font-bold text-slate-800 block">
                      Prof. Rajesh Sharma
                    </span>
                    <span className="text-[10px] text-slate-500">DSA & OS Faculty</span>
                  </div>
                </div>
                <span className="text-[11px] font-semibold text-indigo-600">Quick Fill</span>
              </button>

              <button
                type="button"
                onClick={() => fillDemoAccount('dr.patel@attendease.edu', 'Teacher@Pass2026!')}
                className="flex items-center justify-between p-2.5 rounded-xl border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/50 transition-colors text-left"
              >
                <div className="flex items-center gap-2.5">
                  <UserCheck className="w-4 h-4 text-indigo-600" />
                  <div>
                    <span className="text-xs font-bold text-slate-800 block">
                      Dr. Priya Patel
                    </span>
                    <span className="text-[10px] text-slate-500">DBMS & Networks Faculty</span>
                  </div>
                </div>
                <span className="text-[11px] font-semibold text-indigo-600">Quick Fill</span>
              </button>

              <button
                type="button"
                onClick={() => fillDemoAccount('admin@attendease.edu', 'Admin@Pass2026!')}
                className="flex items-center justify-between p-2.5 rounded-xl border border-slate-200 hover:border-purple-300 hover:bg-purple-50/50 transition-colors text-left"
              >
                <div className="flex items-center gap-2.5">
                  <Shield className="w-4 h-4 text-purple-600" />
                  <div>
                    <span className="text-xs font-bold text-slate-800 block">
                      System Administrator
                    </span>
                    <span className="text-[10px] text-slate-500">Full Academic Management</span>
                  </div>
                </div>
                <span className="text-[11px] font-semibold text-purple-600">Quick Fill</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
