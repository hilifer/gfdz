/**
 * API 请求封装
 *
 * - Attaches the Bearer token from the "token" cookie.
 * - On 401, clears the token and redirects to /login **once** (avoids loops).
 */
export function useApi() {
  const config = useRuntimeConfig();
  const token = useCookie("token");

  const baseURL = config.public.apiBase;

  // Simple guard so a burst of 401s only triggers one redirect
  let redirecting = false;

  async function request<T = any>(
    url: string,
    options: {
      method?: string;
      body?: any;
      params?: Record<string, any>;
    } = {}
  ): Promise<T> {
    const headers: Record<string, string> = {};
    if (token.value) {
      headers["Authorization"] = `Bearer ${token.value}`;
    }

    try {
      const res = await $fetch<T>(url, {
        baseURL,
        method: (options.method || "GET") as any,
        headers,
        body: options.body,
        params: options.params,
      });

      return res;
    } catch (error: any) {
      const status =
        error?.response?.status ?? error?.status ?? error?.statusCode;

      // Global 401 handling: clear token and redirect to login (once)
      if (status === 401 && !redirecting) {
        redirecting = true;
        token.value = null;
        // Use nextTick to avoid interrupting current render cycle
        await navigateTo("/login");
        redirecting = false;
      }
      throw error;
    }
  }

  return {
    get: <T = any>(url: string, params?: Record<string, any>) =>
      request<T>(url, { params }),

    post: <T = any>(url: string, body?: any) =>
      request<T>(url, { method: "POST", body }),

    put: <T = any>(url: string, body?: any) =>
      request<T>(url, { method: "PUT", body }),

    del: <T = any>(url: string) => request<T>(url, { method: "DELETE" }),
  };
}
