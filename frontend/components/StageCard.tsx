"use client";
import useSWR from "swr";
import { fetcher } from "@/lib/api";

export default function StageCard() {
  const { data, isLoading } = useSWR("/stage", fetcher, {
    refreshInterval: 30000,
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="rounded-xl border p-4">
      <p className="text-sm text-gray-500">Current stage</p>
      <p className="text-2xl font-medium">{data?.name}</p>
      <p className="text-sm text-gray-400">Day {data?.day_elapsed}</p>
    </div>
  );
}