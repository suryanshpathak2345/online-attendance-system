import React from 'react';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon } from 'lucide-react';
import {
  format,
  addMonths,
  subMonths,
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  isSameMonth,
  isSameDay,
  addDays,
} from 'date-fns';
import { Badge } from '../common/Badge';

export interface CalendarEvent {
  date: string; // YYYY-MM-DD
  status: 'PRESENT' | 'ABSENT' | 'HALF_DAY' | 'HOLIDAY' | 'CANCELLED' | 'SCHEDULED' | 'CONDUCTED' | 'NOT_RECORDED';
  title?: string;
  subtitle?: string;
  sessionId?: number;
}

interface MonthCalendarProps {
  currentMonth: Date;
  onMonthChange: (date: Date) => void;
  events?: CalendarEvent[];
  selectedDate?: Date | null;
  onSelectDate?: (date: Date, event?: CalendarEvent) => void;
  mode?: 'teacher' | 'student';
}

export const MonthCalendar: React.FC<MonthCalendarProps> = ({
  currentMonth,
  onMonthChange,
  events = [],
  selectedDate,
  onSelectDate,
  mode = 'teacher',
}) => {
  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(monthStart);
  const startDate = startOfWeek(monthStart);
  const endDate = endOfWeek(monthEnd);

  const prevMonth = () => onMonthChange(subMonths(currentMonth, 1));
  const nextMonth = () => onMonthChange(addMonths(currentMonth, 1));
  const goToToday = () => onMonthChange(new Date());

  const eventMap = new Map<string, CalendarEvent>();
  events.forEach((ev) => eventMap.set(ev.date, ev));

  const renderDaysHeader = () => {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    return (
      <div className="grid grid-cols-7 border-b border-slate-200 bg-slate-50/70 text-center py-2.5 text-xs font-semibold text-slate-500 uppercase tracking-wider">
        {days.map((d, i) => (
          <div key={i}>{d}</div>
        ))}
      </div>
    );
  };

  const renderCells = () => {
    const rows = [];
    let days = [];
    let day = startDate;

    while (day <= endDate) {
      for (let i = 0; i < 7; i++) {
        const cloneDay = day;
        const dateKey = format(cloneDay, 'yyyy-MM-dd');
        const ev = eventMap.get(dateKey);
        const isCurrentMonth = isSameMonth(cloneDay, monthStart);
        const isToday = isSameDay(cloneDay, new Date());
        const isSelected = selectedDate ? isSameDay(cloneDay, selectedDate) : false;

        days.push(
          <div
            key={dateKey}
            onClick={() => onSelectDate && onSelectDate(cloneDay, ev)}
            className={`min-h-[75px] md:min-h-[90px] p-2 border-b border-r border-slate-100 transition-colors flex flex-col justify-between cursor-pointer relative ${
              !isCurrentMonth ? 'bg-slate-50/40 text-slate-400' : 'bg-white hover:bg-indigo-50/30'
            } ${isSelected ? 'ring-2 ring-indigo-600 ring-inset bg-indigo-50/40' : ''}`}
          >
            <div className="flex items-center justify-between">
              <span
                className={`text-xs font-medium w-6 h-6 flex items-center justify-center rounded-full ${
                  isToday
                    ? 'bg-indigo-600 text-white font-bold'
                    : isSelected
                    ? 'font-bold text-indigo-700'
                    : 'text-slate-700'
                }`}
              >
                {format(cloneDay, 'd')}
              </span>
            </div>

            {/* Event status badges */}
            {ev && (
              <div className="mt-1">
                {ev.status === 'PRESENT' && (
                  <Badge variant="present" size="sm" className="w-full text-[10px] truncate">
                    Present
                  </Badge>
                )}
                {ev.status === 'ABSENT' && (
                  <Badge variant="absent" size="sm" className="w-full text-[10px] truncate">
                    Absent
                  </Badge>
                )}
                {ev.status === 'HALF_DAY' && (
                  <Badge variant="halfday" size="sm" className="w-full text-[10px] truncate">
                    Half-Day
                  </Badge>
                )}
                {ev.status === 'HOLIDAY' && (
                  <Badge variant="holiday" size="sm" className="w-full text-[10px] truncate">
                    {ev.title || 'Holiday'}
                  </Badge>
                )}
                {ev.status === 'CANCELLED' && (
                  <Badge variant="cancelled" size="sm" className="w-full text-[10px] truncate">
                    Cancelled
                  </Badge>
                )}
                {ev.status === 'CONDUCTED' && (
                  <Badge variant="success" size="sm" className="w-full text-[10px] truncate">
                    Conducted
                  </Badge>
                )}
                {ev.status === 'SCHEDULED' && (
                  <Badge variant="primary" size="sm" className="w-full text-[10px] truncate">
                    Scheduled
                  </Badge>
                )}
              </div>
            )}
          </div>
        );
        day = addDays(day, 1);
      }
      rows.push(
        <div key={day.toISOString()} className="grid grid-cols-7">
          {days}
        </div>
      );
      days = [];
    }
    return <div className="border-l border-t border-slate-200 rounded-b-xl overflow-hidden">{rows}</div>;
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden">
      {/* Calendar Header Controls */}
      <div className="flex flex-wrap items-center justify-between p-4 md:px-6 border-b border-slate-200 gap-3">
        <div className="flex items-center gap-2">
          <CalendarIcon className="w-5 h-5 text-indigo-600" />
          <h2 className="text-base font-semibold text-slate-900">
            {format(currentMonth, 'MMMM yyyy')}
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={goToToday}
            className="px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors shadow-2xs"
          >
            Today
          </button>
          <div className="flex items-center rounded-lg border border-slate-200 bg-white shadow-2xs overflow-hidden">
            <button
              type="button"
              onClick={prevMonth}
              className="p-1.5 hover:bg-slate-50 text-slate-600 transition-colors"
              aria-label="Previous month"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <div className="h-4 w-px bg-slate-200" />
            <button
              type="button"
              onClick={nextMonth}
              className="p-1.5 hover:bg-slate-50 text-slate-600 transition-colors"
              aria-label="Next month"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Weekdays and Grid */}
      {renderDaysHeader()}
      {renderCells()}
    </div>
  );
};
