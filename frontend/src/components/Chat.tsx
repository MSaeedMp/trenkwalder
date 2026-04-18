import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useChat } from "@ai-sdk/react";
import type { JSONValue, UIMessage } from "ai";
import {
  ArrowDown,
  FileText,
  Loader2,
  SendHorizontal,
  Square,
  SquarePen,
} from "lucide-react";
import { type ChangeEvent, useCallback, useEffect, useRef, useState } from "react";
import Markdown from "react-markdown";

import { ModeToggle } from "./ModeToggle";

const SUGGESTIONS = [
  "How many vacation days do I have left?",
  "What is the remote work policy?",
  "Who works in the Engineering department?",
  "What benefits are available?",
];

export function Chat() {
  const [error, setError] = useState<string | null>(null);
  const { messages, input, handleInputChange, handleSubmit, status, stop, data, append } =
    useChat({
      api: "/api/v1/chat",
      streamProtocol: "data",
      experimental_prepareRequestBody: ({ id, messages }) => ({
        conversation_id: id,
        messages: messages.map((message) => ({
          role: message.role,
          content: message.content,
        })),
      }),
      onError: (err) => {
        setError(err.message || "Something went wrong. Please try again.");
        setTimeout(() => setError(null), 5000);
      },
    });

  const bottomRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [expanded, setExpanded] = useState(false);

  const autoResize = useCallback(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    const h = Math.min(el.scrollHeight, 200);
    el.style.height = `${h}px`;
    setExpanded(h > 48);
  }, []);

  const onInputChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    handleInputChange(e);
    autoResize();
  };

  useEffect(() => {
    autoResize();
  }, [input, autoResize]);
  const [showScrollBtn, setShowScrollBtn] = useState(false);
  const isActive = status === "streaming" || status === "submitted";

  const lastMsgCount = useRef(0);
  useEffect(() => {
    if (messages.length > lastMsgCount.current) {
      lastMsgCount.current = messages.length;
      const el = scrollContainerRef.current;
      if (el && el.scrollHeight > el.clientHeight) {
        requestAnimationFrame(() => {
          el.scrollTop = el.scrollHeight;
        });
      }
    }
  }, [messages.length]);

  const handleScroll = () => {
    const el = scrollContainerRef.current;
    if (!el) return;
    setShowScrollBtn(el.scrollHeight - el.scrollTop - el.clientHeight > 100);
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (input.trim() && !isActive) handleSubmit();
    }
  };

  return (
    <div className="flex h-dvh flex-col overflow-hidden bg-background">
      <header className="flex shrink-0 items-center justify-between bg-background px-6 py-3">
        <button
          onClick={() => window.location.reload()}
          className="flex cursor-pointer items-center gap-3 px-1 py-0.5 opacity-80 transition-opacity hover:opacity-100"
        >
          <span className="font-heading text-2xl font-black tracking-tighter text-foreground">A</span>
          <div className="text-left">
            <h1 className="font-heading text-sm font-semibold leading-5 tracking-tight">Agentic AI</h1>
            <p className="text-xs leading-4 text-muted-foreground">Your company assistant</p>
          </div>
        </button>
        <div className="flex items-center gap-1">
          {messages.length > 0 && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => window.location.reload()}
              className="size-8"
              data-testid="new-chat-button"
            >
              <SquarePen className="size-4" />
              <span className="sr-only">New conversation</span>
            </Button>
          )}
          <ModeToggle />
        </div>
      </header>

      <div ref={scrollContainerRef} onScroll={handleScroll} className="relative min-h-0 flex-1 overflow-y-auto scrollbar-none">
        <div className="mx-auto max-w-3xl px-4 py-6 sm:px-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center pt-32 pb-24">
              <h2 className="font-heading text-2xl font-semibold leading-8 tracking-tight">How can I help you?</h2>
              <p className="mt-2 max-w-md text-center text-sm leading-6 text-muted-foreground">Ask about policies, people, or workplace info.</p>
              <div className="mt-7 grid w-full max-w-[36rem] gap-2.5 sm:grid-cols-2">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => void append({ role: "user", content: s })}
                    className="cursor-pointer rounded-lg border bg-card px-3.5 py-2.5 text-left text-sm leading-5 text-card-foreground transition-colors hover:bg-accent"
                    data-testid="suggestion-button"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((message, idx) => (
              <MessageBubble
                key={message.id}
                message={message}
                isStreaming={isActive && idx === messages.length - 1}
                citationsData={message.role === "assistant" && idx === messages.length - 1 ? data : undefined}
              />
            ))
          )}
          {isActive && messages[messages.length - 1]?.role === "user" && (
            <Shimmer />
          )}
          <div ref={bottomRef} />
        </div>

        {showScrollBtn && (
          <button
            onClick={() => bottomRef.current?.scrollIntoView({ behavior: "smooth" })}
            className="absolute bottom-4 left-1/2 -translate-x-1/2 cursor-pointer rounded-lg border bg-card p-2 shadow-md hover:bg-accent"
          >
            <ArrowDown className="size-4" />
          </button>
        )}
      </div>

      <div className="shrink-0 bg-background px-4 pb-5 pt-3 sm:px-6">
        {error && (
          <div className="mx-auto mb-2 max-w-3xl rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-2.5 text-sm text-destructive">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="mx-auto max-w-3xl">
          <div className="overflow-hidden rounded-2xl border bg-card shadow-sm focus-within:ring-2 focus-within:ring-ring">
            <div className={cn("flex", !expanded && "min-h-[44px] items-center")}>
              <textarea
                ref={textareaRef}
                value={input}
                onChange={onInputChange}
                onKeyDown={onKeyDown}
                placeholder="Ask a question..."
                disabled={isActive}
                rows={1}
                className={cn(
                  "max-h-[200px] flex-1 resize-none overflow-y-auto bg-transparent px-4 py-2 text-sm leading-5",
                  "placeholder:text-muted-foreground",
                  "focus:outline-none",
                  "disabled:cursor-not-allowed disabled:opacity-50",
                )}
                data-testid="chat-input"
              />
              {!expanded && <SendButton isActive={isActive} hasInput={!!input.trim()} onStop={stop} />}
            </div>
            {expanded && (
              <div className="flex items-center justify-end px-2 pb-1.5">
                <SendButton isActive={isActive} hasInput={!!input.trim()} onStop={stop} />
              </div>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}

const TOOL_LABELS: Record<string, string> = {
  search_documents: "Searching company documents",
  find_employees: "Looking up employees",
  get_department_headcount: "Checking department size",
  get_vacation_balance: "Checking your vacation balance",
  get_payroll_summary: "Retrieving payroll info",
};

function MessageBubble({
  message,
  isStreaming,
  citationsData,
}: {
  message: UIMessage;
  isStreaming?: boolean;
  citationsData?: JSONValue[];
}) {
  const isUser = message.role === "user";
  const messageText = getMessageText(message);
  const answerText = isUser ? messageText : stripCitationMarkers(messageText);
  const displayedText = useTypewriterText(answerText, !isUser);
  const hasText = answerText.trim().length > 0;

  if (isUser) {
    return (
      <div className="flex justify-end py-3 [overflow-wrap:anywhere]">
        <div className="max-w-[80%] rounded-2xl bg-muted px-4 py-2.5 text-sm leading-relaxed text-foreground">
          {answerText}
        </div>
      </div>
    );
  }

  const toolParts = message.parts.filter((p) => p.type === "tool-invocation");
  const showReasoning = toolParts.length > 0 && isStreaming && !hasText;
  const showToolStatus = toolParts.length > 0 && isStreaming && !hasText;
  const showCitations = !isStreaming && hasText && displayedText.length >= answerText.length;

  return (
    <div className="py-3 [overflow-wrap:anywhere]">
      {showToolStatus && (
        <div className="mb-2 space-y-1">
          {toolParts.map((part, i) => {
            if (part.type !== "tool-invocation") return null;
            const label = TOOL_LABELS[part.toolInvocation.toolName] ?? part.toolInvocation.toolName;
            const done = part.toolInvocation.state === "result";
            return (
              <div key={`tool-${message.id}-${String(i)}`} className="flex items-center gap-2 text-xs text-muted-foreground">
                {done ? (
                  <span className="size-1.5 rounded-full bg-muted-foreground/40" />
                ) : (
                  <Loader2 className="size-3 animate-spin" />
                )}
                <span className={cn(done && "line-through opacity-50")}>{label}</span>
              </div>
            );
          })}
        </div>
      )}
      {showReasoning && <ShimmerText />}
      {displayedText.trim() && (
        <div className="text-sm leading-relaxed text-foreground" data-testid="assistant-message-text">
          <div className="prose prose-sm max-w-none dark:prose-invert">
            <Markdown>{displayedText}</Markdown>
          </div>
        </div>
      )}
      {showCitations && <CitationsList data={citationsData} />}
    </div>
  );
}

function getMessageText(message: UIMessage) {
  const partsText = message.parts
    .filter((part) => part.type === "text")
    .map((part) => part.text)
    .join("");

  return partsText || message.content;
}

function stripCitationMarkers(text: string) {
  return text
    .replace(/\s*\[[^\]]+?\s+§[^\]]+?\]/g, "")
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n");
}

function useTypewriterText(text: string, enabled: boolean) {
  const [displayedText, setDisplayedText] = useState("");
  const shouldAnimate = enabled || (displayedText.length > 0 && displayedText.length < text.length);

  useEffect(() => {
    if (!shouldAnimate || displayedText.length >= text.length) {
      return;
    }

    const interval = window.setInterval(() => {
      setDisplayedText((current) => {
        if (!text.startsWith(current)) {
          return text.slice(0, Math.min(1, text.length));
        }

        const step = current.length < 80 ? 2 : 8;
        const nextLength = Math.min(current.length + step, text.length);
        return text.slice(0, nextLength);
      });
    }, 16);

    return () => window.clearInterval(interval);
  }, [displayedText.length, shouldAnimate, text]);

  return shouldAnimate || displayedText.length > 0 ? displayedText : text;
}

function ShimmerText() {
  return (
    <div className="py-1">
      <span className="shimmer-text text-sm font-medium">Generating response...</span>
    </div>
  );
}

function Shimmer() {
  return (
    <div className="py-3">
      <span className="shimmer-text text-sm font-medium">Thinking...</span>
    </div>
  );
}

function SendButton({ isActive, hasInput, onStop }: { isActive: boolean; hasInput: boolean; onStop: () => void }) {
  const base = "mr-1 size-9 shrink-0 rounded-lg shadow-sm";
  if (isActive) {
    return (
      <Button type="button" size="icon" onClick={onStop} className={base} data-testid="stop-button">
        <Square className="size-3.5" />
      </Button>
    );
  }
  return (
    <Button type="submit" size="icon" disabled={!hasInput} className={base} data-testid="send-button">
      <SendHorizontal className={cn("size-4 transition-transform duration-200 ease-out", hasInput && "-rotate-45")} />
    </Button>
  );
}

function CitationsList({ data }: { data?: JSONValue[] }) {
  if (!data) return null;
  const citations: Array<{ source: string; section?: string }> = [];
  const seen = new Set<string>();

  for (const item of data) {
    if (typeof item === "object" && item !== null && "source" in item && typeof (item as Record<string, unknown>).source === "string") {
      const citation = item as { source: string; section?: string };
      const key = `${citation.source}__${citation.section ?? ""}`;
      if (!seen.has(key)) {
        seen.add(key);
        citations.push(citation);
      }
    }
  }
  if (citations.length === 0) return null;

  return (
    <div className="mt-4 border-t pt-3" data-testid="citations-list">
      <div className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
        <FileText className="size-3.5" />
        References
      </div>
      <ol className="space-y-1.5">
        {citations.map((c, i) => (
          <li key={`${c.source}-${c.section ?? ""}`} className="flex gap-2 text-sm leading-5 text-muted-foreground">
            <span className="flex size-5 shrink-0 items-center justify-center rounded-lg bg-muted text-xs font-medium text-foreground">
              {i + 1}
            </span>
            <span>
              <span className="font-medium text-foreground">{c.source}</span>
              {c.section && <span> — {c.section}</span>}
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}
