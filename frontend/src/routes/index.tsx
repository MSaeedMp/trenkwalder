import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: IndexPage,
});

function IndexPage() {
  return (
    <div className="flex min-h-svh flex-col items-center justify-center">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-foreground">
          Trenkwalder Chatbot
        </h1>
        <p className="text-muted-foreground">
          Scaffold ready. Chat UI will replace this page.
        </p>
        <div className="flex justify-center gap-2">
          <div className="h-4 w-4 rounded bg-red-500" />
          <div className="h-4 w-4 rounded bg-green-500" />
          <div className="h-4 w-4 rounded bg-blue-500" />
        </div>
      </div>
    </div>
  );
}
