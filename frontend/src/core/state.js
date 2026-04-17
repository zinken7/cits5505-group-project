/**
 * Simple Reactive State Store (Pub/Sub)
 *
 * Lightweight state management for CSR interactivity.
 * Works alongside jQuery — no framework needed.
 *
 * Usage:
 *   const store = createStore({ count: 0 });
 *   store.subscribe((state) => console.log(state.count));
 *   store.setState({ count: 1 }); // triggers subscribers
 */

/**
 * Create a reactive store with pub/sub notifications.
 * @param {Object} initialState
 * @returns {{ getState, setState, subscribe }}
 */
export function createStore(initialState = {}) {
  let state = { ...initialState };
  const listeners = new Set();

  return {
    /** Get a shallow copy of the current state. */
    getState() {
      return { ...state };
    },

    /**
     * Merge updates into state and notify subscribers.
     * @param {Object|Function} update - Object to merge, or function (prevState) => partialUpdate
     */
    setState(update) {
      const partial =
        typeof update === "function" ? update(state) : update;
      state = { ...state, ...partial };
      listeners.forEach((fn) => fn(state));
    },

    /**
     * Subscribe to state changes.
     * @param {Function} fn - Callback receiving the new state
     * @returns {Function} Unsubscribe function
     */
    subscribe(fn) {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
  };
}
