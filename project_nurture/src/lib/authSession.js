const authSessionKey = 'project-nurture-auth-session';
export const authSessionChangedEvent = 'project-nurture-auth-session-changed';
export const authSessionTtlMs = 12 * 60 * 60 * 1000;

const emitSessionChange = () => {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new Event(authSessionChangedEvent));
  }
};

const readSession = () => {
  if (typeof window === 'undefined') return null;

  try {
    const rawSession = window.localStorage.getItem(authSessionKey);
    return rawSession ? JSON.parse(rawSession) : null;
  } catch {
    return null;
  }
};

export const getAuthSessionStatus = userId => {
  const session = readSession();

  if (!session) return 'missing';
  if (!Number.isFinite(Number(session.expiresAt))) return 'invalid';
  if (Number(session.expiresAt) <= Date.now()) return 'expired';
  if (!userId) return 'fresh';
  if (session.userId !== userId) return 'mismatch';

  return 'fresh';
};

export const createAuthSession = userId => {
  const now = Date.now();
  const session = {
    userId,
    createdAt: now,
    expiresAt: now + authSessionTtlMs,
  };

  window.localStorage.setItem(authSessionKey, JSON.stringify(session));
  emitSessionChange();
  return session;
};

export const clearAuthSession = () => {
  if (typeof window !== 'undefined') {
    window.localStorage.removeItem(authSessionKey);
    emitSessionChange();
  }
};

export const hasFreshAuthSession = userId => {
  return getAuthSessionStatus(userId) === 'fresh';
};
