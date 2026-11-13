import { CATEGORIES, type Category } from '../types';
import { formatCategory, formatPercent } from '../format';

interface Props {
  counts: Record<Category, number>;
  total: number;
}

export default function CategoryBreakdown({ counts, total }: Props) {
  return (
    <section className="card">
      <h2>تفکیک دسته‌بندی‌ها</h2>
      <ul className="breakdown">
        {CATEGORIES.map((cat) => {
          const count = counts[cat] ?? 0;
          const pct = formatPercent(count, total);
          return (
            <li key={cat}>
              <span className="cat-name">{formatCategory(cat)}</span>
              <span className="bar">
                <span className="bar-fill" style={{ width: pct }} />
              </span>
              <span className="cat-count">{count.toLocaleString('fa-IR')}</span>
              <span className="cat-pct">{pct}</span>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
