import React from 'react';
import { Link } from 'react-router-dom';
import { Menu, LogOut, CheckSquare } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Badge } from '../common/Badge';

interface NavbarProps {
  onToggleSidebar?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleSidebar }) => {
  const { user, logout, role } = useAuth();

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-4 md:px-6 bg-white border-b border-slate-200/80 shadow-2xs">
      <div className="flex items-center gap-3">
        {onToggleSidebar && (
          <button
            onClick={onToggleSidebar}
            className="p-2 rounded-lg text-slate-500 hover:text-slate-700 hover:bg-slate-100 md:hidden transition-colors"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-brand-500 flex items-center justify-center text-white shadow-sm font-bold">
            <CheckSquare className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-slate-900 tracking-tight leading-none">
              AttendEase
            </h1>
            <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">
              Management Portal
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3 md:gap-4">
        {user ? (
          <>
            <div className="hidden sm:flex flex-col text-right">
              <span className="text-sm font-semibold text-slate-900 leading-tight">
                {user.full_name}
              </span>
              <div className="flex items-center justify-end gap-1.5 mt-0.5">
                <Badge
                  variant={role === 'admin' ? 'danger' : role === 'teacher' ? 'primary' : 'success'}
                  size="sm"
                >
                  {role?.toUpperCase()}
                </Badge>
              </div>
            </div>
            <button
              onClick={logout}
              title="Logout"
              className="flex items-center gap-2 p-2 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 transition-colors text-sm font-medium"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden md:inline">Sign Out</span>
            </button>
          </>
        ) : (
          <div className="flex items-center gap-2">
            <a
              href="/login"
              className="text-sm font-medium text-slate-700 hover:text-indigo-600 px-3 py-1.5"
            >
              Sign In
            </a>
          </div>
        )}
      </div>
    </header>
  );
};
