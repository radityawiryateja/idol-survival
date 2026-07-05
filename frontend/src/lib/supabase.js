import { createClient } from '@supabase/supabase-js'

// Uses the public anon key only — safe to expose in the frontend.
// Any table you query directly from here should have Row Level Security
// policies scoping rows to the authenticated user.
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
