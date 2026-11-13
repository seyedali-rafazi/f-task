import { useEffect, useMemo, useState } from 'react';
import { analyze } from './api';
import { businessMinutesLeft } from './sla';
import type { AnalyzeResult, Message } from './types';
import UploadForm from './components/UploadForm';
import SummaryTiles from './components/SummaryTiles';
import CategoryBreakdown from './components/CategoryBreakdown';
import AttentionList, { type AttentionItem } from './components/AttentionList';
import MessagesTable from './components/MessagesTable';

export default function App() {
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nowOverrideMs, setNowOverrideMs] = useState<number | null>(null);
  const [clockMs, setClockMs] = useState<number>(() => Date.now());

  useEffect(() => {
    const id = window.setInterval(() => {
      setClockMs(Date.now());
    }, 30_000);
    return () => window.clearInterval(id);
  }, []);

  async function handleSubmit(file: File, now?: string) {
    setLoading(true);
    setError(null);
    const parsedOverride = now ? Date.parse(now) : NaN;
    const overrideMs = Number.isNaN(parsedOverride) ? null : parsedOverride;
    setNowOverrideMs(overrideMs);
    setClockMs(Date.now());
    try {
      setResult(await analyze(file, now));
    } catch (e) {
      setResult(null);
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  const effectiveNowMs = nowOverrideMs ?? clockMs;

  const attentionItems: AttentionItem[] = useMemo(() => {
    if (!result) return [];
    const items: AttentionItem[] = [];
    for (const m of result.messages) {
      if (m.duplicate_of !== null) continue;
      const sev = (m.severity ?? m.severity_hint ?? '').toLowerCase();
      if (sev !== 'high') continue;
      if (m.answered_at) {
        const ansMs = Date.parse(m.answered_at);
        if (!Number.isNaN(ansMs) && ansMs <= effectiveNowMs) continue;
      }
      const left = businessMinutesLeft(m.received_at, effectiveNowMs);
      items.push({ message: m, left });
    }
    items.sort((a, b) => {
      if (a.left !== b.left) return a.left - b.left;
      return Date.parse(a.message.received_at) - Date.parse(b.message.received_at);
    });
    return items;
  }, [result, effectiveNowMs]);

  const urgentCount = useMemo(
    () => attentionItems.filter((item) => item.left <= 0).length,
    [attentionItems],
  );

  return (
    <main className="container">
      <h1>داشبورد پشتیبانی بازارچه</h1>
      <p className="muted">
        فایل خروجی پیام‌های پشتیبانی را بارگذاری کنید تا وضعیت دسته‌بندی‌ها و پیام‌های نیازمند توجه را ببینید.
      </p>
      <UploadForm onSubmit={handleSubmit} loading={loading} />
      {error && <p className="error">{error}</p>}
      {result && (
        <>
          <SummaryTiles total={result.total_unique_messages} urgent={urgentCount} />
          <CategoryBreakdown counts={result.category_counts} total={result.total_unique_messages} />
          <AttentionList items={attentionItems} />
          <MessagesTable messages={result.messages} nowMs={effectiveNowMs} />
        </>
      )}
    </main>
  );
}
