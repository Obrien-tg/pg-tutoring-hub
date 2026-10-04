import { zodResolver } from "@hookform/resolvers/zod";
import { useQuery } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { useState } from "react";
import { Link, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import type { ReactNode } from "react";
import { z } from "zod";

import { ApiClient, ApiError } from "./api";
import type { StudentDashboardPayload, User } from "./types";

const api = new ApiClient();
const loginSchema = z.object({
  username: z.string().min(1, "Please enter your username."),
  password: z.string().min(1, "Please enter your password."),
});
type LoginValues = z.infer<typeof loginSchema>;

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/dashboard" element={<RequireAuth><DashboardPage /></RequireAuth>} />
      <Route path="/" element={<HomeRedirect />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function RequireAuth({ children }: { children: ReactNode }) {
  const query = useQuery({
    queryKey: ["current-user"],
    queryFn: () => api.getCurrentUser(),
    retry: false,
  });
  if (query.isPending) return <LoadingState />;
  if (query.isError || !query.data) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function HomeRedirect() {
  const query = useQuery({
    queryKey: ["current-user"],
    queryFn: () => api.getCurrentUser(),
    retry: false,
  });
  if (query.isPending) return <LoadingState />;
  return <Navigate to={query.data ? "/dashboard" : "/login"} replace />;
}

function LoginPage() {
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const { register, handleSubmit, formState: { errors, isSubmitting } } =
    useForm<LoginValues>({ resolver: zodResolver(loginSchema) });

  async function onSubmit(values: LoginValues) {
    setError("");
    try {
      await api.login(values.username, values.password);
      await api.getCurrentUser();
      navigate("/dashboard");
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "We could not sign you in.");
    }
  }

  return (
    <main className="grid min-h-screen place-items-center p-6">
      <section className="w-full max-w-md rounded-3xl border border-border bg-surface p-8 shadow-xl shadow-mint-700/10">
        <p className="mb-2 font-display text-sm font-bold uppercase tracking-widest text-mint-600">PG Tutoring Hub</p>
        <h1 className="mb-3 font-display text-4xl font-bold">Welcome back, learner.</h1>
        <p className="mb-8 text-ink-soft">Sign in and let&apos;s take your next small step together.</p>
        <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4">
          {error && <p className="rounded-xl bg-coral-100 p-3 text-coral-600" role="alert">{error}</p>}
          <label className="grid gap-1 font-bold">Username<input className="rounded-xl border border-border px-3 py-3" {...register("username")} autoComplete="username" />{errors.username && <span className="text-sm font-normal text-coral-600">{errors.username.message}</span>}</label>
          <label className="grid gap-1 font-bold">Password<input className="rounded-xl border border-border px-3 py-3" type="password" {...register("password")} autoComplete="current-password" />{errors.password && <span className="text-sm font-normal text-coral-600">{errors.password.message}</span>}</label>
          <button className="rounded-xl bg-mint-600 px-4 py-3 font-extrabold text-white hover:bg-mint-700 disabled:opacity-60" disabled={isSubmitting}>{isSubmitting ? "Signing you in..." : "Sign in"}</button>
        </form>
      </section>
    </main>
  );
}

function DashboardPage() {
  const query = useQuery({ queryKey: ["dashboard"], queryFn: () => api.getDashboard() });
  if (query.isPending) return <LoadingState />;
  if (query.isError) return <main className="grid min-h-screen place-items-center">We couldn&apos;t load your dashboard. Please try again.</main>;
  if (query.data.role !== "student") {
    return <main className="mx-auto max-w-3xl p-6"><Header user={null} /><section className="mt-12 rounded-3xl bg-surface p-8"><p className="font-display font-bold uppercase tracking-widest text-mint-600">Coming soon</p><h1 className="mt-2 font-display text-3xl font-bold">Your dashboard is being built.</h1><p className="mt-3 text-ink-soft">We&apos;re preparing a helpful space for you.</p></section></main>;
  }
  return <StudentDashboard dashboard={query.data} />;
}

function StudentDashboard({ dashboard }: { dashboard: StudentDashboardPayload }) {
  const assignment = dashboard.next_assignment;
  const revision = assignment
    ? dashboard.graded_submissions.find((submission) => submission.assignment === assignment.id && submission.revision_requested)
    : undefined;
  const maxMinutes = Math.max(...dashboard.weekly_effort.map((day) => day.minutes), 1);
  return (
    <main className="min-h-screen">
      <Header user={null} />
      <div className="mx-auto max-w-6xl space-y-6 p-6">
        <div className="flex flex-wrap items-end justify-between gap-4"><div><p className="font-display text-sm font-bold uppercase tracking-widest text-mint-600">Your learning space</p><h1 className="font-display text-4xl font-bold">Let&apos;s make progress today.</h1></div><p className="rounded-full bg-mint-100 px-4 py-2 font-bold text-mint-700">{dashboard.completed_assignments} / {dashboard.total_assignments} complete</p></div>
        <section className="rounded-3xl bg-peach-100 p-6"><p className="font-display text-sm font-bold uppercase tracking-widest text-peach-500">Do now</p>{assignment ? <><h2 className="mt-2 font-display text-2xl font-bold">{assignment.title}</h2><p className="mt-2 text-ink-soft">{assignment.material_title}</p><p className="mt-2 text-sm text-ink-soft">Due {formatDueDate(assignment.due_date)}</p>{revision && <p className="mt-3 rounded-xl bg-coral-100 p-3 text-coral-600">Teacher notes: {revision.revision_notes || revision.teacher_feedback || "Please look over the feedback and have another go."}</p>}<a className="mt-5 inline-block rounded-xl bg-mint-600 px-5 py-3 font-bold text-white" href={`/hub/assignment/${assignment.id}/`}>Start</a></> : <><h2 className="mt-2 font-display text-2xl font-bold">You&apos;re all caught up!</h2><p className="mt-2 text-ink-soft">Take a moment to celebrate your progress.</p></>}</section>
        <div className="grid gap-6 lg:grid-cols-2"><Panel title="Recently graded">{dashboard.graded_submissions.length ? dashboard.graded_submissions.map((submission) => <div className="flex items-start justify-between gap-4 border-b border-border py-3 last:border-0" key={submission.id}><div><p className="font-bold">{submission.assignment_title}</p>{submission.teacher_feedback && <p className="mt-1 text-sm italic text-ink-soft">&quot;{submission.teacher_feedback}&quot;</p>}</div><span className="rounded-full bg-mint-100 px-3 py-1 font-bold text-mint-700">{submission.grade || `${submission.numeric_score ?? 0}%`}</span></div>) : <EmptyState text="Your first marked assignment will appear here." />}</Panel><Panel title="Subject mastery">{dashboard.subject_mastery.length ? dashboard.subject_mastery.map((subject) => <div className="mb-4 last:mb-0" key={subject.name}><div className="mb-1 flex justify-between font-bold"><span>{subject.name}</span><span>{subject.percentage}%</span></div><div className="h-3 overflow-hidden rounded-full bg-mint-100"><span className="block h-full rounded-full" style={{ width: `${subject.percentage}%`, backgroundColor: subject.color }} /></div></div>) : <EmptyState text="Complete a lesson to see your strengths grow." />}</Panel></div>
        <Panel title="Weekly effort"><div className="flex h-44 items-end justify-between gap-3">{dashboard.weekly_effort.length ? dashboard.weekly_effort.map((day) => <div className="flex h-full flex-1 flex-col items-center justify-end gap-2" key={day.date}><span className="w-full max-w-10 rounded-t-xl bg-coral-500" style={{ height: `${Math.max((day.minutes / maxMinutes) * 100, 4)}%` }} /><small className="text-ink-soft">{new Date(day.date).toLocaleDateString("en-ZA", { weekday: "short" })}</small></div>) : <EmptyState text="Your weekly effort will appear here." />}</div></Panel>
      </div>
    </main>
  );
}

function Header({ user }: { user: User | null }) { return <header className="flex items-center justify-between border-b border-border bg-surface px-6 py-4"><Link to="/dashboard" className="font-display font-bold text-mint-600">PG Tutoring Hub</Link>{user && <span>{user.full_name || user.username}</span>}</header>; }
function Panel({ title, children }: { title: string; children: ReactNode }) { return <section className="rounded-3xl border border-border bg-surface p-6"><h2 className="mb-4 font-display text-xl font-bold">{title}</h2>{children}</section>; }
function EmptyState({ text }: { text: string }) { return <p className="text-ink-soft">{text}</p>; }
function LoadingState() { return <main className="grid min-h-screen place-items-center text-ink-soft" aria-label="Loading">Getting your learning space ready...</main>; }
function formatDueDate(value: string) { return new Date(value).toLocaleDateString("en-ZA", { day: "numeric", month: "short" }); }
