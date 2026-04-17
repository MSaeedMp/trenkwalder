import { Chat } from "@/components/Chat";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: IndexPage,
});

function IndexPage() {
  return <Chat />;
}
