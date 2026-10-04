import { zodResolver } from "@hookform/resolvers/zod";
import { useQuery } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { useMemo, useState } from "react";
import { Link, Navigate, Route, Routes, useNavigate, useParams } from "react-router-dom";
import type { FormEvent, ReactNode } from "react";
import { z } from "zod";

import { ApiClient, ApiError } from "./api";
import type { AssignmentDetail, Material, StudentDashboardPayload, User } from "./types";

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
      <Route path="/materials" element={<RequireAuth><MaterialsPage /></RequireAuth>} />
      <Route path="/materials/:id" element={<RequireAuth><MaterialDetailPage /></RequireAuth>} />
      <Route path="/assignments" element={<RequireAuth><AssignmentsPage /></RequireAuth>} />
      <Route path="/assignments/:id" element={<RequireAuth><AssignmentDetailPage /></RequireAuth>} />
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
  const userQuery = useQuery({
    queryKey: ["current-user"],
    queryFn: () => api.getCurrentUser(),
    retry: false,
  });
  const query = useQuery({ queryKey: ["dashboard"], queryFn: () => api.getDashboard() });
  if (query.isPending) return <LoadingState />;
  if (query.isError) return <main className="grid min-h-screen place-items-center">We couldn&apos;t load your dashboard. Please try again.</main>;
  if (query.data.role !== "student") {
    return <main className="mx-auto max-w-3xl p-6"><Header user={userQuery.data ?? null} /><section className="mt-12 rounded-3xl bg-surface p-8"><p className="font-display font-bold uppercase tracking-widest text-mint-600">Coming soon</p><h1 className="mt-2 font-display text-3xl font-bold">Your dashboard is being built.</h1><p className="mt-3 text-ink-soft">We&apos;re preparing a helpful space for you.</p></section></main>;
  }
  return <StudentDashboard dashboard={query.data} user={userQuery.data ?? null} />;
}

function StudentDashboard({ dashboard, user }: { dashboard: StudentDashboardPayload; user: User | null }) {
  const assignment = dashboard.next_assignment;
  const revision = assignment
    ? dashboard.graded_submissions.find((submission) => submission.assignment === assignment.id && submission.revision_requested)
    : undefined;
  const maxMinutes = Math.max(...dashboard.weekly_effort.map((day) => day.minutes), 1);
  return (
    <main className="min-h-screen">
      <Header user={user} />
      <div className="mx-auto max-w-6xl space-y-6 p-6">
        <div className="flex flex-wrap items-end justify-between gap-4"><div><p className="font-display text-sm font-bold uppercase tracking-widest text-mint-600">Your learning space</p><h1 className="font-display text-4xl font-bold">Let&apos;s make progress today.</h1></div><p className="rounded-full bg-mint-100 px-4 py-2 font-bold text-mint-700">{dashboard.completed_assignments} / {dashboard.total_assignments} complete</p></div>
        <section className="rounded-3xl bg-peach-100 p-6"><p className="font-display text-sm font-bold uppercase tracking-widest text-peach-500">Do now</p>{assignment ? <><h2 className="mt-2 font-display text-2xl font-bold">{assignment.title}</h2><p className="mt-2 text-ink-soft">{assignment.material_title}</p><p className="mt-2 text-sm text-ink-soft">Due {formatDueDate(assignment.due_date)}</p>{revision && <p className="mt-3 rounded-xl bg-coral-100 p-3 text-coral-600">Teacher notes: {revision.revision_notes || revision.teacher_feedback || "Please look over the feedback and have another go."}</p>}        <Link className="mt-5 inline-block rounded-xl bg-mint-600 px-5 py-3 font-bold text-white" to={`/assignments/${assignment.id}`}>Start</Link></> : <><h2 className="mt-2 font-display text-2xl font-bold">You&apos;re all caught up!</h2><p className="mt-2 text-ink-soft">Take a moment to celebrate your progress.</p></>}</section>
        <div className="grid gap-6 lg:grid-cols-2"><Panel title="Recently graded">{dashboard.graded_submissions.length ? dashboard.graded_submissions.map((submission) => <div className="flex items-start justify-between gap-4 border-b border-border py-3 last:border-0" key={submission.id}><div><p className="font-bold">{submission.assignment_title}</p>{submission.teacher_feedback && <p className="mt-1 text-sm italic text-ink-soft">&quot;{submission.teacher_feedback}&quot;</p>}</div><span className="rounded-full bg-mint-100 px-3 py-1 font-bold text-mint-700">{submission.grade || `${submission.numeric_score ?? 0}%`}</span></div>) : <EmptyState text="Your first marked assignment will appear here." />}</Panel><Panel title="Subject mastery">{dashboard.subject_mastery.length ? dashboard.subject_mastery.map((subject) => <div className="mb-4 last:mb-0" key={subject.name}><div className="mb-1 flex justify-between font-bold"><span>{subject.name}</span><span>{subject.percentage}%</span></div><div className="h-3 overflow-hidden rounded-full bg-mint-100"><span className="block h-full rounded-full" style={{ width: `${subject.percentage}%`, backgroundColor: subject.color }} /></div></div>) : <EmptyState text="Complete a lesson to see your strengths grow." />}</Panel></div>
        <Panel title="Weekly effort"><div className="flex h-44 items-end justify-between gap-3">{dashboard.weekly_effort.length ? dashboard.weekly_effort.map((day) => <div className="flex h-full flex-1 flex-col items-center justify-end gap-2" key={day.date}><span className="w-full max-w-10 rounded-t-xl bg-coral-500" style={{ height: `${Math.max((day.minutes / maxMinutes) * 100, 4)}%` }} /><small className="text-ink-soft">{new Date(day.date).toLocaleDateString("en-ZA", { weekday: "short" })}</small></div>) : <EmptyState text="Your weekly effort will appear here." />}</div></Panel>
      </div>
    </main>
  );
}

