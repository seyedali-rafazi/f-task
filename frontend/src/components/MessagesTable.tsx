import type { ReactNode } from 'react';
import type { Message } from '../types';
import { businessMinutesLeft } from '../sla';
import { formatCategory, formatDate } from '../format';

const MAX_ROWS = 200;
const ORDER_RE = /(BZ-[0-9۰-۹٠-٩]+)/gi;

function renderHighlightedBody(text: string): ReactNode {
  const parts = text.split(ORDER_RE);
  return parts.map((part, idx) =>
    idx % 2 === 1 ? (
      <mark key={idx} className="order-ref ltr">
        {part}
      </mark>
    ) : (
      part
    ),
  );
}

interface Props {
  messages: Message[];
  nowMs: number;
}

export default function MessagesTable({ messages, nowMs }: Props) {
  const rows = messages.slice(0, MAX_ROWS);
  return (
    <section className="card">
      <h2>همه پیام‌ها ({messages.length.toLocaleString('fa-IR')})</h2>
      {messages.length > MAX_ROWS && (
        <p className="muted">
          نمایش {MAX_ROWS.toLocaleString('fa-IR')} پیام اول از {messages.length.toLocaleString('fa-IR')} پیام.
        </p>
      )}
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>شناسه</th>
              <th>دسته‌بندی</th>
              <th>فوری</th>
              <th>شماره سفارش</th>
              <th>کانال</th>
              <th>زمان دریافت</th>
              <th>عنوان</th>
              <th>متن پیام</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((m) => {
              const sev = (m.severity ?? m.severity_hint ?? '').toLowerCase();
              const isAnswered = Boolean(m.answered_at && Date.parse(m.answered_at) <= nowMs);
              const isUrgentNow =
                m.duplicate_of === null &&
                sev === 'high' &&
                !isAnswered &&
                businessMinutesLeft(m.received_at, nowMs) <= 0;
              return (
                <tr key={m.message_id}>
                  <td className="ltr">{m.message_id}</td>
                  <td>{formatCategory(m.category)}</td>
                  <td>
                    {isUrgentNow ? <span className="badge badge-urgent">بله</span> : ''}
                  </td>
                  <td className="ltr">{m.order_ref ?? '-'}</td>
                  <td className="ltr">{m.channel}</td>
                  <td>{formatDate(m.received_at)}</td>
                  <td dir="auto">{m.subject}</td>
                  <td dir="auto" className="body-cell">
                    {renderHighlightedBody(m.body)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
