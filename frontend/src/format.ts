const CATEGORY_LABELS_FA: Record<string, string> = {
  delivery: 'ارسال و تحویل',
  payment: 'پرداخت',
  refund: 'بازگشت وجه و مرجوعی',
  product_quality: 'کیفیت و مشخصات کالا',
  account: 'حساب کاربری',
  other: 'سایر',
};

export function formatPercent(part: number, total: number): string {
  if (!total) return '0.0%';
  return `${((part / total) * 100).toFixed(1)}%`;
}

export function formatCategory(cat: string): string {
  return CATEGORY_LABELS_FA[cat] ?? cat.replace(/_/g, ' ');
}

export function formatDate(iso: string | null): string {
  if (!iso) return '-';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return new Intl.DateTimeFormat('fa-IR', {
    timeZone: 'Asia/Tehran',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(d);
}
