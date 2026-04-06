"use client";
import Image from "next/image";
import useSWR, { mutate } from "swr";
import { useState, FormEvent } from "react";
import { fetcher, postJson } from "@/lib/api";

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
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [seedDays, setSeedDays] = useState(7);
  const [vegDays, setVegDays] = useState(21);
  const [bloomDays, setBloomDays] = useState(28);

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

  // Normalize progress and icon by label; fallback to index.
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
    progress = Math.min(idx / 2, 1);
  }
  const percent = Math.round(progress * 100);

  async function handleHarvest(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      await postJson("/stage/reset", {});
      const typeRes = await postJson("/plant-types", {
        name: name || "New plant",
        stage_durations_days: [seedDays, vegDays, bloomDays],
        stage_colors: ["#4DA6FF", "#FFFFFF", "#FF6FA3"],
      });
      if (!typeRes.ok) throw new Error("Failed to save plant type");
      const type = await typeRes.json();
      const plantRes = await postJson("/plants/", { label: name || "New plant", plant_type_id: type.id });
      if (!plantRes.ok) throw new Error("Failed to create plant");

      mutate("/stage");
      mutate("/plants/");
      setMessage("Harvested and started new grow");
      setShowForm(false);
      setName("");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Could not harvest/start";
      setMessage(msg);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="status-frame h-full">
      <div className="status-card h-full" style={{ minHeight: "100px" }}>
        <div className="status-header">
          <span className="day-label">Day</span>
          <div className="status-divider" aria-hidden />
          <span className="status-eyebrow">Growth status</span>
          <Image src={icon} alt={stageName} width={88} height={88} className="status-icon" priority />
          <span className="day-number">{stage.days_in_stage}</span>
          <p className="status-title" style={{ marginTop: "-4px" }}>
            {stageName}
          </p>
        </div>

        <div className="status-progress mt-auto">
          <div className="status-steps">
            <span>Seed</span>
            <span>Veg</span>
            <span>Bloom</span>
          </div>
          <div className="status-bar">
            <div className="status-bar-fill" style={{ width: `${percent}%` }} />
          </div>
          <div className="status-meta mt-2">
            <span>
              {harvest.days_to_harvest} days to harvest · {projected}
            </span>
            {!showForm && (
              <button className="status-harvest-btn" onClick={() => setShowForm(true)}>
                Harvest
              </button>
            )}
          </div>
        </div>

        {showForm && (
          <form className="status-form" onSubmit={handleHarvest}>
            <div className="grid grid-cols-1 gap-2">
              <label className="field">
                <span>Next plant name</span>
                <input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g., Basil" />
              </label>
              <div className="grid grid-cols-3 gap-2">
                <label className="field">
                  <span>Seed days</span>
                  <input
                    type="number"
                    min={1}
                    value={seedDays}
                    onChange={(e) => setSeedDays(parseInt(e.target.value) || 1)}
                  />
                </label>
                <label className="field">
                  <span>Veg days</span>
                  <input
                    type="number"
                    min={1}
                    value={vegDays}
                    onChange={(e) => setVegDays(parseInt(e.target.value) || 1)}
                  />
                </label>
                <label className="field">
                  <span>Bloom days</span>
                  <input
                    type="number"
                    min={1}
                    value={bloomDays}
                    onChange={(e) => setBloomDays(parseInt(e.target.value) || 1)}
                  />
                </label>
              </div>
            </div>
            <div className="status-form-actions">
              <button type="submit" className="status-harvest-btn" disabled={saving}>
                {saving ? "Saving…" : "Harvest & start"}
              </button>
              <button type="button" className="status-secondary-btn" onClick={() => setShowForm(false)} disabled={saving}>
                Cancel
              </button>
            </div>
            {message && <p className="status-message">{message}</p>}
          </form>
        )}
      </div>
    </div>
  );
}
