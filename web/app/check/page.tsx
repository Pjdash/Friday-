import type { Metadata } from "next";
import { Suspense } from "react";
import { EligibilityChecker } from "@/components/eligibility-checker";

export const metadata: Metadata = { title: "Check eligibility" };

export default function CheckPage() {
  // useSearchParams (for ?scheme=) needs a Suspense boundary so the rest of the page can prerender.
  return (
    <Suspense fallback={null}>
      <EligibilityChecker />
    </Suspense>
  );
}
