import { useCallback, useEffect, useRef, useState } from 'react';
import { apiFetch } from '../api.js';

/**
 * Fetch a URL immediately, then re-fetch every `ms` milliseconds while `active` is true.
 * Returns { data, error, loading, reload } — reload() forces an immediate re-fetch.
 */
export default function usePoll(url, ms = 3000, active = true) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [nonce, setNonce] = useState(0);

  const activeRef = useRef(active);
  activeRef.current = active;
  const inFlight = useRef(false);

  const reload = useCallback(() => setNonce((n) => n + 1), []);

  useEffect(() => {
    let cancelled = false;

    const tick = async () => {
      if (inFlight.current) return;
      inFlight.current = true;
      try {
        const json = await apiFetch(url);
        if (!cancelled) {
          setData(json);
          setError(null);
        }
      } catch (e) {
        if (!cancelled) setError(e.message || String(e));
      } finally {
        inFlight.current = false;
        if (!cancelled) setLoading(false);
      }
    };

    tick();
    const interval = setInterval(() => {
      if (activeRef.current) tick();
    }, ms);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [url, ms, nonce]);

  return { data, error, loading, reload };
}