function AssignmentsPage() {
  const query = useQuery({ queryKey: ["assignments"], queryFn: () => api.getAssignments(), retry: false });
  if (query.isPending) return <LoadingState />;
  if (query.isError) return <EmptyState text="We couldn't load your assignments. Please try again." />;
  return <main className="min-h-screen"><Header user={null} /><div className="mx-auto max-w-6xl space-y-6 p-6">
    <p className="font-display text-sm font-bold uppercase tracking-widest text-mint-600">Your work</p>
    <h1 className="font-display text-4xl font-bold">Assignments</h1>
    {query.data.length === 0 ? <EmptyState text="No assignments yet." /> : <div className="grid gap-5 md:grid-cols-2">
      {query.data.map((assignment) => <Link key={assignment.id} to={`/assignments/${assignment.id}`} className="rounded-3xl border border-border bg-surface p-6 hover:shadow-lg">
        <p className="text-sm font-bold uppercase text-mint-600">{assignment.priority}</p><h2 className="mt-2 font-display text-xl font-bold">{assignment.title}</h2>
        <p className="mt-2 text-ink-soft">{assignment.description}</p><p className="mt-4 text-sm">Due {formatDueDate(assignment.due_date)}</p>
      </Link>)}</div>}
  </div></main>;
}

function AssignmentDetailPage() {
  const { id } = useParams();
  const assignmentId = Number(id);
  const query = useQuery({ queryKey: ["assignment", assignmentId], queryFn: () => api.getAssignment(assignmentId), enabled: Number.isInteger(assignmentId), retry: false });
  const [text, setText] = useState(""); const [notes, setNotes] = useState(""); const [file, setFile] = useState<File>(); const [message, setMessage] = useState(""); const [saving, setSaving] = useState(false);
  if (query.isPending) return <LoadingState />;
  if (query.isError || !query.data) return <EmptyState text="Assignment not found." />;
  const assignment: AssignmentDetail = query.data;
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSaving(true); setMessage("");
    try { await api.submitAssignment(assignment.id, { submissionText: text, submissionNotes: notes, file }); setMessage("Your work was submitted."); setText(""); setNotes(""); setFile(undefined); await query.refetch(); }
    catch (error) { setMessage(error instanceof ApiError ? error.message : "Could not submit your work."); } finally { setSaving(false); }
  }
  return <main className="min-h-screen"><Header user={null} /><div className="mx-auto max-w-3xl space-y-6 p-6"><Link to="/assignments" className="font-bold text-mint-600">← All assignments</Link>
    <article className="rounded-3xl bg-surface p-8"><p className="font-display text-sm font-bold uppercase text-mint-600">Assignment</p><h1 className="mt-2 font-display text-4xl font-bold">{assignment.title}</h1><p className="mt-4 text-ink-soft">{assignment.description}</p><p className="mt-3 text-sm">Due {formatDueDate(assignment.due_date)} · {assignment.max_score} points</p>
    {assignment.instructions && <div className="mt-6 rounded-xl bg-mint-100 p-4"><strong>Instructions</strong><p>{assignment.instructions}</p></div>}
    {assignment.submission && <div className="mt-6 rounded-xl bg-peach-100 p-4"><strong>Latest submission: {assignment.submission.status}</strong>{assignment.submission.grade && <p>Grade: {assignment.submission.grade} {assignment.submission.numeric_score != null && `(${assignment.submission.numeric_score}%)`}</p>}{assignment.submission.teacher_feedback && <p>{assignment.submission.teacher_feedback}</p>}{assignment.submission.revision_requested && <p className="mt-2 text-coral-600">{assignment.submission.revision_notes}</p>}</div>}
    <form onSubmit={submit} className="mt-6 grid gap-4"><h2 className="font-display text-2xl font-bold">{assignment.submission ? "Resubmit your work" : "Submit your work"}</h2>{message && <p role="status" className="rounded-xl bg-mint-100 p-3">{message}</p>}<label className="grid gap-1 font-bold">Your answer<textarea className="rounded-xl border border-border p-3" rows={6} value={text} onChange={(event) => setText(event.target.value)} /></label><label className="grid gap-1 font-bold">Notes<textarea className="rounded-xl border border-border p-3" rows={3} value={notes} onChange={(event) => setNotes(event.target.value)} /></label><label className="grid gap-1 font-bold">Attach a file<input type="file" onChange={(event) => setFile(event.target.files?.[0])} /></label><button className="rounded-xl bg-mint-600 px-5 py-3 font-bold text-white" disabled={saving}>{saving ? "Submitting..." : assignment.submission ? "Resubmit assignment" : "Submit assignment"}</button></form></article>
  </div></main>;
}

