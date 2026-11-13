import { useState } from 'react';
import type { Message } from '../types';
import { requestDraft } from '../api';
import { formatDate } from '../format';

export interface AttentionItem {
  message: Message;
  left: number;
}

interface Props {
  items: AttentionItem[];
}

interface DraftState {
  text: string;
  blocked: boolean;
  warnings: string[];
  error?: string;
}

function describeMinutesLeft(minutes: number): string {
  const abs = Math.abs(minutes);
  const h = Math.floor(abs / 60);
  const m = abs % 60;
  const parts: string[] = [];
  if (h > 0) parts.push(`${h} ساعت`);
  if (m > 0 || h === 0) parts.push(`${m} دقیقه`);
  const duration = parts.join(' و ');
  if (minutes <= 0) {
    return minutes === 0 ? 'مهلت به پایان رسیده (فوری)' : `${duration} تاخیر (فوری)`;
  }
  return `${duration} باقی‌مانده`;
}

export default function AttentionList({ items }: Props) {
  const [drafts, setDrafts] = useState<Record<string, DraftState>>({});
  const [busy, setBusy] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  async function onDraft(m: Message) {
    setBusy(m.message_id);
    setCopiedId(null);
    try {
      const d = await requestDraft({
        message_id: m.message_id,
        customer_id: m.customer_id,
        subject: m.subject,
        body: m.body,
      });
      setDrafts((prev) => ({
        ...prev,
        [m.message_id]: {
          text: d.draft ?? '',
          blocked: Boolean(d.blocked),
          warnings: Array.isArray(d.warnings) ? d.warnings : [],
        },
      }));
    } catch (e) {
      setDrafts((prev) => ({
        ...prev,
        [m.message_id]: {
          text: '',
          blocked: true,
          warnings: [e instanceof Error ? e.message : 'خطا در دریافت پیش‌نویس پاسخ'],
        },
      }));
    } finally {
      setBusy(null);
    }
  }

  async function onApprove(messageId: string, text: string) {
    try {
      await navigator.clipboard?.writeText(text);
    } catch {
      // Clipboard may be unavailable in headless/test environments
    }
    setCopiedId(messageId);
  }

  return (
    <section className="card">
      <h2>نیازمند توجه ({items.length.toLocaleString('fa-IR')})</h2>
      {items.length === 0 ? (
        <p className="muted">هیچ پیام نیازمند توجهی وجود ندارد.</p>
      ) : (
        <ul className="attention-list">
          {items.map(({ message: m, left }) => {
            const draftState = drafts[m.message_id];
            const isOverdue = left <= 0;
            return (
              <li
                key={m.message_id}
                data-testid="attention-row"
                data-message-id={m.message_id}
                data-business-minutes-left={left}
              >
                <div className="attention-header">
                  <code className="ltr">{m.message_id}</code>
                  {m.order_ref && <mark className="order-ref ltr">{m.order_ref}</mark>}
                  <span className={`badge ${isOverdue ? 'badge-overdue' : 'badge-soon'}`}>
                    {describeMinutesLeft(left)}
                  </span>
                  <strong dir="auto">{m.subject || '(بدون عنوان)'}</strong>
                </div>
                <div className="attention-meta">
                  دریافت: {formatDate(m.received_at)} | کانال: <span className="ltr">{m.channel}</span>
                </div>
                <p dir="auto" style={{ margin: '4px 0 8px' }}>{m.body}</p>
                <button
                  type="button"
                  data-testid="draft-button"
                  disabled={busy === m.message_id}
                  onClick={() => onDraft(m)}
                >
                  {busy === m.message_id ? 'در حال نگارش پیش‌نویس...' : 'پیش‌نویس پاسخ'}
                </button>

                {draftState && (
                  <div className="draft-area">
                    {(draftState.blocked || draftState.warnings.length > 0) && (
                      <div className="draft-warning" data-testid="draft-warning">
                        {draftState.warnings.length > 0
                          ? draftState.warnings.join(' — ')
                          : 'امکان تولید پیش‌نویس امن برای این پیام وجود ندارد.'}
                      </div>
                    )}
                    {!draftState.blocked && (
                      <>
                        <textarea
                          className="draft-textarea"
                          data-testid="draft-text"
                          dir="auto"
                          value={draftState.text}
                          onChange={(e) => {
                            const val = e.target.value;
                            setDrafts((prev) => ({
                              ...prev,
                              [m.message_id]: { ...draftState, text: val },
                            }));
                          }}
                        />
                        <div className="draft-actions">
                          <button
                            type="button"
                            className="approve"
                            data-testid="draft-approve"
                            onClick={() => onApprove(m.message_id, draftState.text)}
                          >
                            تایید و کپی پاسخ
                          </button>
                          {copiedId === m.message_id && (
                            <span className="copied-note">متن نهایی کپی شد.</span>
                          )}
                        </div>
                      </>
                    )}
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
