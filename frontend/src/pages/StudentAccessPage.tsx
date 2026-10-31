import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { GraduationCap, ArrowRight, AlertCircle, Sparkles, CheckSquare, KeyRound, School } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { classesApi, ClassRoom } from '../api/classes';

export const StudentAccessPage: React.FC = () => {
  const navigate = useNavigate();
  const { studentAccess } = useAuth();

  const [classes, setClasses] = useState<ClassRoom[]>([]);
  const [selectedClassId, setSelectedClassId] = useState<number | ''>('');
  const [rollNumber, setRollNumber] = useState('');
  const [secretPasscode, setSecretPasscode] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchClasses = async () => {
      try {
        const list = await classesApi.list();
        setClasses(list);
        if (list.length > 0) {
          setSelectedClassId(list[0].id);
        }
      } catch (err) {
        console.error('Error fetching classes:', err);
      }
    };
    fetchClasses();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedClassId) {
      setError('Please select your class/cohort.');
      return;
    }
    setError(null);
    setIsLoading(true);

    try {
      await studentAccess(rollNumber.trim(), Number(selectedClassId), secretPasscode.trim() || undefined);
      navigate('/student/dashboard');
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'No student record found with this roll number in selected class.';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const fillDemoStudent = () => {
    if (classes.length > 0) {
      setSelectedClassId(classes[0].id);
    }
    setRollNumber('CSE-2026-001');
    setSecretPasscode('STU-1001');
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <Link to="/" className="flex items-center justify-center gap-2.5">
          <div className="w-10 h-10 rounded-xl bg-emerald-600 flex items-center justify-center text-white shadow-md">
            <GraduationCap className="w-6 h-6" />
          </div>
          <span className="text-2xl font-bold tracking-tight text-slate-900">AttendEase</span>
        </Link>
        <h2 className="mt-6 text-center text-2xl font-extrabold text-slate-900">
          Official Student Attendance Portal
        </h2>
        <p className="mt-2 text-center text-sm text-slate-600">
          Or{' '}
          <Link to="/login" className="font-semibold text-indigo-600 hover:text-indigo-500">
            switch to faculty login
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
                Select Your Class & Section
              </label>
              <div className="mt-1 relative rounded-xl shadow-2xs">
                <select
                  required
                  value={selectedClassId}
                  onChange={(e) => setSelectedClassId(Number(e.target.value))}
                  className="block w-full py-2.5 px-3.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-600 focus:border-emerald-600 text-slate-900 bg-white"
                >
                  {classes.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} - {c.section} ({c.academic_year})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
                Roll Number / Student Code
              </label>
              <div className="mt-1 relative rounded-xl shadow-2xs">
                <input
                  type="text"
                  required
                  value={rollNumber}
                  onChange={(e) => setRollNumber(e.target.value)}
                  placeholder="e.g. CSE-2026-001"
                  className="block w-full py-2.5 px-3.5 text-sm uppercase font-medium border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-600 focus:border-emerald-600 text-slate-900 bg-white"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider flex items-center justify-between">
                <span>Security Passcode / Identifier</span>
                <span className="text-[10px] text-slate-400 font-normal">Optional / Required if set</span>
              </label>
              <div className="mt-1 relative rounded-xl shadow-2xs">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <KeyRound className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  value={secretPasscode}
                  onChange={(e) => setSecretPasscode(e.target.value)}
                  placeholder="Security verification code"
                  className="block w-full pl-10 pr-3.5 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-600 focus:border-emerald-600 text-slate-900 bg-white"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center items-center gap-2 py-2.5 px-4 border border-transparent rounded-xl shadow-sm text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-hidden focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-all disabled:opacity-60"
              >
                {isLoading ? 'Verifying...' : 'Access My Attendance'}
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>

          {/* Quick Fill Demo Student */}
          <div className="mt-8 pt-6 border-t border-slate-100">
            <button
              type="button"
              onClick={fillDemoStudent}
              className="w-full flex items-center justify-between p-3 rounded-xl border border-emerald-200 bg-emerald-50/50 hover:bg-emerald-50 transition-colors text-left"
            >
              <div className="flex items-center gap-2.5">
                <Sparkles className="w-4 h-4 text-emerald-600" />
                <div>
                  <span className="text-xs font-bold text-slate-800 block">
                    Quick-Fill Demo Student (Aarav Verma)
                  </span>
                  <span className="text-[10px] text-slate-500">Roll: CSE-2026-001 • Class A</span>
                </div>
              </div>
              <span className="text-xs font-bold text-emerald-700">1-Click Fill</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
