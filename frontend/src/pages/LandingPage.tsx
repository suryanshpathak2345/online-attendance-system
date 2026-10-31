import React from 'react';
import { Link } from 'react-router-dom';
import {
  CheckSquare,
  Users,
  GraduationCap,
  Calendar,
  FileSpreadsheet,
  Shield,
  ArrowRight,
  Sparkles,
  BarChart3,
  Clock,
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-50 text-slate-900">
      {/* Top Navbar */}
      <header className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-100">
            <CheckSquare className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xl font-bold tracking-tight text-slate-900 block leading-none">
              AttendEase
            </span>
            <span className="text-xs text-slate-500 font-medium">Online Attendance System</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/student-access"
            className="text-sm font-semibold text-slate-600 hover:text-indigo-600 px-4 py-2 rounded-lg transition-colors"
          >
            Student Access
          </Link>
          <Link
            to="/login"
            className="text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 px-5 py-2.5 rounded-xl shadow-sm transition-all"
          >
            Teacher Login
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-5xl mx-auto px-6 pt-16 pb-20 text-center">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-700 text-xs font-semibold mb-6">
          <Sparkles className="w-3.5 h-3.5" />
          Official Academic Attendance & Analytics System
        </div>
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 leading-tight">
          Fast for Teachers.{' '}
          <span className="bg-gradient-to-r from-indigo-600 to-brand-500 bg-clip-text text-transparent">
            Simple for Students.
          </span>
        </h1>
        <p className="mt-6 text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
          Modern, reliable attendance management built for colleges and schools. One-click batch attendance marking, absent verification, official Excel registers, and live student calendar tracking.
        </p>

        {/* Action Cards */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-left max-w-4xl mx-auto">
          {/* Teacher Portal */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-sm hover:shadow-md transition-all flex flex-col justify-between group">
            <div>
              <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                <Users className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">Faculty & Teachers</h3>
              <p className="text-sm text-slate-500 mt-2 leading-relaxed">
                Take session attendance with one-click All Present, verify absentees, correct records with audit history, and export formatted registers.
              </p>
            </div>
            <Link
              to="/login"
              className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-indigo-600 group-hover:text-indigo-700"
            >
              Sign In to Faculty Portal <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Student Portal */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-sm hover:shadow-md transition-all flex flex-col justify-between group">
            <div>
              <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                <GraduationCap className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">Student Portal</h3>
              <p className="text-sm text-slate-500 mt-2 leading-relaxed">
                Check official attendance records, subject-wise statistics against the 75% threshold, and view the monthly attendance calendar.
              </p>
            </div>
            <Link
              to="/student-access"
              className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-emerald-600 group-hover:text-emerald-700"
            >
              Student Portal Access <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Personal Tracker */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-sm hover:shadow-md transition-all flex flex-col justify-between group">
            <div>
              <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                <Sparkles className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">Personal Tracker</h3>
              <p className="text-sm text-slate-500 mt-2 leading-relaxed">
                Maintain an isolated self-study and private tracker without modifying official academic attendance records.
              </p>
            </div>
            <Link
              to="/student-access"
              className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-amber-600 group-hover:text-amber-700"
            >
              Launch Personal Tracker <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="bg-slate-100/60 py-20 border-y border-slate-200/80">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <h2 className="text-3xl font-bold tracking-tight text-slate-900">
              Complete Academic Attendance Infrastructure
            </h2>
            <p className="mt-3 text-slate-600">
              Designed with strict institutional validation, relational integrity, and seamless usability.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-2xs">
              <Clock className="w-6 h-6 text-indigo-600 mb-3" />
              <h4 className="font-bold text-slate-900">Rapid Marking Workflow</h4>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Mark 60+ students in seconds using quick actions, with mandatory absentee verification before commit.
              </p>
            </div>
            <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-2xs">
              <Calendar className="w-6 h-6 text-emerald-600 mb-3" />
              <h4 className="font-bold text-slate-900">Holiday & Session Logic</h4>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Holidays and cancelled classes are automatically excluded from the conducted denominator.
              </p>
            </div>
            <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-2xs">
              <FileSpreadsheet className="w-6 h-6 text-blue-600 mb-3" />
              <h4 className="font-bold text-slate-900">Official Excel Export</h4>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Generate traditional styled attendance registers using openpyxl with date-by-date student matrices.
              </p>
            </div>
            <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-2xs">
              <Shield className="w-6 h-6 text-purple-600 mb-3" />
              <h4 className="font-bold text-slate-900">Audit & Corrections</h4>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Every manual status correction is recorded with the editor, previous state, timestamp, and justification reason.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto px-6 py-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
        <p>© 2026 AttendEase. Apex Institute of Technology - Online Attendance Management System.</p>
        <div className="flex items-center gap-6">
          <Link to="/login" className="hover:text-slate-900">
            Faculty Login
          </Link>
          <Link to="/student-access" className="hover:text-slate-900">
            Student Access
          </Link>
        </div>
      </footer>
    </div>
  );
};
