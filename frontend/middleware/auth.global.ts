/**
 * 全局认证中间件
 */
export default defineNuxtRouteMiddleware((to) => {
  const token = useCookie("token");

  if (to.path !== "/login" && !token.value) {
    return navigateTo("/login");
  }

  if (to.path === "/login" && token.value) {
    return navigateTo("/");
  }
});
