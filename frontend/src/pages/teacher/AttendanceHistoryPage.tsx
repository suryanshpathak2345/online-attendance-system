import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  History,
  FileSpreadsheet,
  Edit3,
  Calendar,
  Search,
  Filter,
  CheckCircle2,
  XCircle,
  Clock,
  Shield,
  Eye,
} from 'lucide-react';
import { sessionsApi, ClassSessionItem } from '../../api/sessions';
import { attendanceApi, AttendanceSheetResponse, AttendanceAuditLogItem, AttendanceStatusType } from '../../api/attendance';
import { classesApi, ClassRoom } from '../../api/classes';
import { Badge } from '../../components/common/Badge';
import { Modal } from '../../components/common/Modal';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ToastContainer, ToastMessage } from '../../components/common/Toast';

export const AttendanceHistoryPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const urlSessionId = searchParams.get('sessionId');

  const [classes, setClasses] = useState<ClassRoom[]>([]);
  const [sessions, setSessions] = useState<ClassSessionItem[]>([]);
  const [selectedClassId, setSelectedClassId] = useState<number | ''>('');
  const [selectedSessionId, setSelectedSessionId] = useState<number | ''>(urlSessionId ? Number(urlSessionId) : '');

  const [sheet, setSheet] = useState<AttendanceSheetResponse | null>(null);
  const [auditLogs, setAuditLogs] = useState<AttendanceAuditLogItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Correction Modal State
  const [editingRecord, setEditingRecord] = useState<{
    recordId: number;
    studentName: string;
    studentRoll: string;
    currentStatus: AttendanceStatusType;
  } | null>(null);
  const [newStatus, setNewStatus] = useState<AttendanceStatusType>('PRESENT');
  const [correctionReason, setCorrectionReason] = useState('');
  const [isAuditModalOpen, setIsAuditModalOpen] = useState(false);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = (type: 'success' | 'error' | 'info', message: string) => {
    setToasts((prev) => [...prev, { id: Math.random().toString(), type, message }]);
  };

  useEffect(() => {
    const fetchInit = async () => {
      try {
        const cls = await classesApi.list();
        setClasses(cls);
        const sess = await sessionsApi.list({});
        setSessions(sess);
        if (urlSessionId) {
          setSelectedSessionId(Number(urlSessionId));
        } else if (sess.length > 0) {
          const submitted = sess.find((s) => s.is_attendance_submitted);
          setSelectedSessionId(submitted ? submitted.id : sess[0].id);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchInit();
  }, [urlSessionId]);

  useEffect(() => {
    if (!selectedSessionId) return;
    const fetchDetails = async () => {
      try {
        setIsLoading(true);
        const [sheetRes, logsRes] = await Promise.all([
          attendanceApi.getSheet(Number(selectedSessionId)),
          attendanceApi.getAuditLogs(Number(selectedSessionId)),
        ]);
        setSheet(sheetRes);
        setAuditLogs(logsRes);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchDetails();
  }, [selectedSessionId]);

  const handleOpenCorrection = (record: any) => {
    if (!record.record_id) return;
    setEditingRecord({
      recordId: record.record_id,
      studentName: record.full_name,
      studentRoll: record.roll_number,
      currentStatus: record.status || 'PRESENT',
    });
    setNewStatus(record.status === 'PRESENT' ? 'ABSENT' : 'PRESENT');
    setCorrectionReason('');
  };

  const handleSaveCorrection = async () => {
    if (!editingRecord) return;
    try {
      await attendanceApi.correctRecord(editingRecord.recordId, newStatus, correctionReason);
      addToast('success', `Attendance updated for ${editingRecord.studentName}`);
      setEditingRecord(null);

      // Refresh data
      const [sheetRes, logsRes] = await Promise.all([
        attendanceApi.getSheet(Number(selectedSessionId)),
        attendanceApi.getAuditLogs(Number(selectedSessionId)),
      ]);
      setSheet(sheetRes);
      setAuditLogs(logsRes);
    } catch (err: any) {
      addToast('error', err.response?.data?.detail || 'Correction failed');
    }
  };

  return (
    <div className="space-y-6">
      <ToastContainer toasts={toasts} onDismiss={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))} />

      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-2xs flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-indigo-600">
            Attendance Register Archive
          </span>
          <h1 className="text-2xl font-bold text-slate-900 mt-1">Attendance History & Audit Logs</h1>
          <p className="text-xs text-slate-500">
            Review finalized lecture attendance, edit individual student statuses, and view immutable audit trail.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setIsAuditModalOpen(true)}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-bold shadow-2xs transition-all"
          >
            <Shield className="w-4 h-4 text-purple-600" />
            Audit Trail ({auditLogs.length})
          </button>
        </div>
      </div>

      {/* Session Selection Dropdown */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-2xs flex flex-col sm:flex-row sm:items-center gap-3">
        <label className="text-xs font-bold text-slate-700 uppercase tracking-wider whitespace-nowrap">
          Select Lecture Session:
        </label>
        <select
          value={selectedSessionId}
          onChange={(e) => setSelectedSessionId(Number(e.target.value))}
          className="text-sm font-medium border border-slate-300 rounded-xl px-3.5 py-2 w-full max-w-lg bg-slate-50 focus:bg-white"
        >
          {sessions.map((s) => (
            <option key={s.id} value={s.id}>
              {s.session_date} • {s.subject_name} ({s.class_name}) • {s.is_attendance_submitted ? 'Submitted' : 'Pending'}
            </option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <LoadingSpinner label="Loading attendance history..." className="h-64" />
      ) : !sheet ? (
        <div className="bg-white p-12 text-center rounded-2xl border border-slate-200 text-slate-500 text-sm">
          No session selected.
        </div>
      ) : (
        <div className="space-y-4">
          {/* Session Overview Card */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-2xs flex flex-wrap items-center justify-between gap-4">
            <div>
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
                Session Record Details
              </span>
              <h3 className="text-base font-bold text-slate-900 mt-0.5">
                {sheet.subject_name} ({sheet.subject_code}) — {sheet.session_date}
              </h3>
              <p className="text-xs text-slate-500">
                Class: {sheet.class_name} ({sheet.class_section}) • Topic: {sheet.topic || 'Regular Class'}
              </p>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200">
                {sheet.present_count} Present
              </span>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-rose-50 text-rose-700 border border-rose-200">
                {sheet.absent_count} Absent
              </span>
              {sheet.half_day_count > 0 && (
                <span className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-amber-50 text-amber-700 border border-amber-200">
                  {sheet.half_day_count} Half-Day
                </span>
              )}
            </div>
          </div>

          {/* Student Records Table */}
          <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs overflow-hidden">
            <div className="p-4 border-b border-slate-200 bg-slate-50/70 flex items-center justify-between">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Student Attendance Records ({sheet.students.length})
              </span>
              <span className="text-xs text-slate-400">Click Edit to log a correction</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-600">
                <thead className="bg-slate-50 text-xs font-semibold uppercase text-slate-500 border-b border-slate-200">
                  <tr>
                    <th className="py-3 px-4">Roll No</th>
                    <th className="py-3 px-4">Student Name</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Remarks</th>
                    <th className="py-3 px-4 text-right">Correction</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {sheet.students.map((st) => (
                    <tr key={st.student_id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="py-3 px-4 font-bold text-slate-900">{st.roll_number}</td>
                      <td className="py-3 px-4 font-medium text-slate-900">{st.full_name}</td>
                      <td className="py-3 px-4">
                        {st.status === 'PRESENT' && (
                          <Badge variant="present" size="sm">
                            Present
                          </Badge>
                        )}
                        {st.status === 'ABSENT' && (
                          <Badge variant="absent" size="sm">
                            Absent
                          </Badge>
                        )}
                        {st.status === 'HALF_DAY' && (
                          <Badge variant="halfday" size="sm">
                            Half-Day
                          </Badge>
                        )}
                        {!st.status && <Badge variant="neutral" size="sm">Unmarked</Badge>}
                      </td>
                      <td className="py-3 px-4 text-xs text-slate-500">{st.remarks || '—'}</td>
                      <td className="py-3 px-4 text-right">
                        <button
                          type="button"
                          onClick={() => handleOpenCorrection(st)}
                          className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 px-2.5 py-1 rounded-lg transition-colors"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                          Correct
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Attendance Correction Modal */}
      {editingRecord && (
        <Modal
          isOpen={!!editingRecord}
          onClose={() => setEditingRecord(null)}
          title={`Correct Attendance: ${editingRecord.studentName}`}
          subtitle={`Roll Number: ${editingRecord.studentRoll} • Current: ${editingRecord.currentStatus}`}
          maxWidth="md"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Select New Attendance Status
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(['PRESENT', 'ABSENT', 'HALF_DAY'] as AttendanceStatusType[]).map((st) => (
                  <button
                    key={st}
                    type="button"
                    onClick={() => setNewStatus(st)}
                    className={`py-2 px-3 text-xs font-bold rounded-xl border transition-all ${
                      newStatus === st
                        ? 'border-indigo-600 bg-indigo-50 text-indigo-700 shadow-2xs'
                        : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    {st}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Correction Reason (Logged in Audit History)
              </label>
              <textarea
                rows={3}
                value={correctionReason}
                onChange={(e) => setCorrectionReason(e.target.value)}
                placeholder="e.g. Approved medical leave certificate submitted / Teacher clerical mistake"
                className="w-full text-xs border border-slate-300 rounded-xl p-2.5 text-slate-800 focus:ring-2 focus:ring-indigo-600 focus:border-indigo-600"
              />
            </div>

            <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={() => setEditingRecord(null)}
                className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSaveCorrection}
                className="px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-xs"
              >
                Apply Correction & Log
              </button>
            </div>
          </div>
        </Modal>
      )}

      {/* Audit Log Modal */}
      <Modal
        isOpen={isAuditModalOpen}
        onClose={() => setIsAuditModalOpen(false)}
        title="Session Attendance Audit Log"
        subtitle="Complete immutable history of all edits and submissions"
        maxWidth="xl"
      >
        {auditLogs.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-6">No edits recorded for this session yet.</p>
        ) : (
          <div className="space-y-3">
            {auditLogs.map((log) => (
              <div
                key={log.id}
                className="p-3.5 rounded-xl border border-slate-200/90 bg-slate-50/50 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-900">{log.student_name}</span>
                    <span className="text-[11px] font-semibold text-slate-500">({log.student_roll})</span>
                    <span className="text-xs text-slate-400">→</span>
                    <Badge variant={log.new_status === 'PRESENT' ? 'present' : 'absent'} size="sm">
                      {log.previous_status} ➔ {log.new_status}
                    </Badge>
                  </div>
                  {log.reason && <p className="text-xs text-slate-600 mt-1">Reason: {log.reason}</p>}
                </div>
                <div className="text-right sm:text-right text-[11px] text-slate-400">
                  <span className="font-medium text-slate-600 block">{log.changed_by_name}</span>
                  <span>{new Date(log.changed_at).toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </Modal>
    </div>
  );
};
