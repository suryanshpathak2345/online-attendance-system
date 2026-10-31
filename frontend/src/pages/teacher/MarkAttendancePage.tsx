import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  CheckSquare,
  Users,
  CheckCircle2,
  XCircle,
  Clock,
  RotateCcw,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
  Check,
  X,
  FileCheck2,
  Calendar,
  AlertCircle,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { classesApi, ClassRoom } from '../../api/classes';
import { subjectsApi, SubjectItem } from '../../api/subjects';
import { sessionsApi, ClassSessionItem } from '../../api/sessions';
import { attendanceApi, AttendanceSheetResponse, AttendanceStatusType } from '../../api/attendance';
import { Badge } from '../../components/common/Badge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ConfirmDialog } from '../../components/common/ConfirmDialog';
import { ToastContainer, ToastMessage } from '../../components/common/Toast';

export const MarkAttendancePage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  // URL query params
  const paramSessionId = searchParams.get('sessionId');
  const paramClassId = searchParams.get('classId');

  // State
  const [classes, setClasses] = useState<ClassRoom[]>([]);
  const [subjects, setSubjects] = useState<SubjectItem[]>([]);
  const [sessions, setSessions] = useState<ClassSessionItem[]>([]);

  const [selectedClassId, setSelectedClassId] = useState<number | ''>(paramClassId ? Number(paramClassId) : '');
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | ''>('');
  const [selectedSessionId, setSelectedSessionId] = useState<number | ''>(paramSessionId ? Number(paramSessionId) : '');

  // Session Sheet Data
  const [sheet, setSheet] = useState<AttendanceSheetResponse | null>(null);
  const [studentStatuses, setStudentStatuses] = useState<{ [studentId: number]: AttendanceStatusType | null }>({});
  const [studentRemarks, setStudentRemarks] = useState<{ [studentId: number]: string }>({});

  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // Dialog & Toast State
  const [isConfirmSubmitOpen, setIsConfirmSubmitOpen] = useState(false);
  const [isResetConfirmOpen, setIsResetConfirmOpen] = useState(false);
  const [incompleteWarning, setIncompleteWarning] = useState<string | null>(null);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = (type: 'success' | 'error' | 'info', message: string) => {
    setToasts((prev) => [...prev, { id: Math.random().toString(), type, message }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  // 1. Initial Load: Classes
  useEffect(() => {
    const loadClasses = async () => {
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
    loadClasses();
  }, []);

  // 2. Load Subjects when Class changes
  useEffect(() => {
    if (!selectedClassId) return;
    const loadSubjects = async () => {
      try {
        const subjs = await subjectsApi.list(Number(selectedClassId));
        setSubjects(subjs);
        if (subjs.length > 0) {
          setSelectedSubjectId(subjs[0].id);
        } else {
          setSelectedSubjectId('');
        }
      } catch (err) {
        console.error(err);
      }
    };
    loadSubjects();
  }, [selectedClassId]);

  // 3. Load Sessions for Class & Subject
  useEffect(() => {
    if (!selectedClassId || !selectedSubjectId) return;
    const loadSessions = async () => {
      try {
        const sessList = await sessionsApi.list({
          class_id: Number(selectedClassId),
          subject_id: Number(selectedSubjectId),
        });
        setSessions(sessList);
        if (paramSessionId) {
          setSelectedSessionId(Number(paramSessionId));
        } else if (sessList.length > 0) {
          // Select newest session or first awaiting
          const pending = sessList.find((s) => !s.is_attendance_submitted);
          setSelectedSessionId(pending ? pending.id : sessList[0].id);
        } else {
          setSelectedSessionId('');
        }
      } catch (err) {
        console.error(err);
      }
    };
    loadSessions();
  }, [selectedClassId, selectedSubjectId, paramSessionId]);

  // 4. Load Attendance Sheet when Session changes
  useEffect(() => {
    if (!selectedSessionId) {
      setSheet(null);
      return;
    }
    const loadSheet = async () => {
      try {
        setIsLoading(true);
        setIncompleteWarning(null);
        const res = await attendanceApi.getSheet(Number(selectedSessionId));
        setSheet(res);

        // Populate local marking map
        const statusMap: { [studentId: number]: AttendanceStatusType | null } = {};
        const remarksMap: { [studentId: number]: string } = {};

        res.students.forEach((st) => {
          statusMap[st.student_id] = st.status;
          remarksMap[st.student_id] = st.remarks || '';
        });

        setStudentStatuses(statusMap);
        setStudentRemarks(remarksMap);
        setHasUnsavedChanges(false);
      } catch (err: any) {
        addToast('error', err.response?.data?.detail || 'Failed to load attendance sheet');
      } finally {
        setIsLoading(false);
      }
    };
    loadSheet();
  }, [selectedSessionId]);

  // Handle Quick Create Session if no session exists today
  const handleQuickCreateSession = async () => {
    if (!selectedClassId || !selectedSubjectId) return;
    try {
      setIsLoading(true);
      const todayStr = new Date().toISOString().split('T')[0];
      const newSess = await sessionsApi.create({
        class_id: Number(selectedClassId),
        subject_id: Number(selectedSubjectId),
        session_date: todayStr,
        topic: 'Regular Lecture Session',
      });
      addToast('success', 'New class session created for today.');
      setSessions((prev) => [newSess, ...prev]);
      setSelectedSessionId(newSess.id);
    } catch (err: any) {
      addToast('error', err.response?.data?.detail || 'Could not create class session.');
    } finally {
      setIsLoading(false);
    }
  };

  // Step 4: ALL PRESENT
  const handleAllPresent = () => {
    if (!sheet) return;
    const nextStatuses: { [studentId: number]: AttendanceStatusType | null } = {};
    sheet.students.forEach((st) => {
      nextStatuses[st.student_id] = 'PRESENT';
    });
    setStudentStatuses(nextStatuses);
    setHasUnsavedChanges(true);
    setIncompleteWarning(null);
    addToast('info', 'All students marked PRESENT. Individual students can still be marked absent.');
  };

  // Step 5: Reset / Clear Selections
  const handleResetConfirm = () => {
    if (!sheet) return;
    const resetMap: { [studentId: number]: AttendanceStatusType | null } = {};
    sheet.students.forEach((st) => {
      resetMap[st.student_id] = null;
    });
    setStudentStatuses(resetMap);
    setHasUnsavedChanges(true);
    setIsResetConfirmOpen(false);
    addToast('info', 'Attendance selections cleared.');
  };

  // Individual Status Toggle
  const handleSetStudentStatus = (studentId: number, status: AttendanceStatusType) => {
    setStudentStatuses((prev) => ({
      ...prev,
      [studentId]: status,
    }));
    setHasUnsavedChanges(true);
    setIncompleteWarning(null);
  };

  // Calculation of Live Summary Stats
  const totalStudents = sheet?.students.length || 0;
  const presentStudents = Object.values(studentStatuses).filter((s) => s === 'PRESENT').length;
  const absentStudents = Object.values(studentStatuses).filter((s) => s === 'ABSENT').length;
  const halfDayStudents = Object.values(studentStatuses).filter((s) => s === 'HALF_DAY').length;
  const notMarkedStudents = Object.values(studentStatuses).filter((s) => s === null || s === undefined).length;

  // Step 7: Get list of currently marked absent students for verification
  const absentList = (sheet?.students || []).filter((st) => studentStatuses[st.student_id] === 'ABSENT');

  // Step 8 & 10: Validation Before Confirmation
  const handlePreSubmitCheck = () => {
    if (!sheet) return;

    // Check if any student remains NOT MARKED
    const unmarked = sheet.students.filter(
      (st) => studentStatuses[st.student_id] === null || studentStatuses[st.student_id] === undefined
    );

    if (unmarked.length > 0) {
      const names = unmarked.map((st) => `${st.full_name} (${st.roll_number})`).slice(0, 3).join(', ');
      setIncompleteWarning(
        `Incomplete Attendance: ${unmarked.length} student(s) remain NOT MARKED (${names}${
          unmarked.length > 3 ? '...' : ''
        }). You must assign PRESENT, ABSENT, or HALF-DAY to all students before final submission.`
      );
      return;
    }

    setIncompleteWarning(null);
    setIsConfirmSubmitOpen(true);
  };

  // Step 11: Final Submission Transaction
  const handleFinalSubmit = async () => {
    if (!sheet || !selectedSessionId) return;
    setIsSubmitting(true);

    try {
      const records = sheet.students.map((st) => ({
        student_id: st.student_id,
        status: studentStatuses[st.student_id] as AttendanceStatusType,
        remarks: studentRemarks[st.student_id] || undefined,
      }));

      const res = await attendanceApi.submit(Number(selectedSessionId), { records });
      setIsConfirmSubmitOpen(false);
      setHasUnsavedChanges(false);
      addToast('success', res.message || 'Attendance successfully submitted!');

      // Reload fresh sheet
      const updated = await attendanceApi.getSheet(Number(selectedSessionId));
      setSheet(updated);
    } catch (err: any) {
      addToast('error', err.response?.data?.detail || 'Failed to submit attendance');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <ToastContainer toasts={toasts} onDismiss={removeToast} />

      {/* Page Title & Class/Subject Selectors */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-2xs space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-indigo-600">
                Official Attendance Workflow
              </span>
              {sheet?.is_attendance_submitted && (
                <Badge variant="success" size="sm">
                  Finalized & Saved
                </Badge>
              )}
              {hasUnsavedChanges && (
                <Badge variant="warning" size="sm">
                  Unsaved Changes
                </Badge>
              )}
            </div>
            <h1 className="text-2xl font-bold text-slate-900 mt-1">Mark Class Attendance</h1>
            <p className="text-xs text-slate-500">
              Select class, subject, and session. Complete all student records before submission.
            </p>
          </div>
        </div>

        {/* Step 1 Selector Toolbar */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-slate-100">
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              1. Class & Section
            </label>
            <select
              value={selectedClassId}
              onChange={(e) => setSelectedClassId(Number(e.target.value))}
              className="w-full text-sm font-medium border border-slate-300 rounded-xl px-3 py-2 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-600"
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
              2. Subject
            </label>
            <select
              value={selectedSubjectId}
              onChange={(e) => setSelectedSubjectId(Number(e.target.value))}
              className="w-full text-sm font-medium border border-slate-300 rounded-xl px-3 py-2 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-600"
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
              3. Session / Date
            </label>
            <div className="flex gap-2">
              <select
                value={selectedSessionId}
                onChange={(e) => setSelectedSessionId(Number(e.target.value))}
                className="w-full text-sm font-medium border border-slate-300 rounded-xl px-3 py-2 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-600"
              >
                {sessions.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.session_date} - {s.topic || 'Session'} ({s.is_attendance_submitted ? 'Submitted' : 'Pending'})
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={handleQuickCreateSession}
                title="Create Today's Session"
                className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl whitespace-nowrap transition-colors"
              >
                + New
              </button>
            </div>
          </div>
        </div>
      </div>

      {isLoading ? (
        <LoadingSpinner label="Fetching enrolled student roster..." className="h-64" />
      ) : !sheet ? (
        <div className="bg-white p-12 text-center rounded-2xl border border-slate-200">
          <Calendar className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-800">No session selected</h3>
          <p className="text-sm text-slate-500 mt-1">
            Choose a valid session from the dropdown above or click "+ New" to schedule a lecture.
          </p>
        </div>
      ) : (
        <>
          {/* Step 6: Live Attendance Summary Bar */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-2xs">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex flex-wrap items-center gap-3">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Summary:
                </span>
                <span className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700">
                  Enrolled: <strong className="text-slate-900">{totalStudents}</strong>
                </span>
                <span className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200">
                  Present: <strong className="text-emerald-900">{presentStudents}</strong>
                </span>
                <span className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-rose-50 text-rose-700 border border-rose-200">
                  Absent: <strong className="text-rose-900">{absentStudents}</strong>
                </span>
                <span className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-amber-50 text-amber-700 border border-amber-200">
                  Half-Day: <strong className="text-amber-900">{halfDayStudents}</strong>
                </span>
                {notMarkedStudents > 0 && (
                  <span className="text-xs font-bold px-3 py-1.5 rounded-lg bg-red-100 text-red-800 animate-pulse">
                    Not Marked: {notMarkedStudents}
                  </span>
                )}
              </div>

              {/* Action Buttons: Step 4 (ALL PRESENT) & Step 5 (Reset) */}
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleAllPresent}
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-all shadow-2xs"
                >
                  <Check className="w-4 h-4" />
                  ALL PRESENT
                </button>
                <button
                  type="button"
                  onClick={() => setIsResetConfirmOpen(true)}
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold transition-all"
                >
                  <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
                  Clear Selections
                </button>
              </div>
            </div>
          </div>

          {/* Step 8 Incomplete Warning Alert */}
          {incompleteWarning && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold text-rose-900">Cannot Submit Attendance</h4>
                <p className="text-xs text-rose-700 mt-1 leading-relaxed">{incompleteWarning}</p>
              </div>
            </div>
          )}

          {/* Step 2 & 3: Students Attendance Marking Table */}
          <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs overflow-hidden">
            <div className="px-5 py-4 border-b border-slate-200/80 bg-slate-50/70 flex items-center justify-between">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Enrolled Students ({sheet.students.length})
              </span>
              <span className="text-xs text-slate-500 font-medium">
                Tap status buttons or use ALL PRESENT
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-600">
                <thead className="bg-slate-50/50 text-xs font-semibold uppercase text-slate-500 border-b border-slate-200">
                  <tr>
                    <th className="py-3 px-4 w-28">Roll No</th>
                    <th className="py-3 px-4">Student Name</th>
                    <th className="py-3 px-4 text-center w-72">Attendance Status</th>
                    <th className="py-3 px-4">Remarks (Optional)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {sheet.students.map((st) => {
                    const curr = studentStatuses[st.student_id];
                    return (
                      <tr
                        key={st.student_id}
                        className={`hover:bg-slate-50/50 transition-colors ${
                          curr === 'ABSENT'
                            ? 'bg-rose-50/30'
                            : curr === 'PRESENT'
                            ? 'bg-emerald-50/20'
                            : curr === 'HALF_DAY'
                            ? 'bg-amber-50/20'
                            : 'bg-white'
                        }`}
                      >
                        <td className="py-3.5 px-4 font-bold text-slate-900 whitespace-nowrap">
                          {st.roll_number}
                        </td>
                        <td className="py-3.5 px-4 font-medium text-slate-900">
                          {st.full_name}
                          <span className="block text-[11px] font-normal text-slate-400">
                            {st.student_identifier}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-center">
                          <div className="inline-flex rounded-xl p-1 bg-slate-100 border border-slate-200/80 gap-1">
                            <button
                              type="button"
                              onClick={() => handleSetStudentStatus(st.student_id, 'PRESENT')}
                              className={`px-3 py-1.5 text-xs font-bold rounded-lg transition-all flex items-center gap-1 ${
                                curr === 'PRESENT'
                                  ? 'bg-emerald-600 text-white shadow-xs'
                                  : 'text-slate-600 hover:text-emerald-700 hover:bg-emerald-50'
                              }`}
                            >
                              <Check className="w-3.5 h-3.5" />
                              P
                            </button>
                            <button
                              type="button"
                              onClick={() => handleSetStudentStatus(st.student_id, 'ABSENT')}
                              className={`px-3 py-1.5 text-xs font-bold rounded-lg transition-all flex items-center gap-1 ${
                                curr === 'ABSENT'
                                  ? 'bg-rose-600 text-white shadow-xs'
                                  : 'text-slate-600 hover:text-rose-700 hover:bg-rose-50'
                              }`}
                            >
                              <X className="w-3.5 h-3.5" />
                              A
                            </button>
                            <button
                              type="button"
                              onClick={() => handleSetStudentStatus(st.student_id, 'HALF_DAY')}
                              className={`px-2.5 py-1.5 text-xs font-bold rounded-lg transition-all ${
                                curr === 'HALF_DAY'
                                  ? 'bg-amber-500 text-white shadow-xs'
                                  : 'text-slate-600 hover:text-amber-700 hover:bg-amber-50'
                              }`}
                            >
                              HD
                            </button>
                          </div>
                        </td>
                        <td className="py-3.5 px-4">
                          <input
                            type="text"
                            placeholder="Optional note"
                            value={studentRemarks[st.student_id] || ''}
                            onChange={(e) => {
                              setStudentRemarks({ ...studentRemarks, [st.student_id]: e.target.value });
                              setHasUnsavedChanges(true);
                            }}
                            className="w-full text-xs border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-800 bg-white focus:ring-1 focus:ring-indigo-500"
                          />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Step 7: Distinct Absent Student Review List */}
          <div className="bg-white p-5 rounded-2xl border border-rose-200/80 shadow-2xs">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-rose-600" />
                <h3 className="text-sm font-bold text-slate-900">
                  Step 7: Absent Student Review List ({absentList.length})
                </h3>
              </div>
              <span className="text-xs text-slate-500">
                Carefully verify absentees before final commit
              </span>
            </div>

            {absentList.length === 0 ? (
              <p className="text-xs text-slate-500 italic py-2">
                No students currently marked absent.
              </p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5 pt-2">
                {absentList.map((st) => (
                  <div
                    key={st.student_id}
                    className="flex items-center justify-between p-3 rounded-xl border border-rose-200 bg-rose-50/50"
                  >
                    <div>
                      <span className="text-xs font-bold text-rose-900 block">{st.full_name}</span>
                      <span className="text-[11px] text-rose-600 font-semibold">{st.roll_number}</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleSetStudentStatus(st.student_id, 'PRESENT')}
                      className="text-[11px] font-bold px-2 py-1 bg-white hover:bg-emerald-50 text-emerald-700 rounded-lg border border-emerald-200 shadow-2xs transition-colors"
                    >
                      Make Present
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Step 10: Submission Footer Bar */}
          <div className="sticky bottom-4 z-20 bg-slate-900 text-white p-4 rounded-2xl shadow-xl flex items-center justify-between">
            <div>
              <span className="text-xs text-slate-400 block">Attendance Ready to Submit</span>
              <span className="text-sm font-bold text-white">
                {presentStudents} Present, {absentStudents} Absent, {halfDayStudents} Half-Day
              </span>
            </div>
            <button
              type="button"
              onClick={handlePreSubmitCheck}
              disabled={isSubmitting}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-500 hover:bg-indigo-600 text-white text-sm font-bold shadow-md transition-all disabled:opacity-50"
            >
              <FileCheck2 className="w-4 h-4" />
              SUBMIT ATTENDANCE
            </button>
          </div>
        </>
      )}

      {/* Confirmation Dialogs */}
      <ConfirmDialog
        isOpen={isResetConfirmOpen}
        onClose={() => setIsResetConfirmOpen(false)}
        onConfirm={handleResetConfirm}
        title="Reset All Selections?"
        message="This will clear all present and absent markers for currently displayed students. Are you sure?"
        confirmLabel="Yes, Clear All"
        variant="warning"
      />

      <ConfirmDialog
        isOpen={isConfirmSubmitOpen}
        onClose={() => setIsConfirmSubmitOpen(false)}
        onConfirm={handleFinalSubmit}
        isLoading={isSubmitting}
        title="Submit Official Attendance?"
        message={`Are you sure you want to finalize attendance? This will record ${presentStudents} Present and ${absentStudents} Absent students in the database and recalculate student percentages.`}
        confirmLabel="Confirm & Submit"
        variant="primary"
      />
    </div>
  );
};
