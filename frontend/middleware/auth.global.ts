/**
 * 全局认证中间件
 *
 * - Unauthenticated visitors are sent to /login.
 * - Authenticated visitors that land on /login are sent to /.
 * - A flag prevents redirect loops: if we already redirected once
 *   in this navigation cycle we let it through.
 */
export default defineNuxtRouteMiddleware((to, from) => {
  const token = useCookie("token");

  // Allow the /login page when there is no token (normal case)
  if (to.path === "/login" && !token.value) {
    return; // allow
  }

  // If user is already logged in and tries to visit /login, redirect to dashboard
  if (to.path === "/login" && token.value) {
    return navigateTo("/");
  }

  // For all other pages, require authentication
  if (to.path !== "/login" && !token.value) {
    // Avoid redirect loops: if we are already coming from /login, don't redirect again
    if (from && from.path === "/login") {
      return;
    }
    return navigateTo("/login");
  }
});
