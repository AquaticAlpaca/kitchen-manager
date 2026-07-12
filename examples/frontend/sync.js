import { useQueryClient } from "@tanstack/react-query";
import { supabase } from "./supabaseClient";

// Sync using supabase when the network returns
useEffect(() => {
  const queryClient = useQueryClient();

  const subscription = supabase
    .on(
      "postgres_changes",
      { event: "*", schema: "public", table: "your_table" },
      (payload) => {
        // Update local cache and SQLite
        queryClient.invalidateQueries({ queryKey: ["data"] });
      },
    )
    .subscribe();

  return () => subscription.unsubscribe();
}, []);
