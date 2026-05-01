/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,jsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      colors: {
        background:        'var(--background)',
        surface:           'var(--surface)',
        'surface-2':       'var(--surface-2)',
        border:            'var(--border)',
        'border-strong':   'var(--border-strong)',
        'text-primary':    'var(--text-primary)',
        'text-secondary':  'var(--text-secondary)',
        'text-muted':      'var(--text-muted)',
        accent:            'var(--accent)',
        'accent-fg':       'var(--accent-foreground)',
        'sev-low':         'var(--severity-low)',
        'sev-medium':      'var(--severity-medium)',
        'sev-high':        'var(--severity-high)',
        'sev-critical':    'var(--severity-critical)',
      },
      fontSize: {
        display: ['2.25rem',    { lineHeight: '2.75rem',  fontWeight: '700' }],
        heading: ['1.0625rem',  { lineHeight: '1.5rem',   fontWeight: '600' }],
        body:    ['0.9375rem',  { lineHeight: '1.375rem'                     }],
        caption: ['0.8125rem',  { lineHeight: '1.125rem', fontWeight: '500',
                                  letterSpacing: '0.04em' }],
        label:   ['0.6875rem',  { lineHeight: '1rem',     fontWeight: '600',
                                  letterSpacing: '0.08em' }],
      },
    },
  },
  plugins: [],
}
