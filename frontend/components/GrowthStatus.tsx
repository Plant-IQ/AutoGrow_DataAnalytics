"use client";
import Image from "next/image";
import useSWR from "swr";
import { fetcher } from "@/lib/api";

type StageResponse = {
  stage: number;
  label: string;
  days_in_stage: number;
};

type HarvestResponse = {
  days_to_harvest: number;
  projected_date: string;
};

const STAGE_LABELS = ["Seed", "Veg", "Bloom"];
const ICONS = [
  "/assets/icons/state_seed.png",
  "/assets/icons/state_veg.png",
  "/assets/icons/state_bloom.png",
];

export default function GrowthStatus() {
  const { data: stage, isLoading: stageLoading, error: stageError } = useSWR<StageResponse>("/stage", fetcher, {
    refreshInterval: 30000,
  });
  const { data: harvest, isLoading: harvestLoading, error: harvestError } = useSWR<HarvestResponse>(
    "/harvest-eta",
    fetcher,
    { refreshInterval: 60000 },
  );

  if (stageLoading || harvestLoading) return <div className="card">Loading growth status…</div>;
  if (stageError || harvestError || !stage || !harvest)
    return <div className="card text-red-600">Growth status unavailable</div>;

  const idx = Math.min(Math.max(stage.stage, 0), 2);
  let icon = ICONS[idx] ?? ICONS[2];
  const stageName = stage.label || STAGE_LABELS[idx] || "Stage";

  const projected = new Date(harvest.projected_date).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });

  // Normalize progress: prefer label mapping, fallback to index.
  const labelLower = stageName.toLowerCase();
  let progress = 0; // 0=seed, 0.5=veg, 1=bloom
  if (labelLower.includes("seed") || labelLower.includes("germ")) {
    icon = ICONS[0];
    progress = 0;
  } else if (labelLower.includes("veg")) {
    icon = ICONS[1];
    progress = 0.5;
  } else if (labelLower.includes("bloom") || labelLower.includes("flower") || labelLower.includes("fruit")) {
    icon = ICONS[2];
    progress = 1;
  } else {
    // fallback to index position
    progress = Math.min(idx / 2, 1);
  }
  const percent = Math.round(progress * 100);


  return (
    <div className="card">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="label">Growth status</p>
          <p className="text-3xl font-semibold">{stageName}</p>
          <p className="text-sm text-slate-500">Day {stage.days_in_stage}</p>
        </div>
        <Image src={icon} alt={stageName} width={56} height={56} className="w-14 h-auto object-contain" priority />
      </div>

      <div className="mt-4 space-y-2">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
          <span>Seed</span>
          <span>Veg</span>
          <span>Bloom</span>
        </div>
        <div className="relative h-4 rounded-full bg-slate-200">
          <div
            className="absolute inset-y-0 left-0 rounded-full"
            style={{
              width: `${percent}%`,
              background: "linear-gradient(90deg, var(--brand-primary), var(--brand-secondary))",
            }}
          />
        </div>
        <div className="flex items-center justify-end text-sm text-slate-600">
          <span>
            {harvest.days_to_harvest} days to harvest · {projected}
          </span>
        </div>
      </div>
    </div>
  );
}
