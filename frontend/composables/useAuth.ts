/**
 * 认证状态管理
 */
export function useAuth() {
  const token = useCookie("token", { maxAge: 60 * 60 * 24 });
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

  async function fetchUser() {
    if (!token.value) return;
    try {
      const api = useApi();
      user.value = await api.get("/auth/me");
    } catch {
      logout();
    }
  }

  return { token, user, isLoggedIn, login, logout, fetchUser };
}
