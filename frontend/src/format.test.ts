import { formatPercent, formatCategory, formatDate } from './format';

describe('format helpers', () => {
  it('formats percentages', () => {
    expect(formatPercent(1, 4)).toBe('25.0%');
    expect(formatPercent(0, 0)).toBe('0.0%');
  });
  it('formats category labels in Persian', () => {
    expect(formatCategory('product_quality')).toBe('کیفیت و مشخصات کالا');
    expect(formatCategory('delivery')).toBe('ارسال و تحویل');
  });
  it('formats dates in Persian Tehran time', () => {
    expect(formatDate('2024-03-01T10:15:00Z')).toContain('۱۳:۴۵');
    expect(formatDate(null)).toBe('-');
  });
});
