import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  CheckSquare,
  Users,
  BookOpen,
  CalendarDays,
  FileSpreadsheet,
  BarChart3,
  History,
  GraduationCap,
  Sparkles,
  User,
  ShieldCheck,
  type LucideIcon,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface SidebarProps {
  isOpen: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const { role, user } = useAuth();

  const teacherNavItems: Array<{ label: string; path: string; icon: LucideIcon; tag?: string }> = [
    { label: 'Dashboard', path: '/teacher/dashboard', icon: LayoutDashboard },
    { label: 'Mark Attendance', path: '/teacher/mark-attendance', icon: CheckSquare },
    { label: 'Attendance History', path: '/teacher/history', icon: History },
    { label: 'Class Calendar', path: '/teacher/calendar', icon: CalendarDays },
    { label: 'Reports & Analytics', path: '/teacher/reports', icon: BarChart3 },
    { label: 'Excel Register Export', path: '/teacher/export', icon: FileSpreadsheet },
    { label: 'Classes & Sections', path: '/teacher/classes', icon: GraduationCap },
    { label: 'Students Directory', path: '/teacher/students', icon: Users },
    { label: 'Course Subjects', path: '/teacher/subjects', icon: BookOpen },
    { label: 'Profile', path: '/teacher/profile', icon: User },
  ];

  const studentNavItems: Array<{ label: string; path: string; icon: LucideIcon; tag?: string }> = [
    { label: 'My Dashboard', path: '/student/dashboard', icon: LayoutDashboard },
    { label: 'Subject Attendance', path: '/student/subjects', icon: BookOpen },
    { label: 'Monthly Calendar', path: '/student/calendar', icon: CalendarDays },
    { label: 'Personal Tracker', path: '/student/personal-tracker', icon: Sparkles, tag: 'Private' },
  ];

  const navItems = role === 'student' ? studentNavItems : teacherNavItems;

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-xs md:hidden"
        />
      )}

      {/* Sidebar Panel */}
      <aside
        className={`fixed md:sticky top-16 left-0 z-40 h-[calc(100vh-4rem)] w-64 bg-white border-r border-slate-200/80 transition-transform duration-200 ease-in-out md:translate-x-0 overflow-y-auto ${
          isOpen ? 'translate-x-0 shadow-xl' : '-translate-x-full'
        }`}
      >
        <div className="p-4">
          <div className="mb-4 px-3 py-2 bg-slate-50 rounded-xl border border-slate-200/60">
            <span className="text-[10px] font-semibold tracking-wider uppercase text-slate-400 block">
              Logged in Mode
            </span>
            <div className="flex items-center justify-between mt-1">
              <span className="text-xs font-bold text-slate-800">
                {role === 'student' ? 'Official Student View' : role === 'admin' ? 'Administrator' : 'Teacher Portal'}
              </span>
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
            </div>
          </div>

          <nav className="space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-indigo-600 text-white shadow-xs font-semibold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <item.icon className="w-4 h-4 flex-shrink-0" />
                  <span>{item.label}</span>
                </div>
                {item.tag && (
                  <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded-md bg-amber-100 text-amber-800">
                    {item.tag}
                  </span>
                )}
              </NavLink>
            ))}
          </nav>
        </div>
      </aside>
    </>
  );
};
