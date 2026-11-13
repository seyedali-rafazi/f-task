import { businessMinutesBetween, businessMinutesLeft } from './sla';

describe('frontend SLA business hours (Asia/Tehran)', () => {
  it('skips Thursday and Friday', () => {
    // Wed 2026-10-21 16:00 Tehran (12:30Z) -> Sat 2026-10-24 10:00 Tehran (06:30Z) = 120 min
    const start = Date.parse('2026-10-21T12:30:00Z');
    const end = Date.parse('2026-10-24T06:30:00Z');
    expect(businessMinutesBetween(start, end)).toBe(120);
    expect(businessMinutesLeft('2026-10-21T12:30:00Z', end)).toBe(0);
  });

  it('skips 1405 public holidays (1405/01/25 = 2026-04-14)', () => {
    // Mon 2026-04-13 16:00 Tehran (12:30Z) -> Wed 2026-04-15 10:00 Tehran (06:30Z) = 120 min
    const start = Date.parse('2026-04-13T12:30:00Z');
    const end = Date.parse('2026-04-15T06:30:00Z');
    expect(businessMinutesBetween(start, end)).toBe(120);
    expect(businessMinutesLeft('2026-04-13T12:30:00Z', end)).toBe(0);
  });
});
