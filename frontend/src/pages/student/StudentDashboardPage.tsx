import React, { useEffect, useMemo, useState } from 'react';
import { CalendarDays, GraduationCap, TrendingUp, UserCircle2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { reportsApi, StudentOverallReport } from '../../api/reports';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';

export const StudentDashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [report, setReport] = useState<StudentOverallReport | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const load = async () => {
      if (!user?.student_id) return;
      try {
        setIsLoading(true);
        const result = await reportsApi.getStudentReport(user.student_id);
        setReport(result);
      } catch (error) {
        console.error('Failed to load student report:', error);
      } finally {
        setIsLoading(false);
      }
    };

    load();
  }, [user?.student_id]);

  const summary = useMemo(() => {
    if (!report) return null;

    return {
      percentage: report.overall_percentage ?? 0,
      conducted: report.total_conducted,
      attended: report.total_attended,
      absent: report.total_absent,
      halfDay: report.total_half_day,
    };
  }, [report]);

  if (!user?.student_id) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center text-slate-600">
        Student identity is not available for this session.
      </div>
    );
  }

  if (isLoading) {
    return <LoadingSpinner label="Loading your attendance dashboard..." className="h-64" />;
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div>
            <p className="text-xs font-bold tracking-wider text-emerald-600 uppercase">Student Workspace</p>
            <h1 className="text-2xl font-bold text-slate-900 mt-1">Welcome, {user.full_name}</h1>
          </div>
          <div className="flex items-center gap-2 rounded-xl bg-emerald-50 border border-emerald-200 px-3 py-2 text-sm font-semibold text-emerald-700">
            <UserCircle2 className="w-4 h-4" />
            Roll: {report?.roll_number || 'N/A'}
          </div>
        </div>
      </div>

      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold uppercase">
              <TrendingUp className="w-4 h-4 text-emerald-600" /> Overall
            </div>
            <div className="mt-3 text-3xl font-bold text-slate-900">{summary.percentage.toFixed(2)}%</div>
            <div className="mt-1 text-xs text-slate-500">Attendance percentage</div>
          </div>
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold uppercase">
              <GraduationCap className="w-4 h-4 text-indigo-600" /> Conducted
            </div>
            <div className="mt-3 text-3xl font-bold text-slate-900">{summary.conducted}</div>
            <div className="mt-1 text-xs text-slate-500">Official sessions</div>
          </div>
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold uppercase">
              <CalendarDays className="w-4 h-4 text-amber-600" /> Present
            </div>
            <div className="mt-3 text-3xl font-bold text-slate-900">{summary.attended}</div>
            <div className="mt-1 text-xs text-slate-500">Attended sessions</div>
          </div>
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold uppercase">
              <CalendarDays className="w-4 h-4 text-rose-600" /> Absence
            </div>
            <div className="mt-3 text-3xl font-bold text-slate-900">{summary.absent}</div>
            <div className="mt-1 text-xs text-slate-500">Absent + half-day</div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 className="text-lg font-bold text-slate-900">Subject-wise performance</h2>
        <div className="mt-4 space-y-3">
          {(report?.subject_summaries ?? []).map((subject) => (
            <div key={subject.subject_id} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex items-center justify-between gap-2 flex-wrap">
                <div>
                  <div className="font-semibold text-slate-800">{subject.subject_name}</div>
                  <div className="text-xs text-slate-500">{subject.subject_code}</div>
                </div>
                <div className="text-sm font-bold text-slate-900">
                  {subject.attendance_percentage === null ? 'N/A' : `${subject.attendance_percentage}%`}
                </div>
              </div>
              <div className="mt-2 text-xs text-slate-500">
                {subject.conducted_sessions} conducted • {subject.attended_sessions} attended • {subject.absent_sessions} absent
              </div>
            </div>
          ))}

          {(!report || report.subject_summaries.length === 0) && (
            <p className="text-sm text-slate-500">No subject attendance data is available yet.</p>
          )}
        </div>
      </div>
    </div>
  );
};
