const authSessionKey = 'project-nurture-auth-session';
export const authSessionTtlMs = 12 * 60 * 60 * 1000;

const readSession = () => {
  if (typeof window === 'undefined') return null;

  try {
    const rawSession = window.localStorage.getItem(authSessionKey);
    return rawSession ? JSON.parse(rawSession) : null;
  } catch {
    return null;
  }
};

export const createAuthSession = userId => {
  const now = Date.now();
  const session = {
    userId,
    createdAt: now,
    expiresAt: now + authSessionTtlMs,
  };

  window.localStorage.setItem(authSessionKey, JSON.stringify(session));
  return session;
};

export const clearAuthSession = () => {
  if (typeof window !== 'undefined') {
    window.localStorage.removeItem(authSessionKey);
  }
};

export const hasFreshAuthSession = userId => {
  const session = readSession();

  if (!session || session.userId !== userId) return false;
  if (!Number.isFinite(Number(session.expiresAt))) return false;

  return Number(session.expiresAt) > Date.now();
};
