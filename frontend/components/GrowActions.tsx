"use client";
import { FormEvent, useState } from "react";
import useSWR, { mutate } from "swr";
import { fetcher, postJson } from "@/lib/api";

type PlantInstance = {
  id: number;
  label: string;
  plant_type_id: number;
  current_stage_index: number;
  stage_started_at: string;
  pending_confirm: boolean;
};

type StageResponse = {
  stage: number;
  label: string;
  days_in_stage: number;
};

export default function GrowActions() {
  const [name, setName] = useState("");
  const [seedDays, setSeedDays] = useState(7);
  const [vegDays, setVegDays] = useState(21);
  const [bloomDays, setBloomDays] = useState(28);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const { data: plants } = useSWR<PlantInstance[]>("/plants/", fetcher);
  const activePlant = plants?.[0];

  async function handleStart(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      // Create a plant type with the provided durations and palette
      const typeRes = await postJson("/plant-types", {
        name: name || "Custom",
        stage_durations_days: [seedDays, vegDays, bloomDays],
        stage_colors: ["#4DA6FF", "#FFFFFF", "#FF6FA3"],
      });
      if (!typeRes.ok) throw new Error("Failed to create plant type");
      const type = await typeRes.json();

      // Create a plant instance for that type
      const plantRes = await postJson("/plants/", {
        label: name || "New plant",
        plant_type_id: type.id,
      });
      if (!plantRes.ok) throw new Error("Failed to create plant");

      // Reset stage to seed
      await postJson("/stage/reset", {});

      mutate("/plants/");
      mutate("/stage");
      setMessage("Grow plan started");
      setName("");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Could not start grow";
      setMessage(msg);
    } finally {
      setSaving(false);
    }
  }

  async function handleReset() {
    setSaving(true);
    setMessage(null);
    try {
      await postJson("/stage/reset", {});
      mutate("/stage");
      setMessage("Cycle reset to seed");
    } catch (err: unknown) {
      setMessage("Could not reset cycle");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="card grid gap-4 md:grid-cols-2">
      <form className="space-y-3" onSubmit={handleStart}>
        <p className="label">Start a new grow</p>
        <div className="grid grid-cols-1 gap-2">
          <label className="field">
            <span>Plant name</span>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g., Basil" />
          </label>
          <div className="grid grid-cols-3 gap-2">
            <label className="field">
              <span>Seed days</span>
              <input type="number" min={1} value={seedDays} onChange={(e) => setSeedDays(parseInt(e.target.value) || 1)} />
            </label>
            <label className="field">
              <span>Veg days</span>
              <input type="number" min={1} value={vegDays} onChange={(e) => setVegDays(parseInt(e.target.value) || 1)} />
            </label>
            <label className="field">
              <span>Bloom days</span>
              <input type="number" min={1} value={bloomDays} onChange={(e) => setBloomDays(parseInt(e.target.value) || 1)} />
            </label>
          </div>
        </div>
        <button type="submit" className="btn" disabled={saving}>
          {saving ? "Saving…" : "Save & start"}
        </button>
        {message && <p className="text-sm text-slate-600">{message}</p>}
      </form>

      <div className="space-y-3">
        <p className="label">Harvest / reset</p>
        <p className="text-sm text-slate-600">
          When you harvest a batch (e.g., microgreens), click reset to move the cycle back to seed and restart tracking.
        </p>
        <button type="button" className="btn" onClick={handleReset} disabled={saving}>
          Reset cycle to Seed
        </button>
        {activePlant && (
          <p className="text-xs text-slate-500">
            Active plant: {activePlant.label} (type {activePlant.plant_type_id})
          </p>
        )}
        {message && <p className="text-sm text-slate-600">{message}</p>}
      </div>
    </div>
  );
}
