/**
 * API 请求封装
 */
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
      // Global 401 handling: clear token and redirect to login
      if (error?.response?.status === 401 || error?.status === 401 || error?.statusCode === 401) {
        token.value = null;
        navigateTo("/login");
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
