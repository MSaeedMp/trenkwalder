import { ThemeProvider } from "@/components/theme-provider";
import { TooltipProvider } from "@/components/ui/tooltip";
import { createRootRoute, Outlet, ScrollRestoration } from "@tanstack/react-router";

export const Route = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  return (
    <ThemeProvider defaultTheme="light">
      <TooltipProvider>
        <ScrollRestoration />
        <Outlet />
      </TooltipProvider>
    </ThemeProvider>
  );
}
