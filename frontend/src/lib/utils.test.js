/**
 * Unit tests for lib/utils (Layer 2 – Unit tests).
 */
import { cn } from './utils';

describe('cn (classnames utility)', () => {
  it('returns empty string for no args', () => {
    expect(cn()).toBe('');
  });

  it('merges single class', () => {
    expect(cn('foo')).toBe('foo');
  });

  it('merges multiple classes', () => {
    expect(cn('foo', 'bar')).toContain('foo');
    expect(cn('foo', 'bar')).toContain('bar');
  });

  it('handles conditional classes', () => {
    expect(cn('base', false && 'hidden', true && 'visible')).toContain('base');
    expect(cn('base', false && 'hidden', true && 'visible')).toContain('visible');
    expect(cn('base', false && 'hidden')).not.toContain('hidden');
  });

  it('tailwind-merge overrides conflicting classes', () => {
    const result = cn('p-4', 'p-2');
    expect(result).toBe('p-2');
  });
});
