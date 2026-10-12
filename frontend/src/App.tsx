import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { Navigate, Route, Routes, useNavigate, useParams } from "react-router-dom";

import { ApiClient, ApiError } from "./api";
import type {
  DashboardPayload,
  ChatMessage,
  ChatRoom,
  StudentDashboardPayload,
  User,
} from "./types";

const api = new ApiClient();

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/chat" element={<RequireAuth><ChatPage /></RequireAuth>} />
      <Route path="/chat/:roomId" element={<RequireAuth><ChatPage /></RequireAuth>} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

function LoginPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      await api.login(username, password);
      navigate("/dashboard");
    } catch (reason) {
      setError(
        reason instanceof ApiError
          ? reason.message
          : "We could not sign you in.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-card">
        <p className="eyebrow">PG Tutoring Hub</p>
        <h1>Welcome back, learner.</h1>
        <p className="lede">
          Sign in and let&apos;s take your next small step together.
        </p>
        <form onSubmit={handleSubmit} className="stack">
          {error && <p className="error-banner" role="alert">{error}</p>}
          <label>
            Username
            <input
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
              autoComplete="username"
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              autoComplete="current-password"
            />
          </label>
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Signing you in..." : "Sign in"}
          </button>
        </form>
      </section>
    </main>
  );
}

function DashboardPage() {
  const userQuery = useQuery({
    queryKey: ["current-user"],
    queryFn: () => api.getCurrentUser(),
    retry: false,
  });
  const dashboardQuery = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => api.getDashboard(),
    enabled: userQuery.isSuccess,
    retry: false,
  });

  if (userQuery.isPending || dashboardQuery.isPending) {
    return <LoadingState />;
  }
  if (userQuery.error instanceof ApiError && userQuery.error.status === 401) {
    return <Navigate to="/login" replace />;
  }
  if (userQuery.error || dashboardQuery.error) {
    return <ErrorState />;
  }

  return (
    <DashboardContent user={userQuery.data} dashboard={dashboardQuery.data} />
  );
}

function DashboardContent({
  user,
  dashboard,
}: {
  user: User;
  dashboard: DashboardPayload;
}) {
  if (dashboard.role !== "student") {
    return (
      <main className="page-shell">
        <Header user={user} />
        <section className="placeholder-card">
          <p className="eyebrow">Coming soon</p>
          <h1>Your dashboard is being built.</h1>
          <p>
            We&apos;re preparing a helpful space for {dashboard.role}s. Your
            account is ready.
          </p>
        </section>
      </main>
    );
  }

  return (
    <main className="page-shell">
      <Header user={user} />
      <StudentDashboard dashboard={dashboard} />
    </main>
  );
}

