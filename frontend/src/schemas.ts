import { z } from "zod";

export const userSchema = z.object({
  id: z.number(),
  username: z.string(),
  email: z.string().email(),
  first_name: z.string(),
  last_name: z.string(),
  user_type: z.enum(["student", "teacher", "parent"]),
  full_name: z.string(),
});

export const materialSchema = z.object({
  id: z.number(),
  title: z.string(),
  description: z.string(),
  material_type: z.string(),
  subject: z.number(),
  subject_name: z.string(),
  difficulty_level: z.string(),
  grade_level: z.string(),
  estimated_time: z.number(),
  tags: z.string(),
  external_link: z.string(),
  file_url: z.string().nullable(),
  created_at: z.string(),
});

export const assignmentSchema = z.object({
  id: z.number(),
  title: z.string(),
  description: z.string(),
  material: z.number(),
  material_title: z.string(),
  assigned_to: z.array(z.number()),
  due_date: z.string(),
  priority: z.string(),
  max_score: z.number(),
  instructions: z.string(),
  submission_format: z.string(),
  is_active: z.boolean(),
});

export const submissionSchema = z.object({
  id: z.number(),
  assignment: z.number(),
  assignment_title: z.string(),
  status: z.string(),
  grade: z.string(),
  numeric_score: z.number().nullable(),
  teacher_feedback: z.string(),
  submitted_at: z.string(),
  graded_at: z.string().nullable(),
  revision_requested: z.boolean(),
  revision_notes: z.string(),
});

export const subjectMasterySchema = z.object({
  name: z.string(),
  color: z.string(),
  total: z.number(),
  points: z.number(),
  percentage: z.number(),
});

export const weeklyEffortSchema = z.object({
  date: z.string(),
  minutes: z.number(),
});

export const studentDashboardSchema = z.object({
  role: z.literal("student"),
  total_assignments: z.number(),
  completed_assignments: z.number(),
  completion_rate: z.number(),
  next_assignment: assignmentSchema.nullable(),
  graded_submissions: z.array(submissionSchema),
  subject_mastery: z.array(subjectMasterySchema),
  weekly_effort: z.array(weeklyEffortSchema),
});

export const teacherDashboardSchema = z.object({
  role: z.literal("teacher"),
  total_students: z.number(),
  total_materials: z.number(),
  total_assignments: z.number(),
});

export const parentDashboardSchema = z.object({
  role: z.literal("parent"),
  children: z.array(userSchema),
  total_assignments: z.number(),
  completed_assignments: z.number(),
  completion_rate: z.number(),
});

export const dashboardSchema = z.discriminatedUnion("role", [
  studentDashboardSchema,
  teacherDashboardSchema,
  parentDashboardSchema,
]);

export const chatMessageSchema = z.object({
  id: z.number(),
  room: z.number(),
  sender: z.number(),
  sender_username: z.string(),
  message_type: z.string(),
  content: z.string(),
  file: z.string().nullable(),
  timestamp: z.string(),
  is_read: z.boolean(),
});

export const chatRoomSchema = z.object({
  id: z.number(),
  name: z.string(),
  participants: z.array(z.number()),
  is_group_chat: z.boolean(),
  created_by: z.number(),
  created_at: z.string(),
  latest_message: chatMessageSchema.nullable(),
});

export const progressRecordSchema = z.object({
  id: z.number(),
  material: z.number(),
  material_title: z.string(),
  assignment: z.number().nullable(),
  status: z.string(),
  score: z.number().nullable(),
  completion_percentage: z.number(),
  time_spent_minutes: z.number(),
  started_at: z.string().nullable(),
  completed_at: z.string().nullable(),
  teacher_feedback: z.string(),
});

export const progressSummarySchema = z.object({
  records: z.array(progressRecordSchema),
  total_count: z.number(),
  completed_count: z.number(),
  in_progress_count: z.number(),
  overall_completion: z.number(),
  average_score: z.number(),
  best_score: z.number().nullable(),
  total_study_time: z.number(),
});
