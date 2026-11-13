interface Props {
  total: number;
  urgent: number;
}

export default function SummaryTiles({ total, urgent }: Props) {
  return (
    <section className="tiles">
      <div className="card tile">
        <div className="tile-label">پیام‌های یکتا</div>
        <div className="tile-value" data-testid="total">{total.toLocaleString('fa-IR')}</div>
      </div>
      <div className="card tile urgent" data-testid="urgent-count">
        <div className="tile-label">فوری (عبور از مهلت ۲ ساعته)</div>
        <div className="tile-value" data-testid="urgent">{urgent.toLocaleString('fa-IR')}</div>
      </div>
    </section>
  );
}
