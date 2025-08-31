/* Minimal client-side logger: captures errors, unhandled rejections, and console.*; batches and sends to /api/logs.
   Controlled via NEXT_PUBLIC_ENABLE_CLIENT_LOGS. */

/* eslint-disable no-console */

type LogLevel = 'log' | 'info' | 'warn' | 'error';

type LogEntry = {
  lvl: LogLevel;
  msg: string;
  ts: string; // client-side ISO timestamp
  route?: string;
  userId?: string | null;
  sessionId?: string | null;
  stack?: string;
  context?: Record<string, unknown>;
  ua?: string;
};

const BATCH_MAX = 25;
const FLUSH_MS = 3000;
const MAX_ENTRY_LEN = 10_000;

let queue: LogEntry[] = [];
let timer: number | null = null;
let initialized = false;
let clientSessionId: string | null = null;

function getApiBase(): string {
  const env = (process as any).env || {};
  // Next.js exposes only NEXT_PUBLIC_* on the client
  const base = (env.NEXT_PUBLIC_API_URL as string) || '';
  if (base) return base.replace(/\/$/, '');
  // Fallback to same-origin; backend CORS must allow this
  return '';
}

function postLogs(entries: LogEntry[]): void {
  try {
    const base = getApiBase();
    const url = base ? `${base}/api/logs` : '/api/logs';
    // Fire-and-forget
    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ entries }),
      keepalive: true, // allow send during unload
    }).catch(() => {});
  } catch {
    // ignore
  }
}

function flush(): void {
  if (queue.length === 0) return;
  const batch = queue.splice(0, BATCH_MAX);
  postLogs(batch);
}

function schedule(): void {
  if (timer != null) return;
  timer = (setTimeout(() => {
    timer = null;
    flush();
    if (queue.length > 0) schedule();
  }, FLUSH_MS) as unknown) as number;
}

function enqueue(entry: LogEntry): void {
  try {
    // Bound entry size to avoid giant payloads
    if (entry.msg && entry.msg.length > MAX_ENTRY_LEN) {
      entry.msg = entry.msg.slice(0, MAX_ENTRY_LEN) + '…';
    }
    queue.push(entry);
    if (queue.length >= BATCH_MAX) {
      flush();
    } else {
      schedule();
    }
  } catch {
    // ignore
  }
}

function getRoute(): string | undefined {
  try {
    return window.location?.pathname + window.location?.search;
  } catch {
    return undefined;
  }
}

function getUA(): string | undefined {
  try { return navigator.userAgent; } catch { return undefined; }
}

function makeEntry(lvl: LogLevel, msg: string, context?: Record<string, unknown>, stack?: string): LogEntry {
  return {
    lvl,
    msg,
    ts: new Date().toISOString(),
    route: getRoute(),
    userId: null, // can be enhanced to read from your AuthContext if desired
    sessionId: clientSessionId,
    stack,
    context,
    ua: getUA(),
  };
}

function ensureClientSessionId(): void {
  if (clientSessionId) return;
  try {
    const key = 'GRACE_CLIENT_SID';
    const existing = sessionStorage.getItem(key);
    if (existing) {
      clientSessionId = existing;
      return;
    }
    const sid = Math.random().toString(36).slice(2) + Date.now().toString(36);
    sessionStorage.setItem(key, sid);
    clientSessionId = sid;
  } catch {
    // ignore
  }
}

