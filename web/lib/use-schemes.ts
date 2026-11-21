"use client";

import { useCallback, useEffect, useState } from "react";
import { getSchemes, type Failure } from "./client";
import type { SchemeSummary } from "./types";

type State =
  | { status: "loading" }
  | { status: "ready"; schemes: SchemeSummary[] }
  | { status: "error"; code: Failure };

// The list only changes when the backend is redeployed, so one fetch per page load is enough.
let cache: SchemeSummary[] | null = null;

export function useSchemes() {
  const [state, setState] = useState<State>(() =>
    cache ? { status: "ready", schemes: cache } : { status: "loading" },
  );
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    if (cache) return;
    let cancelled = false;
    getSchemes().then((result) => {
      if (cancelled) return;
      if (result.ok) {
        cache = result.data;
        setState({ status: "ready", schemes: result.data });
      } else {
        setState({ status: "error", code: result.code });
      }
    });
    return () => {
      cancelled = true;
    };
  }, [attempt]);

  const retry = useCallback(() => {
    setState({ status: "loading" });
    setAttempt((n) => n + 1);
  }, []);

  return { state, retry };
}

/** True once `active` has stayed true for `ms`: used to say "getting things ready" on a cold start. */
export function useSlow(active: boolean, ms = 2500): boolean {
  const [slow, setSlow] = useState(false);
  useEffect(() => {
    if (!active) {
      const reset = setTimeout(() => setSlow(false), 0);
      return () => clearTimeout(reset);
    }
    const timer = setTimeout(() => setSlow(true), ms);
    return () => clearTimeout(timer);
  }, [active, ms]);
  return slow;
}