function MaterialsPage() {
  const [search, setSearch] = useState("");
  const query = useQuery({
    queryKey: ["materials"],
    queryFn: () => api.getMaterials(),
  });
  const materials = useMemo(() => {
    const value = search.trim().toLowerCase();
    if (!query.data || !value) return query.data?.results ?? [];
    return query.data.results.filter((material) =>
      [material.title, material.subject_name, material.tags]
        .join(" ")
        .toLowerCase()
        .includes(value),
    );
  }, [query.data, search]);

  return (
    <main className="min-h-screen">
      <Header user={null} />
      <div className="mx-auto max-w-6xl space-y-6 p-6">
        <div>
          <p className="font-display text-sm font-bold uppercase tracking-widest text-mint-600">Learning hub</p>
          <h1 className="font-display text-4xl font-bold">Find something to grow your skills.</h1>
          <p className="mt-2 text-ink-soft">Choose a material that feels like a good next step.</p>
        </div>
        <label className="block">
          <span className="mb-2 block font-bold">Search materials</span>
          <input
            className="w-full rounded-xl border border-border bg-surface px-4 py-3"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search by title, subject or tag"
          />
        </label>
        {query.isPending ? (
          <LoadingState />
        ) : query.isError ? (
          <EmptyState text="We couldn't load your learning materials. Please try again." />
        ) : materials.length === 0 ? (
          <EmptyState text="No learning materials yet. Check back soon." />
        ) : (
          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {materials.map((material) => <MaterialCard key={material.id} material={material} />)}
          </div>
        )}
      </div>
    </main>
  );
}

function MaterialCard({ material }: { material: Material }) {
  return (
    <Link
      to={`/materials/${material.id}`}
      className="rounded-3xl border border-border bg-surface p-6 transition hover:-translate-y-1 hover:shadow-lg hover:shadow-mint-700/10"
    >
      <p className="text-sm font-bold uppercase tracking-wide text-mint-600">{material.subject_name}</p>
      <h2 className="mt-2 font-display text-xl font-bold">{material.title}</h2>
      <p className="mt-2 line-clamp-2 text-ink-soft">{material.description}</p>
      <div className="mt-5 flex flex-wrap gap-2 text-sm text-ink-soft">
        <span className="rounded-full bg-mint-100 px-3 py-1">{material.difficulty_level}</span>
        <span className="rounded-full bg-peach-100 px-3 py-1">Grade {material.grade_level}</span>
        {material.estimated_time > 0 && <span className="rounded-full bg-coral-100 px-3 py-1">{material.estimated_time} min</span>}
      </div>
    </Link>
  );
}

