import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  GraduationCap,
  Users,
  Calendar,
  CheckCircle2,
  Clock,
  ArrowRight,
  FileSpreadsheet,
  BarChart3,
  CheckSquare,
  PlusCircle,
  AlertCircle,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { StatCard } from '../../components/common/StatCard';
import { Badge } from '../../components/common/Badge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { classesApi, ClassRoom } from '../../api/classes';
import { sessionsApi, ClassSessionItem } from '../../api/sessions';

export const TeacherDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user, role } = useAuth();

  const [classes, setClasses] = useState<ClassRoom[]>([]);
  const [sessions, setSessions] = useState<ClassSessionItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setIsLoading(true);
        const [cls, sess] = await Promise.all([
          classesApi.list(),
          sessionsApi.list({ teacher_id: role === 'admin' ? undefined : user?.id }),
        ]);
        setClasses(cls);
        setSessions(sess);
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      } finally {
        setIsLoading(false);
      }
    };
    loadDashboardData();
  }, [user, role]);

  if (isLoading) {
    return <LoadingSpinner label="Loading faculty dashboard..." className="h-64" />;
  }

  // Derive genuine stats from authorized data
  const totalClasses = classes.length;
  const totalStudents = classes.reduce((sum, c) => sum + (c.student_count || 0), 0);
  const completedSessions = sessions.filter((s) => s.is_attendance_submitted).length;
  const awaitingSessions = sessions.filter(
    (s) => !s.is_attendance_submitted && s.status === 'SCHEDULED'
  ).length;

  return (
    <div className="space-y-8">
      {/* Header Greeting */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200/90 shadow-2xs">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-indigo-600">
            {role === 'admin' ? 'Administrator Workspace' : 'Faculty Workspace'}
          </span>
          <h1 className="text-2xl font-bold text-slate-900 mt-1">
            Welcome back, {user?.full_name}
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Manage your scheduled classes, monitor absent rates, and mark today's attendance.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/teacher/mark-attendance"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 text-white font-semibold text-sm hover:bg-indigo-700 shadow-sm transition-all"
          >
            <CheckSquare className="w-4 h-4" />
            Mark Attendance
          </Link>
          <Link
            to="/teacher/export"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-700 font-semibold text-sm hover:bg-slate-50 shadow-2xs transition-all"
          >
            <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
            Excel Export
          </Link>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Assigned Classes"
          value={totalClasses}
          subtitle="Active academic cohorts"
          icon={GraduationCap}
          color="indigo"
        />
        <StatCard
          title="Total Students"
          value={totalStudents}
          subtitle="Enrolled under your classes"
          icon={Users}
          color="purple"
        />
        <StatCard
          title="Attendance Completed"
          value={completedSessions}
          subtitle="Finalized lecture records"
          icon={CheckCircle2}
          color="emerald"
        />
        <StatCard
          title="Awaiting Attendance"
          value={awaitingSessions}
          subtitle="Pending submission"
          icon={Clock}
          color={awaitingSessions > 0 ? 'amber' : 'slate'}
          badge={awaitingSessions > 0 ? { text: 'Needs Action', variant: 'warning' } : undefined}
        />
      </div>

      {/* Assigned Classes / Courses Cards */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Assigned Classes & Subjects</h2>
            <p className="text-xs text-slate-500">Quick actions for your assigned cohorts</p>
          </div>
          <Link
            to="/teacher/classes"
            className="text-xs font-semibold text-indigo-600 hover:text-indigo-700"
          >
            View all classes →
          </Link>
        </div>

        {classes.length === 0 ? (
          <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center">
            <GraduationCap className="w-10 h-10 text-slate-300 mx-auto mb-2" />
            <h3 className="text-sm font-semibold text-slate-700">No classes assigned yet</h3>
            <p className="text-xs text-slate-500 mt-1">
              Classes assigned to your faculty profile will appear here.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {classes.map((c) => (
              <div
                key={c.id}
                className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-2xs hover:shadow-sm transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700">
                      {c.academic_year}
                    </span>
                    <Badge variant="primary" size="sm">
                      {c.section}
                    </Badge>
                  </div>
                  <h3 className="text-base font-bold text-slate-900 leading-snug">{c.name}</h3>
                  <div className="mt-3 flex items-center gap-4 text-xs text-slate-500">
                    <span className="flex items-center gap-1.5">
                      <Users className="w-3.5 h-3.5 text-slate-400" />
                      {c.student_count} Students
                    </span>
                    <span className="flex items-center gap-1.5">
                      <GraduationCap className="w-3.5 h-3.5 text-slate-400" />
                      {c.subject_count} Subjects
                    </span>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-100 grid grid-cols-2 gap-2">
                  <Link
                    to={`/teacher/mark-attendance?classId=${c.id}`}
                    className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl bg-indigo-50 text-indigo-700 text-xs font-semibold hover:bg-indigo-100 transition-colors"
                  >
                    <CheckSquare className="w-3.5 h-3.5" />
                    Mark Session
                  </Link>
                  <Link
                    to={`/teacher/reports?classId=${c.id}`}
                    className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl border border-slate-200 text-slate-700 text-xs font-semibold hover:bg-slate-50 transition-colors"
                  >
                    <BarChart3 className="w-3.5 h-3.5 text-slate-500" />
                    Reports
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recent Sessions Table */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs overflow-hidden">
        <div className="p-5 border-b border-slate-200/80 flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900">Recent Class Sessions</h3>
            <p className="text-xs text-slate-500">Scheduled and conducted attendance activity</p>
          </div>
          <Link
            to="/teacher/history"
            className="text-xs font-semibold text-indigo-600 hover:text-indigo-700"
          >
            Full History →
          </Link>
        </div>

        {sessions.length === 0 ? (
          <div className="p-8 text-center text-sm text-slate-500">No sessions recorded yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-xs font-semibold uppercase text-slate-500 tracking-wider border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Subject</th>
                  <th className="py-3 px-4">Class</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Present / Absent</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-normal">
                {sessions.slice(0, 6).map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3.5 px-4 font-medium text-slate-900 whitespace-nowrap">
                      {s.session_date}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-slate-900">{s.subject_name}</div>
                      <div className="text-xs text-slate-400">{s.subject_code}</div>
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      {s.class_name} ({s.class_section})
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      {s.is_attendance_submitted ? (
                        <Badge variant="present" size="sm">
                          Conducted
                        </Badge>
                      ) : s.status === 'CANCELLED' ? (
                        <Badge variant="cancelled" size="sm">
                          Cancelled
                        </Badge>
                      ) : (
                        <Badge variant="warning" size="sm">
                          Awaiting Attendance
                        </Badge>
                      )}
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      {s.is_attendance_submitted ? (
                        <span className="text-xs font-medium">
                          <span className="text-emerald-600 font-bold">{s.present_count} P</span>
                          {' / '}
                          <span className="text-rose-600 font-bold">{s.absent_count} A</span>
                        </span>
                      ) : (
                        <span className="text-xs text-slate-400">Not recorded</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-right whitespace-nowrap">
                      {s.is_attendance_submitted ? (
                        <Link
                          to={`/teacher/history?sessionId=${s.id}`}
                          className="text-xs font-semibold text-indigo-600 hover:text-indigo-800"
                        >
                          View Details
                        </Link>
                      ) : (
                        <Link
                          to={`/teacher/mark-attendance?sessionId=${s.id}`}
                          className="text-xs font-bold text-indigo-600 hover:text-indigo-800 bg-indigo-50 px-2.5 py-1 rounded-lg"
                        >
                          Mark Now
                        </Link>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
