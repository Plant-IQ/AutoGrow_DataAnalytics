"use client";
import useSWR from "swr";
import { fetcher } from "@/lib/api";
import Image from "next/image";

type ActivePlant = { id: number };
type HistoryPoint = {
  ts: string;
  temp: number;
  humidity: number;
};
type HistoryResponse = {
  points: HistoryPoint[];
};

export default function TempHumidityCard() {
  const { data: activePlant, isLoading: loadingActive } = useSWR<ActivePlant | null>("/plants/active", fetcher);
  const { data, isLoading, error } = useSWR<HistoryResponse>("/history", fetcher, {
    refreshInterval: 30000,
  });

  if (loadingActive || isLoading) return <div className="card">Loading climate sensors…</div>;
  if (!activePlant) return <div className="card">Temperature and humidity appear after a plant starts.</div>;
  if (error || !data) return <div className="card text-red-600">Climate data unavailable</div>;

  const latest = data.points[data.points.length - 1];
  const tempLabel = latest?.temp !== undefined ? `${latest.temp.toFixed(1)}°C` : "N/A";
  const humidityLabel = latest?.humidity !== undefined ? `${latest.humidity.toFixed(0)}% RH` : "N/A";

  return (
    <div className="card relative space-y-2">
      <p className="label">
        <span className="block">Glasshouse Temp & Humidity</span>
      </p>
      <div className="grid grid-cols-1 gap-2 text-sm">
        <div className="relative rounded-lg bg-[#FFF0BE]/70 px-3 py-5">
          <p className="text-xs uppercase tracking-wide text-slate-500">Temperature</p>
          <p className="text-xl font-semibold text-slate-900 pt-1">{tempLabel}</p>
          <Image
            src="/assets/icons/termometer.png"
            alt="Thermometer"
            width={18}
            height={18}
            className="absolute right-6 top-1/2 -translate-y-1/2 object-contain rotate-[27deg]"
          />
        </div>
        <div className="relative rounded-lg bg-[#E2EFF6] px-3 py-5">
          <Image
            src="/assets/icons/water_drops.png"
            alt="Vapor"
            width={55}
            height={55}
            className="absolute left-3 top-1/2 -translate-y-1/2 object-contain"
          />
          <p className="text-right text-xs uppercase tracking-wide text-slate-500 pr-1">Humidity</p>
          <p className="text-right text-xl font-semibold text-slate-900 pt-1 pr-1">{humidityLabel}</p>
        </div>
      </div>
      <p className="absolute bottom-4 right-4 text-xs text-slate-500">collected via KY-015 (DHT11 x2 avg)</p>
    </div>
  );
}
