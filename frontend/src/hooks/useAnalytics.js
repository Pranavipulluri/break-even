/**
 * useAnalytics — shared hook for real-time analytics polling.
 *
 * Features
 * ─────────
 * • Fetches /api/analytics/summary on mount and every `interval` ms
 * • Exposes `refresh()` for manual on-demand re-fetch
 * • Tracks `lastUpdatedAt` (Date) and `secondsAgo` (number, ticked every second)
 * • Cleans up both timers on unmount — no stale closures / memory leaks
 * • Uses the existing Axios `api` instance (auth token, base-URL, interceptors)
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { api } from '../services/api';

const POLL_INTERVAL_MS = 30_000; // 30 seconds

/**
 * @param {object}  options
 * @param {number}  [options.interval=30000]   Poll cadence in ms
 * @param {boolean} [options.enabled=true]     Set false to pause polling
 */
export function useAnalyticsSummary({ interval = POLL_INTERVAL_MS, enabled = true } = {}) {
  const [summary, setSummary]           = useState(null);
  const [loading, setLoading]           = useState(true);
  const [error, setError]               = useState(null);
  const [lastUpdatedAt, setLastUpdatedAt] = useState(null);
  const [secondsAgo, setSecondsAgo]     = useState(0);

  const pollRef  = useRef(null);
  const tickRef  = useRef(null);
  const mountedRef = useRef(true);

  // ── Core fetch ────────────────────────────────────────────────────────────
  const fetchSummary = useCallback(async (showSpinner = false) => {
    try {
      if (showSpinner) setLoading(true);
      setError(null);

      const res = await api.get('/analytics/summary');

      if (!mountedRef.current) return;

      const data = res.data?.summary ?? res.data ?? {};
      setSummary(data);

      const now = new Date();
      setLastUpdatedAt(now);
      setSecondsAgo(0);
    } catch (err) {
      if (!mountedRef.current) return;
      setError(err?.response?.data?.error ?? err.message ?? 'Fetch failed');
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, []);

  // ── Polling setup ─────────────────────────────────────────────────────────
  useEffect(() => {
    mountedRef.current = true;

    if (!enabled) return;

    // Initial load with spinner
    fetchSummary(true);

    // Poll silently (no spinner) every `interval` ms
    pollRef.current = setInterval(() => fetchSummary(false), interval);

    // Tick "X seconds ago" counter every second
    tickRef.current = setInterval(() => {
      if (mountedRef.current) {
        setSecondsAgo((s) => s + 1);
      }
    }, 1000);

    return () => {
      mountedRef.current = false;
      clearInterval(pollRef.current);
      clearInterval(tickRef.current);
    };
  }, [enabled, interval, fetchSummary]);

  // ── Manual refresh ────────────────────────────────────────────────────────
  const refresh = useCallback(() => {
    fetchSummary(true);
    // Reset the poll timer so we don't double-fetch right after a manual refresh
    clearInterval(pollRef.current);
    pollRef.current = setInterval(() => fetchSummary(false), interval);
  }, [fetchSummary, interval]);

  return { summary, loading, error, lastUpdatedAt, secondsAgo, refresh };
}

/**
 * useAnalyticsRange — fetches range-based data whenever `range` changes.
 * Used by Analytics.jsx to re-render charts on filter change.
 *
 * @param {string}  range        e.g. "7d" | "30d" | "90d" | "1y"
 * @param {string}  businessId   User/business ID for event summary endpoint
 */
export function useAnalyticsRange(range, businessId) {
  const [analyticsData, setAnalyticsData]   = useState(null);
  const [sentimentData, setSentimentData]   = useState(null);
  const [customerData, setCustomerData]     = useState(null);
  const [eventSummary, setEventSummary]     = useState(null);
  const [loading, setLoading]               = useState(true);
  const [error, setError]                   = useState(null);
  const [lastUpdatedAt, setLastUpdatedAt]   = useState(null);
  const [secondsAgo, setSecondsAgo]         = useState(0);

  const mountedRef = useRef(true);
  const tickRef    = useRef(null);

  const fetchAll = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const daysMap = { '7d': 7, '30d': 30, '90d': 90, '1y': 365 };

      const requests = [
        api.get(`/analytics/overview?range=${range}`),
        api.get('/analytics/sentiment'),
        api.get('/analytics/customers'),
      ];

      if (businessId) {
        requests.push(
          api.get(`/events/summary/${businessId}?days=${daysMap[range] ?? 30}`)
        );
      }

      const results = await Promise.all(requests.map((p) => p.catch(() => null)));

      if (!mountedRef.current) return;

      if (results[0]?.data) setAnalyticsData(results[0].data);
      if (results[1]?.data) setSentimentData(results[1].data);
      if (results[2]?.data) setCustomerData(results[2].data);

      const evtData = results[3]?.data;
      if (evtData?.success) setEventSummary(evtData.summary);

      const now = new Date();
      setLastUpdatedAt(now);
      setSecondsAgo(0);
    } catch (err) {
      if (!mountedRef.current) return;
      setError(err?.message ?? 'Fetch failed');
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, [range, businessId]);

  // Re-fetch whenever `range` or `businessId` changes
  useEffect(() => {
    mountedRef.current = true;
    fetchAll();

    // Reset the seconds-ago ticker
    clearInterval(tickRef.current);
    tickRef.current = setInterval(() => {
      if (mountedRef.current) setSecondsAgo((s) => s + 1);
    }, 1000);

    return () => {
      mountedRef.current = false;
      clearInterval(tickRef.current);
    };
  }, [fetchAll]);

  return {
    analyticsData,
    sentimentData,
    customerData,
    eventSummary,
    loading,
    error,
    lastUpdatedAt,
    secondsAgo,
    refresh: fetchAll,
  };
}

/** Formats secondsAgo into a human-readable string */
export function formatSecondsAgo(seconds) {
  if (seconds < 5)  return 'just now';
  if (seconds < 60) return `${seconds}s ago`;
  const mins = Math.floor(seconds / 60);
  if (mins < 60)    return `${mins}m ago`;
  return `${Math.floor(mins / 60)}h ago`;
}
