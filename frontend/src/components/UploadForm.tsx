import { useState, type FormEvent } from 'react';

interface Props {
  onSubmit: (file: File, now?: string) => void;
  loading: boolean;
}

export default function UploadForm({ onSubmit, loading }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [now, setNow] = useState('');

  function submit(e: FormEvent) {
    e.preventDefault();
    if (!file) return;
    // datetime-local has no zone; treat the entered value as UTC
    onSubmit(file, now ? `${now}:00Z` : undefined);
  }

  return (
    <form className="card upload" onSubmit={submit}>
      <label>
        فایل CSV پیام‌ها
        <input
          data-testid="upload-input"
          type="file"
          accept=".csv,text/csv"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
      </label>
      <label>
        زمان مرجع دستی (UTC، اختیاری)
        <input
          type="datetime-local"
          dir="ltr"
          value={now}
          onChange={(e) => setNow(e.target.value)}
        />
      </label>
      <button type="submit" data-testid="analyze-button" disabled={!file || loading}>
        {loading ? 'در حال تحلیل...' : 'تحلیل پیام‌ها'}
      </button>
    </form>
  );
}
