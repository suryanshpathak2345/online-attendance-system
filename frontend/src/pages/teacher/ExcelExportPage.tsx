import React, { useState, useEffect } from 'react';
import {
  FileSpreadsheet,
  Download,
  Calendar,
  CheckCircle2,
  Info,
  ShieldAlert,
} from 'lucide-react';
import { classesApi, ClassRoom } from '../../api/classes';
import { subjectsApi, SubjectItem } from '../../api/subjects';
import { reportsApi } from '../../api/reports';
import { ToastContainer, ToastMessage } from '../../components/common/Toast';

export const ExcelExportPage: React.FC = () => {
  const [classes, setClasses] = useState<ClassRoom[]>([]);
  const [subjects, setSubjects] = useState<SubjectItem[]>([]);
  const [selectedClassId, setSelectedClassId] = useState<number | ''>('');
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | ''>('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const [isExporting, setIsExporting] = useState(false);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  useEffect(() => {
    const fetchClasses = async () => {
      try {
        const cls = await classesApi.list();
        setClasses(cls);
        if (cls.length > 0) setSelectedClassId(cls[0].id);
      } catch (err) {
        console.error(err);
      }
    };
    fetchClasses();
  }, []);

  useEffect(() => {
    if (!selectedClassId) return;
    const fetchSubjs = async () => {
      try {
        const list = await subjectsApi.list(Number(selectedClassId));
        setSubjects(list);
        if (list.length > 0) setSelectedSubjectId(list[0].id);
      } catch (err) {
        console.error(err);
      }
    };
    fetchSubjs();
  }, [selectedClassId]);

  const handleDownload = async () => {
    if (!selectedClassId || !selectedSubjectId) return;
    setIsExporting(true);
    try {
      await reportsApi.downloadExcel(
        Number(selectedClassId),
        Number(selectedSubjectId),
        startDate || undefined,
        endDate || undefined
      );
      setToasts((prev) => [
        ...prev,
        { id: Math.random().toString(), type: 'success', message: 'Excel attendance register downloaded successfully.' },
      ]);
    } catch (err: any) {
      setToasts((prev) => [
        ...prev,
        { id: Math.random().toString(), type: 'error', message: err.response?.data?.detail || 'Export failed.' },
      ]);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <ToastContainer toasts={toasts} onDismiss={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))} />

      <div className="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-2xs">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-emerald-50 text-emerald-600">
            <FileSpreadsheet className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Official Excel Register Export</h1>
            <p className="text-xs text-slate-500">
              Download formatted openpyxl workbooks ready for academic record keeping and printing.
            </p>
          </div>
        </div>
      </div>

      {/* Export Form */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-2xs space-y-5">
        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
          Export Parameters
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Class & Section
            </label>
            <select
              value={selectedClassId}
              onChange={(e) => setSelectedClassId(Number(e.target.value))}
              className="w-full text-sm font-medium border border-slate-300 rounded-xl px-3.5 py-2.5 bg-slate-50 focus:bg-white"
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
              Course Subject
            </label>
            <select
              value={selectedSubjectId}
              onChange={(e) => setSelectedSubjectId(Number(e.target.value))}
              className="w-full text-sm font-medium border border-slate-300 rounded-xl px-3.5 py-2.5 bg-slate-50 focus:bg-white"
            >
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.code})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Start Date (Optional)
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full text-sm border border-slate-300 rounded-xl px-3.5 py-2.5 bg-slate-50 focus:bg-white"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              End Date (Optional)
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full text-sm border border-slate-300 rounded-xl px-3.5 py-2.5 bg-slate-50 focus:bg-white"
            />
          </div>
        </div>

        {/* Informational Format Details */}
        <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600 space-y-2">
          <div className="flex items-center gap-2 font-bold text-slate-800">
            <Info className="w-4 h-4 text-indigo-600" />
            <span>Spreadsheet Register Standard Structure</span>
          </div>
          <ul className="list-disc list-inside space-y-1 text-slate-500 pl-1">
            <li>Standard institutional header (Institution, Class, Subject, Faculty, Academic Year).</li>
            <li>Date-by-date student attendance columns (P = Present, A = Absent, HD = Half-Day, H = Holiday, C = Cancelled).</li>
            <li>Summary columns automatically matching verified backend database calculations.</li>
            <li>Clear colored cell styling and safe filename formatting.</li>
          </ul>
        </div>

        <button
          type="button"
          onClick={handleDownload}
          disabled={isExporting || !selectedClassId || !selectedSubjectId}
          className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md transition-all disabled:opacity-50"
        >
          <Download className="w-4 h-4" />
          {isExporting ? 'Generating Spreadsheet...' : 'Download Attendance Register (.xlsx)'}
        </button>
      </div>
    </div>
  );
};
