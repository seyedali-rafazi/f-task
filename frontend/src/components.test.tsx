import { render, screen } from '@testing-library/react';
import SummaryTiles from './components/SummaryTiles';
import CategoryBreakdown from './components/CategoryBreakdown';

describe('SummaryTiles', () => {
  it('shows totals', () => {
    render(<SummaryTiles total={1200} urgent={7} />);
    expect(screen.getByTestId('urgent')).toHaveTextContent(/7|۷/);
  });
});

describe('CategoryBreakdown', () => {
  it('renders all six categories when all are present', () => {
    const counts = { delivery: 4, payment: 2, refund: 1, product_quality: 1, account: 1, other: 1 };
    render(<CategoryBreakdown counts={counts} total={10} />);
    expect(screen.getAllByRole('listitem')).toHaveLength(6);
    expect(screen.getByText('40.0%')).toBeInTheDocument();
  });
});