export function initClientLogger(router?: { events?: { on: Function; off: Function } } | any): void {
  if (initialized) return;
  initialized = true;
  ensureClientSessionId();

  // Hook window.onerror
  try {
    const prevOnError = window.onerror;
    window.onerror = function(message, source, lineno, colno, error) {
      const stack = (error && (error as any).stack) || undefined;
      enqueue(makeEntry('error', String(message), { source, lineno, colno }, stack));
      if (typeof prevOnError === 'function') return prevOnError(message, source, lineno, colno, error) as any;
      return false;
    };
  } catch {}

  // Hook unhandledrejection
  try {
    window.addEventListener('unhandledrejection', (event) => {
      const reason: any = event?.reason;
      const msg = typeof reason === 'string' ? reason : (reason?.message || 'Unhandled promise rejection');
      const stack = reason?.stack;
      enqueue(makeEntry('error', msg, { type: 'unhandledrejection' }, stack));
    });
  } catch {}

  // Wrap console methods
  (['log','info','warn','error'] as LogLevel[]).forEach((lvl) => {
    try {
      const original = (console as any)[lvl];
      (console as any)[lvl] = ((...args: any[]) => {
        try {
          const msg = args.map((a) => {
            if (typeof a === 'string') return a;
            try { return JSON.stringify(a); } catch { return String(a); }
          }).join(' ');
          enqueue(makeEntry(lvl, msg));
        } catch {}
        try { original.apply(console, args); } catch {}
      });
    } catch {}
  });

  // Wrap fetch to log failed API calls and latency
  try {
    const originalFetch = window.fetch.bind(window);
    (window as any).fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const start = performance.now();
      let url = '';
      try { url = typeof input === 'string' ? input : (input as any)?.url || ''; } catch {}
      try {
        const res = await originalFetch(input as any, init);
        const dur = Math.round(performance.now() - start);
        if (!res.ok) {
          enqueue(makeEntry('warn', 'fetch-fail', {
            url,
            status: res.status,
            statusText: res.statusText,
            durationMs: dur,
          }));
        }
        return res;
      } catch (err: any) {
        const dur = Math.round(performance.now() - start);
        enqueue(makeEntry('error', 'fetch-error', {
          url,
          durationMs: dur,
          error: err?.message || String(err),
        }, err?.stack));
        throw err;
      }
    };
  } catch {}

  // Page visibility / navigation breadcrumbs (lightweight)
  try {
    window.addEventListener('visibilitychange', () => {
      enqueue(makeEntry('info', 'visibility:' + document.visibilityState));
    });
    window.addEventListener('pageshow', () => enqueue(makeEntry('info', 'pageshow')));
    window.addEventListener('pagehide', () => enqueue(makeEntry('info', 'pagehide')));
    window.addEventListener('popstate', () => enqueue(makeEntry('info', 'popstate')));
    window.addEventListener('focus', () => enqueue(makeEntry('info', 'focus')));
    window.addEventListener('blur', () => enqueue(makeEntry('info', 'blur')));
    window.addEventListener('resize', () => {
      try {
        enqueue(makeEntry('info', 'resize', { w: window.innerWidth, h: window.innerHeight }));
      } catch { enqueue(makeEntry('info', 'resize')); }
    });
  } catch {}

  // Flush on unload
  try {
    window.addEventListener('beforeunload', () => {
      flush();
    });
  } catch {}

  // Router event breadcrumbs (Next.js)
  try {
    const ev = router?.events;
    if (ev && typeof ev.on === 'function') {
      const onStart = (url: string) => enqueue(makeEntry('info', 'routeChangeStart', { url }));
      const onComplete = (url: string) => enqueue(makeEntry('info', 'routeChangeComplete', { url }));
      const onHashStart = (url: string) => enqueue(makeEntry('info', 'hashChangeStart', { url }));
      const onHashComplete = (url: string) => enqueue(makeEntry('info', 'hashChangeComplete', { url }));
      ev.on('routeChangeStart', onStart);
      ev.on('routeChangeComplete', onComplete);
      ev.on('hashChangeStart', onHashStart);
      ev.on('hashChangeComplete', onHashComplete);
      // We do not remove handlers on unload since page unload clears them; low risk in dev
    }
  } catch {}

  // Performance observers for layout shifts (CLS) and long tasks (jank)
  try {
    // Layout Shifts
    if ('PerformanceObserver' in window) {
      try {
        const po = new PerformanceObserver((list) => {
          for (const entry of list.getEntries() as any) {
            const e: any = entry;
            // Ignore layout shifts triggered by recent user input
            if (e && e.hadRecentInput) continue;
            const ctx: Record<string, unknown> = {
              value: e?.value,
              startTime: Math.round(e?.startTime || 0),
              sources: Array.isArray(e?.sources) ? e.sources.map((s: any) => s?.node?.tagName || s?.id || 'node') : undefined,
            };
            enqueue(makeEntry('warn', 'layout-shift', ctx));
          }
        });
        (po as any).observe({ type: 'layout-shift', buffered: true });
      } catch {}

      // Long Tasks
      try {
        const po2 = new PerformanceObserver((list) => {
          for (const entry of list.getEntries() as any) {
            const e: any = entry;
            const ctx: Record<string, unknown> = {
              durationMs: Math.round(e?.duration || 0),
              startTime: Math.round(e?.startTime || 0),
              name: e?.name,
            };
            if ((e?.duration || 0) >= 50) {
              enqueue(makeEntry('warn', 'longtask', ctx));
            }
          }
        });
        (po2 as any).observe({ type: 'longtask', buffered: true });
      } catch {}
    }
  } catch {}
}

export default { initClientLogger };
