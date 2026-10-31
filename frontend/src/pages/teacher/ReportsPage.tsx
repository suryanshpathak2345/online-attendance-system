import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import {
  BarChart3,
  FileSpreadsheet,
  AlertTriangle,
  Users,
  CheckCircle2,
  Sliders,
  Filter,
  Download,
} from 'lucide-react';
import { classesApi, ClassRoom } from '../../api/classes';
import { subjectsApi, SubjectItem } from '../../api/subjects';
import { reportsApi, ClassAttendanceReport } from '../../api/reports';
import { StatCard } from '../../components/common/StatCard';
import { Badge } from '../../components/common/Badge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';

export const ReportsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const urlClassId = searchParams.get('classId');

  const [classes, setClasses] = useState<ClassRoom[]>([]);
  const [subjects, setSubjects] = useState<SubjectItem[]>([]);
  const [selectedClassId, setSelectedClassId] = useState<number | ''>(urlClassId ? Number(urlClassId) : '');
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | ''>('');
  const [threshold, setThreshold] = useState<number>(75);
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  const [report, setReport] = useState<ClassAttendanceReport | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchInit = async () => {
      try {
        const cls = await classesApi.list();
        setClasses(cls);
        if (!selectedClassId && cls.length > 0) {
          setSelectedClassId(cls[0].id);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchInit();
  }, [urlClassId]);

  useEffect(() => {
    if (!selectedClassId) return;
    const fetchSubjs = async () => {
      try {
        const list = await subjectsApi.list(Number(selectedClassId));
        setSubjects(list);
      } catch (err) {
        console.error(err);
      }
    };
    fetchSubjs();
  }, [selectedClassId]);

  useEffect(() => {
    if (!selectedClassId) return;
    const loadReport = async () => {
      try {
        setIsLoading(true);
        const data = await reportsApi.getClassReport(Number(selectedClassId), {
          subject_id: selectedSubjectId ? Number(selectedSubjectId) : undefined,
          threshold,
          start_date: startDate || undefined,
          end_date: endDate || undefined,
        });
        setReport(data);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    loadReport();
  }, [selectedClassId, selectedSubjectId, threshold, startDate, endDate]);

  const handleExport = async () => {
    if (!selectedClassId) return;
    const subjId = selectedSubjectId ? Number(selectedSubjectId) : subjects[0]?.id;
    if (!subjId) return;
    await reportsApi.downloadExcel(Number(selectedClassId), subjId, startDate || undefined, endDate || undefined);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-2xs flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-indigo-600">
            Attendance Reports & Analytics
          </span>
          <h1 className="text-2xl font-bold text-slate-900 mt-1">Class Attendance Analytics</h1>
          <p className="text-xs text-slate-500">
            Detailed attendance performance matrices, low-attendance alerts, and configurable thresholds.
          </p>
        </div>

        <button
          type="button"
          onClick={handleExport}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-sm transition-all"
        >
          <FileSpreadsheet className="w-4 h-4" />
          Export to Excel
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-2xs grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
            Class & Section
          </label>
          <select
            value={selectedClassId}
            onChange={(e) => setSelectedClassId(Number(e.target.value))}
            className="w-full text-xs font-medium border border-slate-300 rounded-xl px-3 py-2 bg-slate-50 focus:bg-white"
          >
            {classes.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name} - {c.section}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
            Subject (Optional)
          </label>
          <select
            value={selectedSubjectId}
            onChange={(e) => setSelectedSubjectId(e.target.value ? Number(e.target.value) : '')}
            className="w-full text-xs font-medium border border-slate-300 rounded-xl px-3 py-2 bg-slate-50 focus:bg-white"
          >
            <option value="">All Subjects Combined</option>
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} ({s.code})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1 flex justify-between">
            <span>Threshold Flag</span>
            <span className="text-indigo-600 font-bold">{threshold}%</span>
          </label>
          <input
            type="range"
            min="50"
            max="95"
            step="5"
            value={threshold}
            onChange={(e) => setThreshold(Number(e.target.value))}
            className="w-full accent-indigo-600 mt-2"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
            Date Filter (Optional)
          </label>
          <div className="flex gap-2">
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-1/2 text-xs border border-slate-300 rounded-xl px-2 py-1.5 bg-slate-50"
            />
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-1/2 text-xs border border-slate-300 rounded-xl px-2 py-1.5 bg-slate-50"
            />
          </div>
        </div>
      </div>

      {isLoading ? (
        <LoadingSpinner label="Compiling attendance statistics..." className="h-64" />
      ) : !report ? (
        <div className="bg-white p-12 text-center rounded-2xl border border-slate-200 text-slate-500">
          No report data found.
        </div>
      ) : (
        <div className="space-y-6">
          {/* Summary Stat Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            <StatCard
              title="Class Average"
              value={report.average_attendance_percentage ? `${report.average_attendance_percentage}%` : 'N/A'}
              subtitle="Mean attendance score"
              icon={BarChart3}
              color="indigo"
            />
            <StatCard
              title="Conducted Sessions"
              value={report.total_conducted_sessions}
              subtitle="Excluding holidays & cancelled"
              icon={CheckCircle2}
              color="emerald"
            />
            <StatCard
              title="Enrolled Students"
              value={report.students_count}
              subtitle="Active cohort enrollment"
              icon={Users}
              color="purple"
            />
            <StatCard
              title="Below Threshold"
              value={report.low_attendance_count}
              subtitle={`Below ${threshold}% attendance`}
              icon={AlertTriangle}
              color={report.low_attendance_count > 0 ? 'rose' : 'slate'}
              badge={report.low_attendance_count > 0 ? { text: 'Alert', variant: 'absent' } : undefined}
            />
          </div>

          {/* Student-wise Attendance Table */}
          <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs overflow-hidden">
            <div className="p-4 border-b border-slate-200 bg-slate-50/70 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Student Breakdown Table</h3>
                <p className="text-xs text-slate-500">
                  Calculated from validated attendance records
                </p>
              </div>
              <span className="text-xs text-slate-400 font-medium">
                Target: {threshold}%
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-600">
                <thead className="bg-slate-50 text-xs font-semibold uppercase text-slate-500 border-b border-slate-200">
                  <tr>
                    <th className="py-3 px-4">Roll No</th>
                    <th className="py-3 px-4">Student Name</th>
                    <th className="py-3 px-4 text-center">Conducted</th>
                    <th className="py-3 px-4 text-center">Attended</th>
                    <th className="py-3 px-4 text-center">Absent</th>
                    <th className="py-3 px-4 text-center">Attendance %</th>
                    <th className="py-3 px-4 text-center">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {report.student_rows.map((row) => (
                    <tr
                      key={row.student_id}
                      className={`hover:bg-slate-50/50 transition-colors ${
                        row.is_below_threshold ? 'bg-rose-50/20' : ''
                      }`}
                    >
                      <td className="py-3.5 px-4 font-bold text-slate-900">{row.roll_number}</td>
                      <td className="py-3.5 px-4 font-medium text-slate-900">{row.full_name}</td>
                      <td className="py-3.5 px-4 text-center font-semibold text-slate-700">
                        {row.conducted_sessions}
                      </td>
                      <td className="py-3.5 px-4 text-center font-semibold text-emerald-700">
                        {row.attended_sessions}
                      </td>
                      <td className="py-3.5 px-4 text-center font-semibold text-rose-700">
                        {row.absent_sessions}
                      </td>
                      <td className="py-3.5 px-4 text-center font-bold text-slate-900">
                        {row.attendance_percentage !== null ? `${row.attendance_percentage}%` : 'N/A'}
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        {row.is_below_threshold ? (
                          <Badge variant="absent" size="sm">
                            Shortage (&lt;{threshold}%)
                          </Badge>
                        ) : row.attendance_percentage !== null ? (
                          <Badge variant="present" size="sm">
                            Eligible
                          </Badge>
                        ) : (
                          <Badge variant="neutral" size="sm">
                            No Classes
                          </Badge>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
