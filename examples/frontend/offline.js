import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "./supabaseClient";
import * as SQLite from "expo-sqlite";

// Basic pattern: fetch from Supabase, cache locally
const useFetchData = () => {
  const queryClient = useQueryClient();

  return useQuery({
    queryKey: ["data"],
    queryFn: async () => {
      // Try Supabase first
      const { data, error } = await supabase.from("your_table").select("*");

      if (error && !navigator.onLine) {
        // Fall back to local SQLite on error if offline
        return fetchFromLocalDB();
      }

      // Update local SQLite with fresh data
      if (data) {
        await saveToLocalDB(data);
      }

      return data;
    },
    retry: true,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
};

// Mutations with optimistic updates
const useUpdateData = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (newData) => {
      const { data, error } = await supabase
        .from("your_table")
        .update(newData)
        .eq("id", newData.id);

      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["data"] });
    },
  });
};
