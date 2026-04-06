"use client";
import useSWR from "swr";
import { fetcher, postJson } from "@/lib/api";

type PlantInstance = {
  id: number;
  label: string;
  plant_type_id: number;
  current_stage_index: number;
  stage_started_at: string;
  pending_confirm: boolean;
};

type PlantLight = {
  plant_id: number;
  stage: number;
  color: string;
  pending_confirm: boolean;
};

export default function PlantLight() {
  const { data: plants, isLoading: loadingPlants, error: plantsError } = useSWR<PlantInstance[]>("/plants/", fetcher, {
    refreshInterval: 60000,
  });

  const activePlant = plants?.[0];

  const {
    data: light,
    isLoading: loadingLight,
    mutate,
    error: lightError,
  } = useSWR<PlantLight>(activePlant ? `/plants/${activePlant.id}/light` : null, fetcher, { refreshInterval: 30000 });

  const isLoading = loadingPlants || loadingLight;
  const hasError = plantsError || lightError;

  // Force a consistent palette: Seed → Blue, Veg → Warm White, Bloom → Red
  const palette = ["#6fb2d2", "#F5E6C5", "#cb6a7e"];
  const tone = light ? palette[Math.min(light.stage, palette.length - 1)] ?? light.color : palette[0];
  const toneLabel = light?.stage === 0 ? "Blue" : light?.stage === 1 ? "Warm white" : "Red";

  async function handleConfirm() {
    if (!activePlant) return;
    await postJson(`/plants/${activePlant.id}/confirm-transition`, {});
    mutate();
  }

  if (hasError) return <div className="card text-red-600">Light status unavailable</div>;
  if (isLoading) return <div className="card">Loading light status…</div>;
  if (!activePlant) return <div className="card">No plants defined yet.</div>;
  if (!light) return <div className="card text-red-600">Light data missing</div>;

  return (
    <div className="card relative">
      <span
        className="h-14 w-14 rounded-full border-2 border-black shadow-inner absolute right-3 top-3"
        style={{ background: tone }}
      />

      <div className="mb-1">
        <p className="label">Light Status</p>
      </div>

      <div className="space-y-0.5">
        <p className="text-sm text-slate-500 leading-tight">Color</p>
        <p className="text-2xl font-semibold leading-tight">{toneLabel}</p>
      </div>

      {light.pending_confirm ? (
        <div className="mt-2 flex items-center justify-between gap-3 rounded-lg bg-amber-50 px-3 py-2 text-amber-800">
          <div>
            <p className="text-sm font-medium">Change pending</p>
            <p className="text-xs">Confirm to apply the next light color.</p>
          </div>
          <button className="btn !px-3 !py-2 !text-sm" onClick={handleConfirm}>
            Confirm
          </button>
        </div>
      ) : (
        <p className="text-sm text-emerald-700">Synced · no confirmation needed</p>
      )}
    </div>
  );
}