function StudentDashboard({
  dashboard,
}: {
  dashboard: StudentDashboardPayload;
}) {
  return (
    <div className="dashboard-content">
      <section className="welcome-row">
        <div>
          <p className="eyebrow">Your learning space</p>
          <h1>Let&apos;s make progress today.</h1>
        </div>
        <div className="completion-pill">
          {dashboard.completion_rate}% complete
        </div>
      </section>

      <section className="do-now-card">
        <div>
          <p className="eyebrow">Do now</p>
          <h2>
            {dashboard.next_assignment?.title ?? "You&apos;re all caught up!"}
          </h2>
          <p>
            {dashboard.next_assignment
              ? "A little focused effort is a great next step."
              : "Take a moment to celebrate your progress, then explore something new."}
          </p>
        </div>
        {dashboard.next_assignment && (
          <span className="date-chip">
            {formatDate(dashboard.next_assignment.due_date)}
          </span>
        )}
      </section>

      <div className="dashboard-grid">
        <section className="panel">
          <h2>Recently graded</h2>
          {dashboard.graded_submissions.length === 0 ? (
            <p className="muted">
              Your first marked assignment will appear here.
            </p>
          ) : (
            <ul className="graded-list">
              {dashboard.graded_submissions.map((submission) => (
                <li key={submission.id}>
                  <span>{submission.assignment_title}</span>
                  <strong>
                    {submission.grade || `${submission.numeric_score}%`}
                  </strong>
                </li>
              ))}
            </ul>
          )}
        </section>
        <section className="panel">
          <h2>Subject mastery</h2>
          {dashboard.subject_mastery.length === 0 ? (
            <p className="muted">
              Complete a lesson to see your strengths grow.
            </p>
          ) : (
            dashboard.subject_mastery.map((subject) => (
              <div className="progress-row" key={subject.name}>
                <div>
                  <span>{subject.name}</span>
                  <span>{subject.percentage}%</span>
                </div>
                <div className="progress-track">
                  <span style={{ width: `${subject.percentage}%` }} />
                </div>
              </div>
            ))
          )}
        </section>
      </div>

      <section className="panel">
        <h2>Weekly effort</h2>
        <div className="effort-chart">
          {dashboard.weekly_effort.map((day) => (
            <div
              className="effort-bar"
              key={day.date}
              title={`${day.minutes} minutes`}
            >
              <span
                style={{
                  height: `${Math.min(Math.max(day.minutes, 4), 100)}%`,
                }}
              />
              <small>
                {new Date(day.date).toLocaleDateString("en-ZA", {
                  weekday: "short",
                })}
              </small>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function Header({ user }: { user: User }) {
  return (
    <header className="site-header">
      <nav className="site-nav" aria-label="Main navigation">
        <span className="brand">PG Tutoring Hub</span>
        <a href="/dashboard">Dashboard</a>
        <a href="/assignments">Assignments</a>
        <a href="/materials">Materials</a>
        <a href="/chat">Chat</a>
      </nav>
      <span>{user.full_name || user.username}</span>
    </header>
  );
}

function RequireAuth({ children }: { children: ReactNode }) {
  const userQuery = useQuery({
    queryKey: ["current-user"],
    queryFn: () => api.getCurrentUser(),
    retry: false,
  });

  if (userQuery.isPending) return <LoadingState />;
  if (userQuery.error instanceof ApiError && userQuery.error.status === 401) {
    return <Navigate to="/login" replace />;
  }
  if (userQuery.error || !userQuery.data) return <ErrorState />;
  return <>{children}</>;
}

function ChatPage() {
  const navigate = useNavigate();
  const { roomId } = useParams();
  const [actionError, setActionError] = useState("");
  const userQuery = useQuery({
    queryKey: ["current-user"],
    queryFn: () => api.getCurrentUser(),
    retry: false,
  });
  const roomsQuery = useQuery({
    queryKey: ["chat-rooms"],
    queryFn: () => api.getRooms(),
  });
  const selectedRoom = roomsQuery.data?.results.find(
    (room) => room.id === Number(roomId),
  ) ?? null;

  async function openTeacherChat() {
    setActionError("");
    try {
      const room = await api.openTeacherChat();
      await roomsQuery.refetch();
      navigate(`/chat/${room.id}`);
    } catch {
      setActionError("Your teacher chat is not available just yet. Please try again soon.");
    }
  }

  if (roomsQuery.isPending || userQuery.isPending) return <LoadingState />;
  if (roomsQuery.error || userQuery.error || !userQuery.data) return <ErrorState />;

  return (
    <main className="page-shell">
      <Header user={userQuery.data} />
      <div className="chat-layout">
        <section className="chat-sidebar panel">
          <div className="chat-heading">
            <div>
              <p className="eyebrow">Your conversations</p>
              <h1>Chat</h1>
            </div>
            <button type="button" onClick={openTeacherChat}>Message teacher</button>
          </div>
          {actionError && <p className="error-banner" role="alert">{actionError}</p>}
          {roomsQuery.data.results.length === 0 ? (
            <p className="muted">No chats yet. Say hello to your teacher.</p>
          ) : (
            <ul className="room-list">
              {roomsQuery.data.results.map((room) => (
                <li key={room.id}>
                  <button
                    type="button"
                    className={room.id === selectedRoom?.id ? "room-button active" : "room-button"}
                    onClick={() => navigate(`/chat/${room.id}`)}
                  >
                    <strong>{room.name}</strong>
                    <span>{room.latest_message?.content ?? "No messages yet"}</span>
                    {room.latest_message && (
                      <small>{formatRelativeTime(room.latest_message.timestamp)}</small>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
        <ChatThread room={selectedRoom} user={userQuery.data} />
      </div>
    </main>
  );
}

function ChatThread({ room, user }: { room: ChatRoom | null; user: User }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [content, setContent] = useState("");
  const [error, setError] = useState("");
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    if (!room) {
      setMessages([]);
      return;
    }
    let active = true;
    const load = async () => {
      try {
        const result = await api.getMessages(room.id);
        if (active) {
          setMessages(result.results);
          setError("");
        }
      } catch {
        if (active) setError("We couldn’t load this chat just now.");
      }
    };
    void load();
    const interval = window.setInterval(load, 7000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, [room]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = content.trim();
    if (!room || !trimmed) return;
    setIsSending(true);
    setError("");
    try {
      const message = await api.sendMessage(room.id, trimmed);
      setMessages((current) => [...current, message]);
      setContent("");
    } catch {
      setError("Your message could not be sent. Please try again.");
    } finally {
      setIsSending(false);
    }
  }

  if (!room) {
    return (
      <section className="chat-thread panel">
        <p className="muted">Choose a chat to get started.</p>
      </section>
    );
  }

  return (
    <section className="chat-thread panel">
      <div className="thread-header">
        <p className="eyebrow">Conversation</p>
        <h2>{room.name}</h2>
      </div>
      <div className="message-list">
        {messages.length === 0 ? (
          <p className="muted">Write a short message — your teacher will see it here.</p>
        ) : (
          messages.map((message) => {
            const own = message.sender === user.id;
            return (
              <div className={own ? "message own" : "message"} key={message.id}>
                {!own && <strong>{message.sender_username}</strong>}
                <p>{message.content}</p>
                <small>{formatRelativeTime(message.timestamp)}</small>
              </div>
            );
          })
        )}
      </div>
      {error && <p className="error-banner" role="alert">{error}</p>}
      <form className="composer" onSubmit={handleSubmit}>
        <input
          value={content}
          onChange={(event) => setContent(event.target.value)}
          placeholder="Write a message..."
          aria-label="Message"
          disabled={isSending}
        />
        <button type="submit" disabled={isSending || !content.trim()}>
          {isSending ? "Sending..." : "Send"}
        </button>
      </form>
    </section>
  );
}

function LoadingState() {
  return (
    <main className="center-state">
      <p>Getting your learning space ready...</p>
    </main>
  );
}

function ErrorState() {
  return (
    <main className="center-state">
      <p>We couldn&apos;t load your dashboard. Please try again.</p>
    </main>
  );
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("en-ZA", {
    day: "numeric",
    month: "short",
  });
}

function formatRelativeTime(value: string) {
  const minutes = Math.max(0, Math.round((Date.now() - new Date(value).getTime()) / 60000));
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return new Date(value).toLocaleDateString("en-ZA", { day: "numeric", month: "short" });
}
