"use client";
import { FormEvent, useState } from "react";
import useSWR from "swr";
import { postJson } from "@/lib/api";
import { fetcher } from "@/lib/api";

const initial = {
  height_cm: 8,
  leaf_count: 6,
  root_visible: false,
  canopy_score: 3,
};

type ActivePlant = {
  id: number;
  label: string;
  session_code: string;
};

type ObservationProfile = {
  title: string;
  subtitle: string;
  heightLabel: string;
  leafLabel: string;
  canopyLabel: string;
  rootLabel: string;
  heightHint: string;
  leafHint: string;
};

function getProfile(plantName?: string): ObservationProfile {
  const name = (plantName ?? "").toLowerCase();
  const microgreens = ["sprout", "microgreen", "sunflower", "pea shoots", "radish", "broccoli", "mustard"];
  const fruiting = ["tomato", "pepper", "chili", "cucumber", "zucchini", "strawberry", "eggplant", "bean"];

  if (microgreens.some((k) => name.includes(k))) {
    return {
      title: "Sprout / microgreen observation",
      subtitle: "Quick visual quality check for tray crops.",
      heightLabel: "Shoot height (cm)",
      leafLabel: "Density score (0-10)",
      canopyLabel: "Color / vigor score (1-5)",
      rootLabel: "Roots visible at tray bottom",
      heightHint: "Typical range: 2-12 cm",
      leafHint: "0 sparse, 10 very dense",
    };
  }

  if (fruiting.some((k) => name.includes(k))) {
    return {
      title: "Fruiting crop observation",
      subtitle: "Track structure and fruit/flower progress.",
      heightLabel: "Plant height (cm)",
      leafLabel: "Flower / fruit count",
      canopyLabel: "Canopy health score (1-5)",
      rootLabel: "Roots visible",
      heightHint: "Measure from base to top canopy",
      leafHint: "Count visible flowers + fruits",
    };
  }

  return {
    title: "Leafy / herb observation",
    subtitle: "Track growth and canopy quality.",
    heightLabel: "Plant height (cm)",
    leafLabel: "Leaf count",
    canopyLabel: "Canopy score (1-5)",
    rootLabel: "Roots visible",
    heightHint: "Measure tallest point",
    leafHint: "Count mature leaves",
  };
}

export default function ObsForm() {
  const [values, setValues] = useState(initial);
  const [status, setStatus] = useState<"idle" | "saving" | "done" | "error">("idle");
  const [message, setMessage] = useState<string>("");
  const { data: activePlant, isLoading: loadingPlant } = useSWR<ActivePlant | null>("/plants/active", fetcher, {
    refreshInterval: 30000,
  });
  const profile = getProfile(activePlant?.label);
  const rootHint = profile.rootLabel.includes("tray")
    ? "Tick when roots show through tray holes."
    : "Check when roots are visible at the base or reservoir.";

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!activePlant) {
      setStatus("error");
      setMessage("Start a plant before logging observations.");
      return;
    }
    setStatus("saving");
    setMessage("");

    try {
      const res = await postJson("/observations", values);

      if (!res.ok) throw new Error(await res.text());

      setStatus("done");
      setMessage("Saved");
      setValues(initial);
    } catch {
      setStatus("error");
      setMessage("Could not save observation");
    }
  }

  function handleChange(field: string, value: number | boolean) {
    setValues((prev) => ({ ...prev, [field]: value }));
  }

  return (
    <form className="card gap-3" onSubmit={handleSubmit}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="label">Add observation</p>
          <p className="text-xs text-slate-500">{profile.title}</p>
          <p className="text-xs text-slate-400">{profile.subtitle}</p>
        </div>
        {activePlant && (
          <div className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs text-slate-600">
            Session {activePlant.session_code}
          </div>
        )}
      </div>
      {!loadingPlant && !activePlant && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
          No active plant. Start a plant first, then add observations.
        </div>
      )}
      <div className="grid grid-cols-2 gap-3">
        <label className="field">
          <span>{profile.heightLabel}</span>
          <input
            type="number"
            step="0.1"
            value={values.height_cm}
            onChange={(e) => handleChange("height_cm", parseFloat(e.target.value) || 0)}
            placeholder={profile.heightHint}
            disabled={!activePlant || status === "saving"}
          />
          <span className="text-xs text-slate-500">{profile.heightHint}</span>
        </label>
        <label className="field">
          <span>{profile.leafLabel}</span>
          <input
            type="number"
            value={values.leaf_count}
            onChange={(e) => handleChange("leaf_count", parseInt(e.target.value, 10) || 0)}
            disabled={!activePlant || status === "saving"}
          />
          <span className="text-xs text-slate-500">{profile.leafHint}</span>
        </label>
        <label className="field">
          <span>{profile.canopyLabel}</span>
          <input
            type="number"
            min={1}
            max={5}
            value={values.canopy_score}
            onChange={(e) => handleChange("canopy_score", parseInt(e.target.value, 10) || 1)}
            disabled={!activePlant || status === "saving"}
          />
        </label>
        <div className="col-span-2">
          <label className="checkbox-tile">
            <input
              type="checkbox"
              className="checkbox-tile-input"
              checked={values.root_visible}
              onChange={(e) => handleChange("root_visible", e.target.checked)}
              disabled={!activePlant || status === "saving"}
            />
            <div>
              <span className="checkbox-title">{profile.rootLabel}</span>
              <p className="text-xs text-slate-500">{rootHint}</p>
            </div>
          </label>
        </div>
      </div>
      <button
        type="submit"
        className="observation-btn"
        disabled={status === "saving" || !activePlant}
      >
        {status === "saving" ? "Saving…" : "Save observation"}
      </button>
      {message && (
        <p className={`text-sm ${status === "error" ? "text-red-600" : "text-emerald-600"}`}>{message}</p>
      )}
    </form>
  );
}
