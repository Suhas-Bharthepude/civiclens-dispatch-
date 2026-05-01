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
        display: ['1.5rem',  { lineHeight: '2rem',    fontWeight: '600' }],
        heading: ['1rem',    { lineHeight: '1.5rem',  fontWeight: '600' }],
        body:    ['0.875rem',{ lineHeight: '1.25rem'                    }],
        caption: ['0.75rem', { lineHeight: '1rem',    fontWeight: '500',
                               letterSpacing: '0.05em' }],
      },
    },
  },
  plugins: [],
}
