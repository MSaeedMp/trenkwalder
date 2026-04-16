import { createRootRoute, Outlet, ScrollRestoration } from "@tanstack/react-router";
import { TooltipProvider } from "@/components/ui/tooltip";

export const Route = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  return (
    <TooltipProvider>
      <ScrollRestoration />
      <Outlet />
    </TooltipProvider>
  );
}