function MaterialDetailPage() {
  const { id } = useParams();
  const materialId = Number(id);
  const validId = Number.isInteger(materialId) && materialId > 0;
  const query = useQuery({
    queryKey: ["material", materialId],
    queryFn: () => api.getMaterial(materialId),
    enabled: validId,
    retry: false,
  });

  if (!validId || query.isError) {
    return <NotFoundMaterial />;
  }
  if (query.isPending) return <LoadingState />;
  const material = query.data;
  return (
    <main className="min-h-screen">
      <Header user={null} />
      <article className="mx-auto max-w-3xl space-y-6 p-6">
        <Link to="/materials" className="font-bold text-mint-600">← Back to materials</Link>
        <section className="rounded-3xl border border-border bg-surface p-8">
          <p className="font-display text-sm font-bold uppercase tracking-widest text-mint-600">{material.subject_name}</p>
          <h1 className="mt-2 font-display text-4xl font-bold">{material.title}</h1>
          <div className="mt-4 flex flex-wrap gap-2 text-sm text-ink-soft">
            <span className="rounded-full bg-mint-100 px-3 py-1">{material.difficulty_level}</span>
            <span className="rounded-full bg-peach-100 px-3 py-1">Grade {material.grade_level}</span>
            {material.estimated_time > 0 && <span className="rounded-full bg-coral-100 px-3 py-1">{material.estimated_time} min</span>}
          </div>
          <p className="mt-8 whitespace-pre-wrap text-lg leading-8 text-ink-soft">{material.description}</p>
          <div className="mt-8 flex flex-wrap gap-3">
            {material.file_url && <a className="rounded-xl bg-mint-600 px-5 py-3 font-bold text-white" href={material.file_url} target="_blank" rel="noopener noreferrer">Open worksheet</a>}
            {material.external_link && <a className="rounded-xl border border-mint-600 px-5 py-3 font-bold text-mint-700" href={material.external_link} target="_blank" rel="noopener noreferrer">Open link</a>}
          </div>
          {!material.file_url && !material.external_link && <p className="mt-6 rounded-xl bg-peach-100 p-4 text-ink-soft">Your teacher will add the file soon. You can come back and try it then.</p>}
        </section>
      </article>
    </main>
  );
}

function NotFoundMaterial() {
  return <main className="grid min-h-screen place-items-center p-6"><section className="text-center"><h1 className="font-display text-3xl font-bold">We couldn&apos;t find that material.</h1><Link to="/materials" className="mt-4 inline-block font-bold text-mint-600">Back to materials</Link></section></main>;
}

function Header({ user }: { user: User | null }) { return <header className="flex flex-wrap items-center justify-between gap-4 border-b border-border bg-surface px-6 py-4"><Link to="/dashboard" className="font-display font-bold text-mint-600">PG Tutoring Hub</Link><nav className="flex items-center gap-4 font-bold"><Link to="/dashboard" className="hover:text-mint-600">Dashboard</Link><Link to="/assignments" className="hover:text-mint-600">Assignments</Link><Link to="/materials" className="hover:text-mint-600">Materials</Link>{user && <span className="text-ink-soft">{user.full_name || user.username}</span>}</nav></header>; }
function Panel({ title, children }: { title: string; children: ReactNode }) { return <section className="rounded-3xl border border-border bg-surface p-6"><h2 className="mb-4 font-display text-xl font-bold">{title}</h2>{children}</section>; }
function EmptyState({ text }: { text: string }) { return <p className="text-ink-soft">{text}</p>; }
function LoadingState() { return <main className="grid min-h-screen place-items-center text-ink-soft" aria-label="Loading">Getting your learning space ready...</main>; }
function formatDueDate(value: string) { return new Date(value).toLocaleDateString("en-ZA", { day: "numeric", month: "short" }); }
