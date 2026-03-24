/**
 * 认证状态管理
 *
 * - Token is persisted in a cookie (24 h, accessible client + server).
 * - `fetchUser()` validates the token against /auth/me on app load.
 * - On token expiry / invalid token the cookie is cleared gracefully.
 */
export function useAuth() {
  const token = useCookie("token", {
    maxAge: 60 * 60 * 24, // 24 hours
    path: "/",
    sameSite: "lax",
  });
  const user = useState<any>("user", () => null);

  const isLoggedIn = computed(() => !!token.value);

  async function login(username: string, password: string) {
    const api = useApi();
    const res = await api.post<{ token: string; user: any }>("/auth/login", {
      username,
      password,
    });
    token.value = res.token;
    user.value = res.user;
    return res;
  }

  function logout() {
    token.value = null;
    user.value = null;
    navigateTo("/login");
  }

  /**
   * Validate current token by fetching user profile.
   * If the token is invalid / expired, clear it silently
   * (the auth middleware will redirect to /login).
   *
   * Uses skipAuthRedirect so a 401 here does NOT trigger another
   * redirect to /login (which would cause a loop on the login page).
   */
  async function fetchUser() {
    if (!token.value) return null;
    try {
      const api = useApi();
      user.value = await api.get("/auth/me", undefined, {
        skipAuthRedirect: true,
      });
      return user.value;
    } catch {
      // Token invalid or expired — clear it without redirect loop
      token.value = null;
      user.value = null;
      return null;
    }
  }

  return { token, user, isLoggedIn, login, logout, fetchUser };
}
