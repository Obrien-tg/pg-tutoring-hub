export type UserRole = "student" | "teacher" | "parent";

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  user_type: UserRole;
  full_name: string;
}

export interface Material {
  id: number;
  title: string;
  description: string;
  material_type: string;
  subject: number;
  subject_name: string;
  difficulty_level: string;
  grade_level: string;
  estimated_time: number;
  tags: string;
  external_link: string;
  file_url: string | null;
  created_at: string;
}

export interface Assignment {
  id: number;
  title: string;
  description: string;
  material: number;
  material_title: string;
  assigned_to: number[];
  due_date: string;
  priority: string;
  max_score: number;
  instructions: string;
  submission_format: string;
  is_active: boolean;
}

export interface Submission {
  id: number;
  assignment: number;
  assignment_title: string;
  status: string;
  grade: string;
  numeric_score: number | null;
  teacher_feedback: string;
  submitted_at: string;
  graded_at: string | null;
  revision_requested: boolean;
  revision_notes: string;
}

export interface SubjectMastery {
  name: string;
  color: string;
  total: number;
  points: number;
  percentage: number;
}

export interface WeeklyEffort {
  date: string;
  minutes: number;
}

export interface StudentDashboardPayload {
  role: "student";
  total_assignments: number;
  completed_assignments: number;
  completion_rate: number;
  next_assignment: Assignment | null;
  graded_submissions: Submission[];
  subject_mastery: SubjectMastery[];
  weekly_effort: WeeklyEffort[];
}

export interface TeacherDashboardPayload {
  role: "teacher";
  total_students: number;
  total_materials: number;
  total_assignments: number;
}

export interface ParentDashboardPayload {
  role: "parent";
  children: User[];
  total_assignments: number;
  completed_assignments: number;
  completion_rate: number;
}

export type DashboardPayload =
  | StudentDashboardPayload
  | TeacherDashboardPayload
  | ParentDashboardPayload;

export interface ChatMessage {
  id: number;
  room: number;
  sender: number;
  sender_username: string;
  message_type: string;
  content: string;
  file: string | null;
  timestamp: string;
  is_read: boolean;
}

export interface ChatRoom {
  id: number;
  name: string;
  participants: number[];
  is_group_chat: boolean;
  created_by: number;
  created_at: string;
  latest_message: ChatMessage | null;
}

export interface ProgressRecord {
  id: number;
  material: number;
  material_title: string;
  assignment: number | null;
  status: string;
  score: number | null;
  completion_percentage: number;
  time_spent_minutes: number;
  started_at: string | null;
  completed_at: string | null;
  teacher_feedback: string;
}

export interface ProgressSummary {
  records: ProgressRecord[];
  total_count: number;
  completed_count: number;
  in_progress_count: number;
  overall_completion: number;
  average_score: number;
  best_score: number | null;
  total_study_time: number;
}
