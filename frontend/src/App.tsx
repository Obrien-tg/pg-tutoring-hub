import { useState, type FormEvent } from "react";
import { useQuery } from "@tanstack/react-query";
import { Navigate, Route, Routes, useNavigate } from "react-router-dom";

import { ApiClient, ApiError } from "./api";
import type {
  DashboardPayload,
  StudentDashboardPayload,
  User,
} from "./types";

const api = new ApiClient();

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
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
      <span className="brand">PG Tutoring Hub</span>
      <span>{user.full_name || user.username}</span>
    </header>
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
