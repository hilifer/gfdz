/**
 * API 请求封装
 *
 * - Attaches the Bearer token from the "token" cookie.
 * - On 401, clears the token and redirects to /login **once** (avoids loops).
 */

// Module-level guard so a burst of 401s only triggers one redirect
let _redirectingTo401 = false;

export function useApi() {
  const config = useRuntimeConfig();
  const token = useCookie("token");

  const baseURL = config.public.apiBase;

  async function request<T = any>(
    url: string,
    options: {
      method?: string;
      body?: any;
      params?: Record<string, any>;
      /** Skip the global 401 → redirect-to-login behaviour */
      skipAuthRedirect?: boolean;
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
      if (
        status === 401 &&
        !options.skipAuthRedirect &&
        !_redirectingTo401
      ) {
        _redirectingTo401 = true;
        token.value = null;
        await navigateTo("/login", { replace: true });
        // Small delay before allowing another redirect
        setTimeout(() => {
          _redirectingTo401 = false;
        }, 1000);
      }
      throw error;
    }
  }

  return {
    get: <T = any>(
      url: string,
      params?: Record<string, any>,
      opts?: { skipAuthRedirect?: boolean }
    ) => request<T>(url, { params, ...opts }),

    post: <T = any>(url: string, body?: any) =>
      request<T>(url, { method: "POST", body }),

    put: <T = any>(url: string, body?: any) =>
      request<T>(url, { method: "PUT", body }),

    del: <T = any>(url: string) => request<T>(url, { method: "DELETE" }),
  };
}
