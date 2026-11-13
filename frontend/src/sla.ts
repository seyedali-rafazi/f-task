/**
 * Iranian support business-hours calculation in Asia/Tehran.
 * Working days: Saturday (6) through Wednesday (3).
 * Off days: Thursday (4), Friday (5), and 1405 official public holidays.
 * Working hours: 09:00 - 17:00 Asia/Tehran.
 */

// 1405 official public holidays converted to Gregorian YYYY-MM-DD
const PUBLIC_HOLIDAYS = new Set<string>([
  '2026-03-21', // 1405/01/01
  '2026-03-22', // 1405/01/02
  '2026-03-23', // 1405/01/03
  '2026-03-24', // 1405/01/04
  '2026-04-01', // 1405/01/12
  '2026-04-02', // 1405/01/13
  '2026-04-14', // 1405/01/25
  '2026-05-28', // 1405/03/07
  '2026-06-04', // 1405/03/14
  '2026-06-05', // 1405/03/15
  '2026-06-26', // 1405/04/05
  '2026-06-27', // 1405/04/06
  '2026-08-06', // 1405/05/15
  '2026-08-14', // 1405/05/23
  '2026-08-16', // 1405/05/25
  '2026-08-23', // 1405/06/01
  '2026-09-01', // 1405/06/10
  '2026-11-15', // 1405/08/24
  '2026-12-24', // 1405/10/03
  '2027-01-07', // 1405/10/17
  '2027-01-25', // 1405/11/05
  '2027-02-11', // 1405/11/22
  '2027-03-01', // 1405/12/10
  '2027-03-11', // 1405/12/20
  '2027-03-12', // 1405/12/21
  '2027-03-20', // 1405/12/29
]);

const TEHRAN_FMT = new Intl.DateTimeFormat('en-CA', {
  timeZone: 'Asia/Tehran',
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
  hour12: false,
});

interface TehranWall {
  dateStr: string; // YYYY-MM-DD
  dayMs: number; // UTC midnight of that Gregorian date
  secondsOfDay: number;
}

function toTehranWall(utcMs: number): TehranWall {
  const parts = TEHRAN_FMT.formatToParts(new Date(utcMs));
  const get = (t: string) => parts.find((p) => p.type === t)?.value ?? '00';
  const y = Number(get('year'));
  const m = Number(get('month'));
  const d = Number(get('day'));
  const hh = Number(get('hour')) % 24;
  const mm = Number(get('minute'));
  const ss = Number(get('second'));
  const dateStr = `${String(y).padStart(4, '0')}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
  return {
    dateStr,
    dayMs: Date.UTC(y, m - 1, d),
    secondsOfDay: hh * 3600 + mm * 60 + ss,
  };
}

function isBusinessDate(dayUtcMs: number): boolean {
  const d = new Date(dayUtcMs);
  const wd = d.getUTCDay(); // 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
  if (wd === 4 || wd === 5) return false;
  const dateStr = d.toISOString().slice(0, 10);
  return !PUBLIC_HOLIDAYS.has(dateStr);
}

const START_SEC = 9 * 3600;
const END_SEC = 17 * 3600;
const DAY_MS = 86400 * 1000;

export function businessMinutesBetween(startUtcMs: number, endUtcMs: number): number {
  if (endUtcMs <= startUtcMs || Number.isNaN(startUtcMs) || Number.isNaN(endUtcMs)) {
    return 0;
  }
  const s = toTehranWall(startUtcMs);
  const e = toTehranWall(endUtcMs);

  let totalSec = 0;
  for (let dayMs = s.dayMs; dayMs <= e.dayMs; dayMs += DAY_MS) {
    if (!isBusinessDate(dayMs)) continue;
    const lo = dayMs === s.dayMs ? Math.max(START_SEC, s.secondsOfDay) : START_SEC;
    const hi = dayMs === e.dayMs ? Math.min(END_SEC, e.secondsOfDay) : END_SEC;
    if (hi > lo) {
      totalSec += hi - lo;
    }
  }
  return totalSec / 60;
}

export function businessMinutesLeft(receivedAtIso: string, nowMs: number, slaMinutes = 120): number {
  const receivedMs = Date.parse(receivedAtIso);
  if (Number.isNaN(receivedMs)) return slaMinutes;
  const elapsed = businessMinutesBetween(receivedMs, nowMs);
  return Math.round(slaMinutes - elapsed);
}
