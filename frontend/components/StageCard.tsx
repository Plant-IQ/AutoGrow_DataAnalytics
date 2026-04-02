"use client";
import Image from "next/image";
import useSWR from "swr";
import { fetcher } from "@/lib/api";

type StageResponse = {
  stage: number;
  label: string;
  days_in_stage: number;
};

export default function StageCard() {
  const { data, isLoading, error } = useSWR<StageResponse>("/stage", fetcher, {
    refreshInterval: 30000,
  });

  if (isLoading) return <div className="card">Loading stage…</div>;
  if (error) return <div className="card text-red-600">Failed to load stage</div>;

  const stageIdx = data?.stage ?? 0;
  const label = (data?.label ?? "").toLowerCase();

  let stageIcon = "/assets/icons/state_bloom.png";
  if (label.includes("seed") || label.includes("germ")) {
    stageIcon = "/assets/icons/state_seed.png";
  } else if (label.includes("veg")) {
    stageIcon = "/assets/icons/state_veg.png";
  } else if (label.includes("bloom") || label.includes("flower") || label.includes("fruit")) {
    stageIcon = "/assets/icons/state_bloom.png";
  } else {
    // fallback on index when labels are unknown
    if (stageIdx <= 0) stageIcon = "/assets/icons/state_seed.png";
    else if (stageIdx === 1 || stageIdx === 2) stageIcon = "/assets/icons/state_veg.png";
    else stageIcon = "/assets/icons/state_bloom.png";
  }

  return (
    <div className="card relative overflow-hidden">
      <p className="label">Current stage</p>
      <div className="flex items-center justify-between gap-4">
        <div className="flex flex-col">
          <div className="flex items-baseline gap-2">
            <p className="text-3xl font-semibold">{data?.label ?? "–"}</p>
            <span className="rounded-full bg-[color:var(--brand-secondary)]/15 px-2 py-1 text-xs font-medium text-[color:var(--brand-secondary)]">
              #{data?.stage}
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-500">Day {data?.days_in_stage}</p>
        </div>
      </div>
      <Image
        src={stageIcon}
        alt={`Stage icon ${stageIdx}`}
        width={64}
        height={64}
        className="pointer-events-none absolute bottom-3 right-3 h-19 w-19 object-contain opacity-90"
        priority
      />
    </div>
  );
}
