import { Button } from "@/components/ui/button";
import { useTheme } from "./theme-provider";
import { Moon, Sun } from "lucide-react";

export function ModeToggle() {
  const { theme, setTheme } = useTheme();

  const toggle = () => {
    if (theme === "dark") setTheme("light");
    else setTheme("dark");
  };

  return (
    <Button variant="ghost" size="icon" onClick={toggle} className="size-10">
      <Sun className="size-4 scale-100 rotate-0 transition-all dark:scale-0 dark:-rotate-90" />
      <Moon className="absolute size-4 scale-0 rotate-90 transition-all dark:scale-100 dark:rotate-0" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  );
}
