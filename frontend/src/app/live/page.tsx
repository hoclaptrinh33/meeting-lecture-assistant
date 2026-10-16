"use client";

import { useRouter } from "next/navigation";
import { LiveTranscript } from "@/components/live-transcript";

export default function LivePage() {
  const router = useRouter();

  return (
    <div className="py-6 space-y-6">
      <LiveTranscript
        onSessionFinalized={(jobId) => {
          router.push(`/jobs/${jobId}`);
        }}
      />
    </div>
  );
}
