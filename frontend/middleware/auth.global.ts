/**
 * 全局认证中间件
 *
 * - Unauthenticated visitors are sent to /login.
 * - Authenticated visitors that land on /login are sent to /.
 * - Uses abortNavigation() to prevent redirect loops.
 */
export default defineNuxtRouteMiddleware((to, _from) => {
  const token = useCookie("token");
  const isLoginPage = to.path === "/login";

  // Allow the /login page when there is no token (normal case)
  if (isLoginPage && !token.value) {
    return; // allow — user needs to log in
  }

  // If user has a token and tries to visit /login, redirect to dashboard
  if (isLoginPage && token.value) {
    return navigateTo("/", { replace: true });
  }

  // For all other pages, require a token
  if (!isLoginPage && !token.value) {
    return navigateTo("/login", { replace: true });
  }

  // Token present and not on /login — allow through
});
